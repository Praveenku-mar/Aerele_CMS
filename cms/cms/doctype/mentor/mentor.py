# Copyright (c) 2026, Praveenkumar Dhanasekar and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import re

class Mentor(Document):
	def before_save(self):
		self.validate_phone()

	def validate_phone(self):
		phone = str(self.phone_number or "")
		if not re.fullmatch(r"\d{10}",phone):
			frappe.throw("Phone number must contain exactly 10 digits.")

