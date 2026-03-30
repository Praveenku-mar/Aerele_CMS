import frappe
import requests
import json

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

    required_keys = ["summary", "tasks_completed", "strengths", "weaknesses", "improvements"]

    missing = [k for k in required_keys if k not in data]
    if missing:
        frappe.throw(f"AI returned incomplete fields: {missing}\nFull Response: {data}")

    return data