# Copyright (c) 2026, Praveenkumar Dhanasekar and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate

class PerformanceReport(Document):
    def before_insert(self):
        date_obj = getdate(self.date)
        if self.type == "Weekly":
            self.week = date_obj.isocalendar()[1]
        if self.type == "Monthly":
            self.month = date_obj.month
        
        self.year = date_obj.year


def performance_report_permission_query_conditions(user):
    roles = frappe.get_roles(user)

    if "CTO" in roles or "Administrator" in roles:
        return ""

    if "Mentor" in roles:
        return f"""
            `tabPerformance Report`.`mentee_id` IN (
                SELECT name FROM `tabMentee`
                WHERE mentor_id = '{user}'
            )
        """

    if "Mentee" in roles:
        mentee_id = frappe.db.get_value("Mentee", {"email": user}, "name")
        if mentee_id:
            return f"`tabPerformance Report`.`mentee_id` = '{mentee_id}'"

    return "1=0"