# Copyright (c) 2026, Praveenkumar Dhanasekar and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from cms.cms.api import call_llm_api

class DailyTest(Document):
	def before_submit(self):
		if self.is_submited != 1:
			self.check_all_answer()

	def on_submit(self):
		self.validate_answer_with_ai()
		self.calculate_total_mark()
		

	def calculate_total_mark(self):
		total_marks = 0
		count = 0
		for row in self.questions:
			total_marks += row.ai_score or 0
			count += 1

		self.total_marks = total_marks / count


	def check_all_answer(self):
		missing = []
		for q in self.questions:
			if not q.answer:
				missing.append(q.question_id)
		if missing:
			msg = ", ".join(missing)
			frappe.throw(f"The following questions are not answered: {msg}")


	def validate_answer_with_ai(self):
		for row in self.questions:
			prompt = f"""
			Question: {row.question.strip()}
			Correct Answer: {row.correct_answer}
			Mentee's Answer: {row.answer}

			Score this out of 10 and give JSON output:
			{{"score": 7, "feedback": ""}}
			"""

			response = call_llm_api(prompt)
			frappe.db.set_value(row.doctype, row.name, {
        		"ai_score": response.get("score"),
        		"ai_feedback": response.get("feedback")
    			})

		self.reload()



@frappe.whitelist()
def get_or_set_session_start(docname):
	frappe.log_error("sssssssss",docname)
	doc = frappe.get_doc("Daily Test", docname)
	now = frappe.utils.now_datetime()

	if now < doc.exam_start_time:
		return {"status": "not_started"}

	if now > doc.exam_end_time:
		return {"status": "ended"}

	if not doc.session_start_time and now >= doc.exam_start_time:
		doc.session_start_time = now
		doc.save()

	return {
		"status": "running",
		"session_start_time": doc.session_start_time
	}


@frappe.whitelist()
def check_all_answer(docname):
    doc = frappe.get_doc("Daily Test", docname)
    return [q.question_id for q in doc.questions if not q.answer]

	