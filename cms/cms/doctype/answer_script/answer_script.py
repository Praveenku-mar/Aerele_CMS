# Copyright (c) 2026, Praveenkumar Dhanasekar and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import date
import requests



class AnswerScript(Document):
	def validate(self):
		self.validate_time()

	def on_submit(self):
		self.validate_owner()
		if self.status == "Approved":
			self.copy_doc()


	def copy_doc(self):

		mentees = frappe.get_all("Mentee", fields=["name"])
		if not mentees:
			return

		src = frappe.get_doc("Answer Script", self.name)

		for row in mentees:
			new_doc = frappe.new_doc("Daily Test")
			new_doc.mentee_id = row["name"]

			new_doc.exam_start_time = src.exam_start_time
			new_doc.exam_end_time = src.exam_end_time
			for q in src.questions:
				new_doc.append("questions", {
					"question_id": q.question_id,
					"question": q.question,
					"correct_answer": q.correct_answer,
					"ai_score": 0,
					"mentor_score": 0
				})
			new_doc.insert()
	
	
	def validate_owner(self):
		if frappe.session.user == "Administrator":
			return
		if self.owner == frappe.session.user:
			frappe.throw("You cannot approve an Answer Script you created.")


	def validate_time(self):
		st = self.exam_start_time
		ed = self.exam_end_time
		
		if st >= ed:
			frappe.throw("End time must be greater than start time")



def permission_query_condition(user):
	if user == "Administrator":
		return ""

	roles = frappe.get_roles(user)
	if "Mentor" in roles:
		return ""

	mentee = frappe.db.get_value(
		"Mentee", 
		{"email": user}, 
		"name"
	)

	if not mentee:
		return "1=0"   

	return f"`tabDaily Test`.mentee_id = '{mentee}'"


