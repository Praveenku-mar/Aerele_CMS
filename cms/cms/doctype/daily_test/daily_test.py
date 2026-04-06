# Copyright (c) 2026, Praveenkumar Dhanasekar and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import now_datetime, get_datetime
import re
from cms.cms.api import strip_html
from frappe.model.document import Document

class DailyTest(Document):

	def before_submit(self):
		if now_datetime() < get_datetime(self.exam_start_time):
			frappe.throw("You cannot submit the test before the exam start time.")
		if self.is_submited != 1:
			self.validate_all_answer()


	def on_submit(self):
		self.validate_answer_with_ai()

	def validate_all_answer(self):
		missing = []
		for row in self.questions:
			if not row.answer:
				missing.append(row.question_id)
		msg = ", ".join(missing)
		if missing:
			frappe.throw(f"Your are not answer for these following question {msg}.")


	def validate_answer_with_ai(self):
		batch = []

		for row in self.questions:
			mentee_answer = strip_html(row.answer)
			batch.append({
				"question_id": row.question_id,
				"question": row.question,
				"mentee_answer": mentee_answer,
				"mentor_answer": row.correct_answer,
				"concept": row.concept
			})

		frappe.enqueue(
			"cms.cms.api.evaluate_with_ai",
			queue="long",
			job_name=f"ai_eval_{self.name}",
			parent=self.name,
			data=batch,
			mentee_id=self.mentee_id
		)

	

@frappe.whitelist()
def get_or_set_session_start(docname):
	doc = frappe.get_doc("Daily Test", docname)
	now = frappe.utils.now_datetime()

	if doc.start == 0:
		doc.start = 1

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


    
	