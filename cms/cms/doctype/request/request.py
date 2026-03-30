# Copyright (c) 2026, Praveenkumar Dhanasekar and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Request(Document):
	def on_submit(self):
		if self.status == "Approved":
			frappe.db.set_value("Daily Test",self.exam_no,"exam_end_time",self.request_end_time)
			email = frappe.get_value("Mentee",self.mentee_id,"email")
			frappe.sendmail(recipients=email,
				subject="Exam Time extend request related",
				message="Your exam end time request is approved.",
				now=True)

		if self.status == "Rejected":
			email = frappe.get_value("Mentee",self.mentee_id,"email")
			frappe.sendmail(recipients=email,
				subject="Exam Time extend request related",
				message="Your exam end time request is Rejected.",
				now=True)



@frappe.whitelist()
def request_time(date,exam_id,mentee_id):

	exists = frappe.db.exists("Request",{"exam_id":exam_id})
	if exists:
		return
	req = frappe.get_doc({
		"doctype": "Request",
		"mentee_id": mentee_id,
		"exam_no": exam_id,
		"request_end_time": date
	})

	req.insert(ignore_permissions=True)
