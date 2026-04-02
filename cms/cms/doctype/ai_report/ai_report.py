# Copyright (c) 2026, Praveenkumar Dhanasekar and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class AIReport(Document):
	pass



def ai_report_permission_query_condition(user):
	roles = frappe.get_roles(user)

	if "CTO" in roles or "Administrator" in roles:
		return ""
	if "Mentor" in roles:
		return f"""
			`tabAI Report`.`mentee_id` IN (
				SELECT name
				FROM `tabMentee`
    	        WHERE mentor_id = '{user}'
    	    )
    	"""

	if "Mentee" in roles:
		mentee_id = frappe.db.get_value("Mentee", {"email": user}, "name")
		if mentee_id:
			return f"`tabAI Report`.`mentee_id` = '{mentee_id}' AND `tabAI Report`.`status`='Approved'"

	return "1=0"