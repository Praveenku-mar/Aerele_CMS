# Copyright (c) 2026, Praveenkumar Dhanasekar and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import date
import requests
from cms.cms.api import call_llm_api


class AnswerScript(Document):
	def validate(self):
		self.validate_time()

	def before_submit(self):
		self.check_all_answer()
	
	def on_submit(self):
		self.validate_answer_with_ai()

	
	def check_all_answer(self):
		missing = []
		# frappe.log_error("1111111")

		for q in self.questions:
			# frappe.log_error("22222",q)
			if not q.answer:
				missing.append(q.question_id)
		# frappe.log_error("missinf",missing)
		if missing:
			msg = ", ".join(missing)
			frappe.throw(f"The following questions are not answered: {msg}")


	def validate_answer_with_ai(self):
		frappe.log_error("1111111111 after")
		for row in self.questions:
			prompt = f"""
			Question: {row.question.strip()}
			Correct Answer: {row.correct_answer}
			Mentee's Answer: {row.answer}

			Score this out of 10 and give JSON output:
			{{"score": 7, "feedback": ""}}
			"""

			response = call_llm_api(prompt)
			frappe.log_error("response",response)
			frappe.db.set_value(row.doctype, row.name, {
        		"ai_score": response.get("score"),
        		"ai_feedback": response.get("feedback")
    			})

		self.reload()
	


	def validate_time(self):
		st = self.exam_start_time
		ed = self.exam_end_time
		
		if st >= ed:
			frappe.throw("End time must be greater than start time")



def permission_query_condition(user):
	if user == "Administrator":
		return ""
	# get mentee record for this logged-in user
	mentee = frappe.db.get_value(
		"Mentee", 
		{"email": user}, 
		"name"
	)

	if not mentee:
		return "1=0"   # block everything

	# mentee_id in Answer Script refers to Mentee.name
	return f"`tabAnswer Script`.mentee_id = '{mentee}'"
