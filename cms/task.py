import frappe
import requests
import json
from datetime import datetime, timedelta
from cms.cms.api import call_llm_api_daily


def generate_report(mentee, start, end, report_type):
    tests = frappe.get_all(
        "Daily Test",
        filters={
            "mentee_id": mentee,
            "docstatus": 1,
            "creation": ["between", [start, end]]
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

    # build Q&A
    qna_list = "\n".join(
        [f"Q: {q['question']}\nA: {q['answer']}\n correct_answer:{q['correct_answer']}" for q in questions]
    )
    ROLE = "Performance Analyst + Academic Evaluator"
    DOMAIN = "Frappe , MySQL"

    prompt = (
    f"{qna_list}"
    + f"""
        You are operating as a dual-expert system embodying the combined roles of:
        {ROLE} → “Performance Analyst” + “Academic Evaluator”
        Your responsibility is to generate {report_type} Performance Reports**
        for the domain/context:
        {DOMAIN} → “Employee performance, Student assessment, Skill test analysis.”

        Your task is to produce a **structured, motivational, professional, comparison-based performance report** that includes:
        • Strong Areas  
        • Weak Areas (explained in deeper detail)  
        • Improvement Areas (with analysis + actionable steps)  
        • Scores/metrics  
        • Time-based comparisons (daily, weekly, monthly)  
        • Zero hallucinations  
        • Factual, logical reasoning  
        • No assumptions without stated data  

        ────────────────────────────────────────────
        ### 🔥 **REPORT STRUCTURE — ALWAYS USE THE SAME FORMAT**  
        (For DAILY, WEEKLY, and MONTHLY Reports)

        1. **Header Section**
           - Candidate/Employee/Student Name (if provided)
           - Date Range (Daily/Weekly/Monthly)
           - Purpose of the report  
           - Type of assessment or test evaluated

        2. **Performance Summary (Motivational + Professional Tone)**
           Provide a clear narrative explaining:
           - Overall performance level  
           - Highlights and notable achievements  
           - General direction of progress  
           - Motivation + confidence-building statements  
           - Keep tone encouraging but factual  

        3. **Strong Areas (Short, Confidence-Boosting, Specific)**
           - Clearly list what the candidate is **strong at**  
           - Explain why these strengths are solid  
           - Mention evidence from the assessment/test  
           - Reinforce confidence through positive, precise phrasing  

        4. **Weak Areas (Detailed, Analytical, Deep Explanation)**
           For each weak area include:
           - What the weakness is  
           - How it manifested in this test  
           - How performance in this area compares to:  
             • previous tests,  
             • other skills,  
             • expected standards  
           - Identify logical patterns or behavioral clues  
           - Explain whether the weakness is due to:  
             • skill gaps,  
             • misunderstanding,  
             • lack of practice,  
             • inconsistency,  
             • difficulty with time/pressure, etc.  

           (Weak areas MUST be more detailed than strong areas.)

        5. **Improvement Areas (Root-Cause + Actionable Plan)**
           Provide a structured improvement framework:
           A. **Possible Reasons for Low Performance**
              - Internal factors (skill, knowledge, consistency)  
              - External factors (stress, pacing, environment, misunderstanding of instructions)  
           B. **Suggested Improvement Strategy**
              - Concrete, step-by-step actions  
              - Practice recommendations  
              - Study/work techniques  
              - Behavioral adjustments  
              - Frequency and duration of improvements  
           C. **Expected Outcome**
              - What will improve  
              - What progress should look like  

        6. **Scorecard Section**
           Provide numeric or qualitative scores:
           - Overall Score  
           - Section-wise Scores  
           - Performance Trend: ↑ / ↓ / →  
           - Benchmark comparison (if applicable)  

        7. **Time-Based Comparative Analysis**
           Provide comparisons based on the timeframe of the report:
           - DAILY → Compare with yesterday or previous assessment  
           - WEEKLY → Compare with earlier days of the week  
           - MONTHLY → Compare with previous weeks or prior months  
           Include:
           - Improvements  
           - Declines  
           - Consistency measurements  
           - Trend interpretations  

        8. **Final Summary & Forward Direction**
           - Close with a motivational, professional summary  
           - Reinforce confidence while staying factual  
           - Clearly define what to prioritize next  
           - Provide reassurance that improvement is achievable  

        ────────────────────────────────────────────
        ### RULES & INTELLIGENCE REQUIREMENTS

        1. **Never hallucinate data.**  
           If information is missing, ask for clarification or state that it's unavailable.

        2. **Tone control:**  
           Always remain motivational, supportive, professional, and confidence-boosting.

        3. **Analytical depth:**  
           Use reasoning to explain the *why* behind every strength, weakness, and improvement need.

        4. **Consistency:**  
           DAILY, WEEKLY, and MONTHLY reports must follow the **exact same structure**.

        5. **Comparisons required:**  
           Always compare performance with past attempts when data is provided.

        6. **Domain-sensitive writing:**  
           Adjust examples and explanations based on whether the subject is:
           - an employee  
           - a student  
           - a skill-test candidate  

        7. **No vague statements.**  
           Everything must be precise, evidence-based, and tied to the provided performance data.

        ────────────────────────────────────────────
        ### EXECUTION FORMAT

        When generating a report, always respond in the following order:

        **“Daily/Weekly/Monthly Performance Report — Based on {ROLE}, Evaluating {DOMAIN}”**  
        Then produce the full structured report exactly as defined above.

        ────────────────────────────────────────────
        ### VARIABLES TO ALWAYS INCLUDE  
        {ROLE}  
        {DOMAIN}  
        {qna_list} → “Provide strong, weak, and improvement areas with score, motivational + professional tone, same structure, include comparisons.”

        ────────────────────────────────────────────
       🚀 FINAL DIRECTIVE 
            Deliver the final output as a **fully structured, polished, zero-hallucination performance report** strictly following every rule above.
        
            Score based solely on how well the mentee understands the concept — NOT on similarity to the mentor’s wording.

            Reward:
            • Real understanding  
            • Correct reasoning  

            Penalize:
            • Superficial answers  
            • Incorrect reasoning  
            • Misunderstanding  

            Output ONLY valid JSON.
        """
        )

    response = call_llm_api_daily(prompt)
    
    frappe.get_doc({
        "doctype": "Performance Report",
        "mentee_id": mentee,
        "type": report_type,
        "summary": response.get("summary"),
        "strong_area": response.get("strengths"),
        "week_area": response.get("weaknesses"),
        "improvement": response.get("improvements"),
    }).insert(ignore_permissions=True)


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