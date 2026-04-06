# Copyright (c) 2026, Praveenkumar Dhanasekar and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Question(Document):
	pass


@frappe.whitelist()
def get_mentor():
	users = frappe.get_all("User", fields=["name"])
	mentors = []

	for u in users:
		roles = frappe.get_roles(u["name"])
		if "Mentor" in roles:
			mentors.append(u["name"])

	frappe.log_error("mentor list",mentors)

	return mentors
