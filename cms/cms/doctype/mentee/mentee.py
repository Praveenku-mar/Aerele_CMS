# Copyright (c) 2026, Praveenkumar Dhanasekar and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import re

class Mentee(Document):
	def before_save(self):
		self.validate_phone()

	def validate_phone(self):
		phone = str(self.phone_number or "")
		if not re.fullmatch(r"\d{10}",phone):
			frappe.throw("Phone number must contain exactly 10 digits.")



def get_permission_query_conditions(user):
	if not user or user == "Administrator":
		return ""

	frappe.log_error("user",user)

	# Check if logged-in user has Mentor role
	if "Mentor" in frappe.get_roles(user):

		mentor_id = frappe.db.get_value("Mentor", {"email": user}, "email")
		frappe.log_error("mentor",mentor_id)

		if mentor_id:
			return f""" `tabMentee`.`mentor_id` = '{mentor_id}' """

		return "1=0" 

	# return ""


def permission_query_conditions_mentor_see_mentees_answer_script(user):
    # If not a Mentor user → no restriction
    if "Administrator":
        return ""

    return f"""
        mentee IN (
            SELECT name FROM `tabMentee`
            WHERE mentor IN (
                SELECT name FROM `tabMentor`
                WHERE user = '{user}'
            )
        )
    """