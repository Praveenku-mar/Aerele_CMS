# Copyright (c) 2026, Praveenkumar Dhanasekar and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from datetime import datetime

def create_user(email,role):
	if frappe.db.exists("User",email):
		return frappe.get_doc("User",email)
	
	user = frappe.get_doc({
		"doctype":"User",
		"email":email,
		"first_name":email.split("@")[0],
		"roles":[{"role":role}]
	})
	user.insert(ignore_permissions=True)

	return user

def create_mentor(email="mentor1@gmail.com",phone_number=None):
	user = create_user(email,"Mentor")
	if not phone_number:
		phone_number = 9092837965

	if frappe.db.exists("Mentor",{"email":email}):
		return frappe.get_doc("Mentor",{"email":email})

	mentor = frappe.get_doc({
		"doctype":"Mentor",
		"email":email,
		"mentor_name":"Mentor Test",
		"phone_number":phone_number,
	}).insert(ignore_permissions=True)

	return mentor

def create_mentee(email,phone_number=None):
	user = create_user(email,"Mentee")
	if not phone_number:
		phone_number = 9092837965

	if frappe.db.exists("Mentee",{"email":email}):
		return frappe.get_doc("Mentee",{"email":email})

	mentee = frappe.get_doc({
		"doctype":"Mentee",
		"name1":"Mentee Test",
		"email":email,
		"mentor_id": "mentor1@gmail.com",
		"phone_number":phone_number
	}).insert(ignore_permissions=True)

	return mentee



def create_answer_script(
    status="Approved",
    start=None,
    end=None,
    question_list=None
):
    if not start:
        start = datetime(2026, 1, 1, 9, 0, 0)

    if not end:
        end = datetime(2026, 1, 1, 10, 0, 0)

    as_doc = frappe.get_doc({
        "doctype": "Answer Script",
        "exam_start_time": start,
        "exam_end_time": end,
        "status": status,
        "questions": []
    })

    if question_list:
        for q in question_list:
            as_doc.append("questions", {
                "question_id": q.name
            })

    as_doc.insert(ignore_permissions=True)
    return as_doc


def create_question(question="what is AI ?", answer="Artificial Intelligence"):
	if frappe.db.exists("Question",{"question":question,"answer":answer}):
		return frappe.get_doc("Question",{"question":question,"answer":answer})

	
	question = frappe.get_doc({
		"doctype":"Question",
		"question":question,
		"answer":answer,
		"status":"Approved"
	}).insert(ignore_permissions=True)

	return question





class TestAnswerScript(FrappeTestCase):
	
	def setUp(self):
		self.mentor = create_mentor("mentor1@gmail.com")
		self.mentee = create_mentee("mentee1@gmail.com")

		self.question = create_question(
			question="What is AI?",
            answer="Artificial Intelligence"
		)

	def test_validate_time_invalid(self):
		frappe.set_user(self.mentor.email)

		with self.assertRaises(frappe.ValidationError):
			create_answer_script(
				start=datetime(2025, 1, 1, 10, 0),
				end=datetime(2025, 1, 1, 10, 0),
				question_list=[self.question]
    	    )

	def test_validate_owner_prevents_creator_approval(self):
		frappe.set_user(self.mentee.email)

		as_doc = create_answer_script(
			status="Approved",
			start=datetime(2025, 1, 1, 9, 0),
			end=datetime(2025, 1, 1, 10, 0),
		)

		with self.assertRaises(frappe.ValidationError):
			as_doc.validate_owner()


	def test_answer_script_submit_creates_daily_test(self):
		frappe.set_user(self.mentor.email)

		as_doc = create_answer_script(
			status="Draft",
			start=datetime(2025, 1, 1, 9, 0),
			end=datetime(2025, 1, 1, 10, 0),
			question_list=[self.question]
		)

		mentor = create_mentor("mentor2@gmail.com")
		frappe.set_user("mentor2@gmail.com")
		as_doc.status = "Approved"
		as_doc.save()
		as_doc.submit()

		# Daily Test must be created for the mentee
		dt_list = frappe.get_all(
			"Daily Test",
			filters={"mentee_id": self.mentee.name},
			fields=["name"]
		)

		self.assertEqual(len(dt_list), 1)

		dt = frappe.get_doc("Daily Test", dt_list[0].name)

		# Verify datetime copy
		self.assertEqual(
			dt.exam_start_time,
			datetime(2025, 1, 1, 9, 0)
		)
		self.assertEqual(
			dt.exam_end_time,
			datetime(2025, 1, 1, 10, 0)
		)

		# Verify question copy
		self.assertEqual(len(dt.questions), 1)
		q = dt.questions[0]

		self.assertEqual(q.question, "What is AI?")
		self.assertEqual(q.correct_answer, "Artificial Intelligence")

	def test_validate_mentor_phone_number(self):
		frappe.set_user("Administrator")
		invalid_numbers = [
			"12345",
			"123456789012",
			"98765abc12",
			"+919876543210",
			"98 765 43210",
			"",
			None
		]

		for number in invalid_numbers:
			with self.assertRaises(frappe.ValidationError):
				frappe.get_doc({
					"doctype": "Mentor",
					"email": "mentor1@gmail.com",
					"phone_number": number
				}).insert() 


	def test_validate_mentee_phone_number(self):
		frappe.set_user("Administrator")
		invalid_numbers = [
			"12345",
			"123456789012",
			"98765abc12",
			"+919876543210",
			"98 765 43210",
			"",
			None
		]

		for number in invalid_numbers:
			with self.assertRaises(frappe.ValidationError):
				frappe.get_doc({
					"doctype": "Mentee",
					"email": "mentee1@gmail.com",
					"mentor_id":"mentor1@gmail.com",
					"phone_number": number
				}).insert()   


	


	



		
