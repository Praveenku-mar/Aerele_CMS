import frappe
import requests
import json
from datetime import datetime, timedelta
from cms.cms.api import call_llm_api_daily,strip_html


def generate_report(mentee_id, start_date, end_date, report_type):
   
   tests = frappe.get_all(
        "Daily Test",
        filters={
            "mentee_id": mentee_id,
            "docstatus": 1,
            "creation": ["between", [start_date, end_date]]
        },
        pluck="name"
    )   
   if not tests:
        return   
   questions = frappe.get_all(
        "Test Question",
        filters={
            "parenttype": "Daily Test",
            "parentfield": "questions",
            "parent": ["in", tests]
        },
        fields=["question", "answer","correct_answer"]
   )    
   if not questions:
       return
   qna_list = ""
   for q in questions:
        ans = strip_html(q.answer)
        qna_list += f"Q: {q.question}\nA: {ans}\ncorrect_answer: {q.correct_answer}\n\n"    
   prompt = """
      You are operating as a Hybrid-Meta Evaluation System combining Chain-of-Thought (CoT), Tree-of-Thought (ToT), ReAct Reasoning, and Metacognitive Reflection.  
      Your operation must follow strict zero-hallucination policies and avoid any inference that is not explicitly supported by the provided data.   
      ───────────────────────────────────────────
      ### 🎭 SYSTEM ROLES  
      You now embody the combined expert roles:   
      ROLE →  
      • Performance Analyst  
      • Assessment Validator  
      • Skill Test Examiner     
      Your responsibility is to evaluate performance quality with structured analytical depth and to generate a JSON-only output containing:
      • score_out_of_10  
      • ai_summary  
      • strong_areas  
      • weak_areas  
      • improvement_plan  
      • reasoning_for_score     
      ───────────────────────────────────────────
      ### 📚 DOMAIN  
      You must perform all evaluations strictly within:    
      DOMAIN →  
      • Student Learning  
      • Employee Training       
      You may NOT hallucinate any domain-specific details not explicitly present. You may NOT assume hidden context.  
      Minimal inference is allowed **only when logically deducible from Q and A** and must never contradict given data.   
      ───────────────────────────────────────────
      ### 📥 INPUT FORMAT  
      You will ALWAYS receive:     
      • Q → The Question  
      • A → The Mentee’s Answer  
      • correct_answer → The official correct answer for reference     
      All evaluation MUST consider:
      1. The question itself (context, complexity, expectations)  
      2. The mentee’s answer  
      3. The correct answer  
      4. The reasoning quality, not just similarity to the correct answer       
      ───────────────────────────────────────────
      ### 🧠 INTELLIGENCE REQUIREMENTS   
      Your evaluation must follow these principles:     
      1. **Evaluate understanding, not memorization**  
      2. **Zero hallucination**  
      3. **Evidence-based judgement**  
      4. **Deep analytical breakdown**  
      5. **Respect scoring policy**  
      6. **Explain the score**     
      ───────────────────────────────────────────
      ### 🧾 OUTPUT REQUIREMENTS (JSON ONLY)   
      You MUST output a strict JSON object:    
      {{
        "score_out_of_10": number,
        "ai_summary": "A clear summary of the mentee’s performance",
        "strong_areas": "string",
        "weak_areas":  "string",
        "improvement_plan": "Actionable, domain-specific improvements with reasoned steps",
        "reasoning_for_score": "Why the mentee received this score, referencing Q, A, and correct_answer"
      }}   
      Rules:
      - No extra text outside JSON  
      - No commentary  
      - No markdown  
      - No hidden fields  
      - No removed fields  
      - No hallucinations       
      ───────────────────────────────────────────
      ### 🏁 FINAL EXECUTION       
      """
   
   final_prompt = prompt + "\n\nEvaluate the following responses:\n" + qna_list
   ai_result = call_llm_api_daily(final_prompt)
   doc = frappe.new_doc("Performance Report")
   doc.mentee_id = mentee_id
   doc.date = datetime.now()
   doc.type = report_type
   doc.ai_score = ai_result["score_out_of_10"]
   doc.summary = ai_result["ai_summary"]
   doc.strong_area = json.dumps(ai_result["strong_areas"])
   doc.week_area = json.dumps(ai_result["weak_areas"])
   doc.improvement = ai_result["improvement_plan"]
   doc.why_i_gave_this_score = ai_result["reasoning_for_score"]
   doc.insert(ignore_permissions=True)
   frappe.log_error("name",doc.name)

def daily():
    mentees = frappe.get_all("Mentee", pluck="name")
    now = datetime.now()
    start = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    end = now

    for mentee in mentees:
        generate_report(mentee, start, end, "Daily")


def monthly():
    mentees = frappe.get_all("Mentee", pluck="name")
    now = datetime.now()
    start = now - timedelta(days=30)
    end = now

    for mentee in mentees:
        generate_report(mentee, start, end, "Monthly")


def weekly():
    mentees = frappe.get_all("Mentee", pluck="name")
    now = datetime.now()
    start = now - timedelta(days=7)
    end = now

    for mentee in mentees:
        generate_report(mentee, start, end, "Weekly")