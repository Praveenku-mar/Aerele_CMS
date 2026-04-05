# Copyright (c) 2026, Praveenkumar Dhanasekar and contributors
# For license information, please see license.txt
import frappe
from frappe.utils.nestedset import NestedSet


class Concept(NestedSet):
	def autoname(self):
		if self.concept and not self.question_id:
			self.name = self.concept

		if self.question_id and not self.concept:
			self.name = self.question_id
