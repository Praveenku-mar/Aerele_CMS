import frappe
import requests
import json
import re

def call_llm_api(prompt: str):
    url = "https://api.groq.com/openai/v1/chat/completions"
    api_key = frappe.conf.get("groq_api_key")

    if not api_key:
        frappe.throw("Groq API key missing in site_config.json")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are an evaluator.\n"
                    "Respond ONLY with valid JSON.\n"
                    "Mandatory format:\n"
                    "{\"score\": number, \"feedback\": \"string\"}\n"
                    "Both keys must always exist. No markdown. No extra text."
                )
            },
            {"role": "user", "content": prompt}
        ]
    }

    res = requests.post(url, headers=headers, json=payload)

    if res.status_code != 200:
        frappe.throw(f"LLM API Error: {res.text}")

    text = res.json()["choices"][0]["message"]["content"].strip()

    # Remove accidental markdown fences
    if text.startswith("```"):
        text = text.replace("```json", "").replace("```", "").strip()

    # Parse JSON
    try:
        data = json.loads(text)
    except Exception:
        frappe.throw(f"Invalid JSON from AI:\n{text}")

    # Validate mandatory fields
    if "score" not in data or "feedback" not in data:
        frappe.throw(f"AI returned incomplete result: {data}")

    return data


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
    url = "https://api.groq.com/openai/v1/chat/completions"
    api_key = frappe.conf.get("groq_api_key")

    if not api_key:
        frappe.throw("Groq API key missing in site_config.json")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a daily performance evaluator.\n"
                    "Respond ONLY with valid JSON.\n"
                    "Required format:\n"
                    "{\"summary\": \"string\", \"tasks_completed\": [\"string\"], \"strengths\": \"string\", \"weaknesses\": \"string\", \"improvements\": \"string\"}\n"
                    "All keys are mandatory. No markdown. No extra text. Output must be valid JSON ONLY."
                )
            },
            {"role": "user", "content": prompt}
        ]
    }

    res = requests.post(url, headers=headers, json=payload)

    if res.status_code != 200:
        frappe.throw(f"LLM API Error: {res.text}")

    text = res.json()["choices"][0]["message"]["content"].strip()

    if text.startswith("```"):
        text = text.replace("```json", "").replace("```", "").strip()

    try:
        data = json.loads(text)
    except:
        frappe.throw(f"Invalid JSON from AI:\n{text}")

    required_keys = ["summary", "strengths", "weaknesses", "improvements"]

    missing = [k for k in required_keys if k not in data]
    if missing:
        frappe.throw(f"AI returned incomplete fields: {missing}\nFull Response: {data}")

    return data



def evaluate_with_ai(parent, data,mentee_id):
    print("Function called")
    frappe.log_error("eval",parent)
    frappe.log_error("data",data)

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


