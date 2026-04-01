from frappe.email.doctype.notification.notification import Notification
from cms.cms.api import send_telegram,strip_html
import frappe

class Telegram(Notification):

    def send(self, doc):
        if self.channel != "Telegram":
            return super().send(doc)

        link = frappe.utils.get_url_to_form(doc.doctype, doc.name)

        if self.document_type == "Daily Test":
            message = (
            f"*New Test Available!*\n"
            f"*Test:* {doc.name}\n\n"
            f"Complete it within the allowed window!\n"
            f"*Test Timing:* {doc.exam_start_time} to {doc.exam_end_time}\n"
            f"*Duration:* 60 minutes\n\n"
            f"*Open the Test:* {link}\n\n"
            "Instructions:\n"
            "• Auto-submit when time ends\n"
            "• Do not switch tabs repeatedly\n"
            "• Start only when you're ready\n\n"
            "*All the best!*"
            )
            chat_id = frappe.db.get_value("Mentee", doc.mentee_id, "chat_id")
            if not chat_id:
                return

            send_telegram(chat_id,message)

        
        if self.name == "Request Notification":
            link = frappe.utils.get_url_to_form(doc.doctype, doc.name)
            mentor = frappe.db.get_value("Mentee",doc.mentee_id,["mentor_id","name1"],as_dict=True)
            chat_id = frappe.db.get_value("Mentor",{'email':mentor.mentor_id},"chat_id")

            if not chat_id:
                return
            
            message = (
                f"*New Exam Time Extended Request*\n"
                f"Mentee Id: {doc.mentee_id}\n"
                f"Mentee Name: {mentor.name1}\n"
                f"Exam Id : {doc.exam_no}\n"
                f"Requested Time : {doc.request_end_time}\n\n"
                f"Reason : {doc.reason}\n"
                f"Open the request : {link}"
            )

            send_telegram(chat_id,message)

        if self.name == "Request Approval Notification":
            link = frappe.utils.get_url_to_form("Daily Test", doc.exam_no)
            chat_id = frappe.db.get_value("Mentee", doc.mentee_id, "chat_id")

            if not chat_id:
                return

            message = (
                f"*Hi Dear,*\n"
                f"\t Your Request {doc.name} is :{doc.status}\n"
                f"\t Open the test :{link}"
            )

            send_telegram(chat_id,message)


        if self.name == "AI Report Request Notification":

            link = frappe.utils.get_url_to_form(doc.doctype, doc.exam_id)

            mentor_email = frappe.db.get_value("Mentee",doc.mentee_id,"mentor_id")
            chat_id = frappe.db.get_value("Mentor",{'email':mentor_email},"chat_id")

            if not chat_id:
                return
            
            message = (
                f"AI Report is created for the exam id {doc.exam_id}.\n"
                f"Please verify the result.\n"
                f"Open the link : {link}"
            )

            send_telegram(chat_id,message)

        if self.name == "AI Report Approved Notification":
            link = frappe.utils.get_url_to_form(doc.doctype, doc.exam_id)
            chat_id = frappe.db.get_value("Mentee", doc.mentee_id, "chat_id")

            frappe.log_error("mentee",chat_id)
            if not chat_id:
                frappe.throw("Not chat id")

            message = (
                f"Hi Dear, \n"
                f"Your Exam is verified by the AI and also Me.\n"
                f"Open the exam report : {link}"
            )

            send_telegram(chat_id, message)
            


            
