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
        fields=["question", "answer"]
    )


    if not questions:
        return

    # build Q&A
    qna_list = "\n".join(
        [f"Q: {q['question']}\nA: {q['answer']}" for q in questions]
    )

    prompt = (
        f"Generate {report_type} performance report based on the following Q&A:\n\n"
        f"{qna_list}"
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