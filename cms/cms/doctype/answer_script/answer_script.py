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
		frappe.log_error("Copy",self.name)
		mentee = frappe.get_all("Mentee",fields=["name"])
		if not mentee:
			return
		src = frappe.get_doc("Answer Script", self.name)
		for row in mentee:
			new_doc = frappe.new_doc("Daily Test")
			new_doc.mentee_id = row
			new_doc.exam_start_time = src.exam_start_time
			new_doc.exam_end_time = src.exam_end_time
			new_doc.questions = src.questions
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
	# get mentee record for this logged-in user
	mentee = frappe.db.get_value(
		"Mentee", 
		{"email": user}, 
		"name"
	)

	if not mentee:
		return "1=0"   # block everything

	# mentee_id in Answer Script refers to Mentee.name
	return f"`tabDaily Test`.mentee_id = '{mentee}'"


