import frappe
import requests
import json
import re

# def call_llm_api(prompt: str):
#     url = "https://api.groq.com/openai/v1/chat/completions"
#     api_key = frappe.conf.get("groq_api_key")

#     if not api_key:
#         frappe.throw("Groq API key missing in site_config.json")

#     headers = {
#         "Content-Type": "application/json",
#         "Authorization": f"Bearer {api_key}",
#     }

#     payload = {
#         "model": "llama-3.1-8b-instant",
#         "messages" : [{"role": "user", "content": prompt}]
#     }

#     res = requests.post(url, headers=headers, json=payload)
#     print(res)
#     if res.status_code != 200:
#         frappe.throw(f"LLM API Error: {res.text}")

#     text = res.json()["choices"][0]["message"]["content"].strip()

#     # Remove accidental markdown fences
#     if text.startswith("```"):
#         text = text.replace("```json", "").replace("```", "").strip()

#     # Parse JSON
#     try:
#         data = json.loads(text)
#     except Exception:
#         frappe.throw(f"Invalid JSON from AI:\n{text}")

#     # Validate mandatory fields
#     required = [
#         "score_out_of_10",
#         "ai_summary",
#         "strong_areas",
#         "weak_areas",
#         "improvement_plan",
#         "reasoning_for_score"
#     ]

#     missing = [k for k in required if k not in data]

#     if missing:
#         frappe.throw(f"AI returned incomplete result. Missing: {missing}")
    
#     return data


def create_audit_log(doc,method):
    if doc.doctype == "Audit Log":
        return
    doctype = ["Answer Script","Question","Daily Test","Mentee","Mentor","Request"]
    if doc.doctype in doctype:
        audit = frappe.new_doc("Audit Log")
        audit.doctype_name = doc.doctype
        audit.document_id = doc.name
        audit.action = method
        audit.user = frappe.session.user
        audit.insert(ignore_permissions=True)


def log_login(login_manager):
    doc = frappe.get_last_doc("Activity Log")
    frappe.get_doc({
        "doctype": "Audit Log",
        "doctype_name": "Activity Log",
        "document_id": doc.name,
        "action": "Login",
        "user": frappe.session.user
    }).insert(ignore_permissions=True)


def log_logout(login_manager=None):
    doc = frappe.get_last_doc("Activity Log")
    frappe.get_doc({
        "doctype": "Audit Log",
        "doctype_name": "Activity Log",
        "document_id": doc.name,
        "action": "Logout",
        "user": frappe.session.user
    }).insert(ignore_permissions=True)



def call_llm_api_daily(prompt: str):
    import frappe, json, re
    import requests

    url = "https://api.groq.com/openai/v1/chat/completions"
    api_key = frappe.conf.get("groq_api_key")

    if not api_key:
        frappe.throw("Groq API key missing in site_config.json")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    # --- STRICT SYSTEM MESSAGE ---
    messages = [
        {
            "role": "system",
            "content": (
                "You must output ONLY valid JSON. "
                "No markdown, no text outside JSON, no headings, no comments."
            )
        },
        {
            "role": "user",
            "content": prompt
        }
    ]

    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": messages,
        "temperature": 0  # ZERO hallucination
    }

    # ------------------------------
    # CALL MODEL
    # ------------------------------
    res = requests.post(url, headers=headers, json=payload)

    if res.status_code != 200:
        frappe.throw(f"LLM API Error: {res.text}")

    text = res.json()["choices"][0]["message"]["content"].strip()

    # ------------------------------
    # CLEAN OUTPUT
    # ------------------------------
    # Remove fences
    if text.startswith("```"):
        text = text.replace("```json", "").replace("```", "").strip()

    # Extract JSON if wrapped in text
    match = re.search(r"\{.*\}", text, flags=re.S)
    if not match:
        frappe.throw(f"AI returned no valid JSON object:\n{text}")

    json_str = match.group(0)

    # ------------------------------
    # PARSE JSON
    # ------------------------------
    try:
        data = json.loads(json_str)
    except Exception:
        frappe.throw(f"AI returned malformed JSON:\n{json_str}")

    required = [
        "score_out_of_10",
        "ai_summary",
        "strong_areas",
        "weak_areas",
        "improvement_plan",
        "reasoning_for_score"
    ]

    missing = [f for f in required if f not in data]
    if missing:
        frappe.throw(f"AI returned incomplete JSON. Missing fields: {missing}")

    return data



def evaluate_with_ai(parent, data,mentee_id):
    url = "http://135.13.20.57:11434/api/generate"  
    question = []
    total = 0

    for item in data:
        question_id = item["question_id"]

        text = f"""
            Question: {item['question']}
            Concept: {item['concept']}
            Mentor Answer: {item['mentor_answer']}
            Mentee Answer: {item['mentee_answer']}
        """


        prompt = f"""
            MASTER PROMPT — AI ANALYSER (Concept Understanding Scoring Engine | Ultra-Strict | Zero-Teaching | Python • MySQL • Frappe)

            You are an advanced AI operating under the role:

            ROLE:
            "AI Analyser (Expert Evaluator, Senior Examiner, Concept Understanding Scorer | Ultra-Strict Mode)"

            DOMAIN:
            "Concept-Based Evaluation System (Python, MySQL, Frappe — Infer exact sub-concept strictly from Mentor Answer)"

            USER_QUESTION_OR_TASK:
            "Evaluate a Mentee Answer against a Mentor Answer and assign a score based primarily on the mentee’s conceptual understanding. Focus strictly on how well the mentee grasps the concept (not how well they match wording). Provide concise diagnostic feedback and identify conceptual strength or weakness — WITHOUT teaching, corrections, or external additions."

            ------------------------------------------------------------
            🔒 CORE OBJECTIVE — UNDERSTANDING-FIRST EVALUATION

            You MUST:
            1. Compare Mentor vs Mentee Answer.
            2. Evaluate:
               - Conceptual Understanding (TOP PRIORITY)
               - Logical correctness
               - Alignment with the core idea
            3. Ignore:
               - Syntax issues if logic is correct
               - Wording differences
            4. Assign a score (0–10) based only on understanding.
            5. Provide concise diagnostic feedback (no teaching).
            6. Identify:
               - ❌ Concept to concentrate (if weak/partial)
               - ✅ Concept strength (if well understood)

            ------------------------------------------------------------
            🧠 INTERNAL EVALUATION FRAMEWORK

            STEP 1 — CONCEPT IDENTIFICATION
            • Extract the exact concept from the Mentor Answer
            • Examples:
              - Python → “list comprehension”, “function scope”
              - MySQL → “INNER JOIN”, “aggregation”
              - Frappe → “frappe.get_doc”, “DocType logic”

            STEP 2 — UNDERSTANDING ANALYSIS
            Classify the mentee’s level:

            1. Deep Understanding:
               - Captures core idea clearly
               - Logic correct
               - Wording may differ

            2. Good Understanding:
               - Mostly correct
               - Minor gaps

            3. Partial Understanding:
               - Some correct ideas
               - Incomplete or unclear

            4. Weak Understanding:
               - Misinterprets or misses core idea

            5. No Understanding:
               - Incorrect or irrelevant

            STEP 3 — VALIDATION
            Ask:
            • Does mentee explain WHY/WHAT correctly?
            • Is logic aligned with the concept?
            • Is understanding genuine or superficial?

            Rules:
            ✔ Different correct explanation = valid  
            ✘ Keyword matching without conceptual grasp = invalid  

            STEP 4 — CONCEPT CLASSIFICATION  
            Choose ONE:
            1. Strong Concept  → deep/good understanding  
            2. Concept to Concentrate → partial/weak/none  

            You MUST explicitly name the concept (e.g., “Python Loop Control”, “MySQL LEFT JOIN”, “Frappe ORM Usage”).

            STEP 5 — SCORING (UNDERSTANDING-BASED ONLY)
            9–10 → Deep understanding  
            7–8  → Good understanding  
            5–6  → Partial understanding  
            3–4  → Weak understanding  
            0–2  → No understanding  

            Understanding > syntax  
            Understanding > wording  

            ------------------------------------------------------------
            🔍 META-CHECK BEFORE OUTPUT
            Ask yourself:
            • Did I prioritize understanding over wording?
            • Did I avoid assumptions?
            • Is the concept correctly identified?
            • Does the score match the level of understanding?

            If uncertain → reduce score.

            ------------------------------------------------------------
            ⚠ STRICT RULES
            • Use ONLY Mentor & Mentee answers.
            • You may use external knowledge ONLY if aligned with Mentor Answer.
            • NO teaching.
            • NO suggestions.
            • NO corrections.
            • NO rewriting the answers.

            ------------------------------------------------------------
            ✍ OUTPUT FORMAT (MANDATORY JSON ONLY)

            Return ONLY this structure:

            {{
              "score": "Out of 10",
              "Feedback": "1–3 precise lines about understanding—no teaching."
            }}

            No markdown.  
            No extra text.  
            No additional fields.  
            JSON ONLY.

            ------------------------------------------------------------
            🎯 STYLE
            • Sharp evaluator tone  
            • Minimal, precise  
            • No teaching language  
            • Focus purely on understanding  

            ------------------------------------------------------------
            🚀 FINAL DIRECTIVE
            Score based solely on how well the mentee understands the concept — NOT on similarity to the mentor’s wording.

            Reward:
            • Real understanding  
            • Correct reasoning  

            Penalize:
            • Superficial answers  
            • Incorrect reasoning  
            • Misunderstanding  

            Output ONLY valid JSON.

            {text}
            """

        payload = {
         "model": "qwen3:8b",
         "prompt": prompt,
         "stream": False
        }

        # ---- CALL OLLAMA ----
        res = requests.post(url, json=payload)
        if res.status_code != 200:
            frappe.throw(f"LLM API Error: {res.text}")

        raw = res.json().get("response", "").strip()
        raw = raw.replace("```json", "").replace("```", "").strip()

        # Extract JSON
        match = re.search(r"\{.*\}", raw, flags=re.S)
        if not match:
            frappe.throw(f"AI returned no JSON:\n{raw}")

        try:
            result = json.loads(match.group(0))
        except:
            frappe.throw(f"Invalid JSON from AI:\n{raw}")

        # Validate
        if "score" not in result or "Feedback" not in result:
            frappe.throw(f"AI returned incomplete result:\n{result}")

        score = result.get("score",0)
        feedback = result["Feedback"]
        total += int(score)
        question.append({"question_id":question_id,"ai_summary":feedback,"ai_score":score,"your_answer":item['mentee_answer']})
    final = total / len(question) 
    report = frappe.get_doc({
        'doctype':"AI Report",
        'mentee_id':mentee_id,
        'exam_id':parent,
        'total_score':total,
        'table_amwm':question
    }).insert(ignore_permissions=True)

    return "OK"
    

def strip_html(text):
    if not text:
        return ""
    return re.sub(r"<[^>]+>", "", text)

def send_telegram(chat_id, msg):
    frappe.log_error("send",chat_id)
    token = frappe.conf.telegram_bot_token
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, json={
    "chat_id": chat_id,
    "text": msg,
    "parse_mode": "Markdown"
    })

@frappe.whitelist()
def get_list():
    user = frappe.session.user
    roles = frappe.get_roles(user)

    if "CTO" in roles and "Administrator" in roles:
        mentee = frappe.get_all("Mentee", fields=["name", "name1"])

    elif "Mentor" in roles:
        mentee = frappe.get_all("Mentee",{"mentor_id":user},["name","name1"])

    elif "Mentee" in roles:
        mentee = frappe.db.get_value("Mentee", {"email": user}, ["name","name1"],as_dict=True)
        frappe.log_error("mentee",mentee)
            
    return mentee


@frappe.whitelist()
def get_report(mentee, type, date=None, week=None, month=None):
    filters = {"mentee_id": mentee, "type": type}
    if date: filters["date"] = date
    if week: filters["week"] = week
    if month: filters["month"] = month

    data = frappe.get_value("Performance Report", filters,
        ["strong_area", "week_area", "improvement", "summary","name"],as_dict=True)
    frappe.log_error("data",data)
    return data

@frappe.whitelist()
def get_top_weekly():
    data = frappe.db.sql("""
        SELECT 
            pr.mentee_id,
            m.name1,
            MAX(pr.ai_score) AS ai_score
        FROM `tabPerformance Report` pr
        JOIN `tabMentee` m ON pr.mentee_id = m.name
        WHERE pr.type = 'Weekly'
        GROUP BY pr.mentee_id, m.name1
        ORDER BY ai_score DESC
        LIMIT 5
    """, as_dict=True)

    frappe.log_error("get_top",data)
    return data
