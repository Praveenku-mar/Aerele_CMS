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