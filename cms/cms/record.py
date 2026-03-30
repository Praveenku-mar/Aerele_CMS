import frappe

data = [
  {
    "question": "What is a Doctype in Frappe?",
    "answer": "A Doctype defines structured data and server-side logic for a module.",
    "module": "Core",
    "concept": "Model"
  },
  {
    "question": "What is the purpose of frappe.get_doc?",
    "answer": "It loads or creates a document instance for reading or saving.",
    "module": "Core",
    "concept": "ORM"
  },
  {
    "question": "What does frappe.db.get_value do?",
    "answer": "It fetches a specific field value directly from the database.",
    "module": "Database",
    "concept": "Querying"
  },
  {
    "question": "What are permission query conditions?",
    "answer": "They restrict backend data visibility using SQL-based filters.",
    "module": "Permissions",
    "concept": "Access Control"
  },
  {
    "question": "How does frappe.call work?",
    "answer": "It invokes server methods from client-side JavaScript.",
    "module": "Client",
    "concept": "RPC"
  },
  {
    "question": "What is a whitelisted function?",
    "answer": "A Python method allowed to be accessed via API or client scripts.",
    "module": "API",
    "concept": "Whitelisting"
  },
  {
    "question": "How to run code on form refresh?",
    "answer": "Use client-side event hooks inside frappe.ui.form.on().",
    "module": "Client",
    "concept": "Form Events"
  },
  {
    "question": "What is validate() used for?",
    "answer": "It performs field and document validations before saving.",
    "module": "Backend",
    "concept": "Validation"
  },
  {
    "question": "What is a scheduled job?",
    "answer": "A function executed automatically using Frappe’s scheduler.",
    "module": "Scheduler",
    "concept": "Cron Jobs"
  },
  {
    "question": "How to define a REST API endpoint?",
    "answer": "Use whitelisted functions accessible through /api/method/.",
    "module": "API",
    "concept": "REST"
  },
  {
    "question": "What is a Frappe App?",
    "answer": "A reusable package containing modules, doctypes, pages, and logic.",
    "module": "Core",
    "concept": "Application Structure"
  },
  {
    "question": "What is the use of hooks.py?",
    "answer": "It registers events, overrides, scripts, and background jobs.",
    "module": "Core",
    "concept": "Configuration"
  },
  {
    "question": "What is frappe.db.exists used for?",
    "answer": "It checks whether a specific record exists in the database.",
    "module": "Database",
    "concept": "Existence Check"
  },
  {
    "question": "What is the role of server scripts?",
    "answer": "They execute backend logic without modifying the actual codebase.",
    "module": "Server Scripts",
    "concept": "Customization"
  },
  {
    "question": "What is a Client Script?",
    "answer": "A JavaScript file customizing form behaviors on the client side.",
    "module": "Client",
    "concept": "UI Behavior"
  },
  {
    "question": "What is frappe.get_all used for?",
    "answer": "It retrieves multiple records with selected fields efficiently.",
    "module": "Database",
    "concept": "Bulk Query"
  },
  {
    "question": "What is an Event Hook?",
    "answer": "A trigger allowing custom logic before or after certain actions.",
    "module": "Hooks",
    "concept": "Event Handling"
  },
  {
    "question": "Why use before_save in Frappe?",
    "answer": "To apply logic immediately before a document is saved.",
    "module": "Backend",
    "concept": "Pre-save Logic"
  },
  {
    "question": "What is a Workspace in Frappe?",
    "answer": "A customizable dashboard grouping shortcuts, reports, and pages.",
    "module": "Desk",
    "concept": "UI Navigation"
  },
  {
    "question": "What is a Page in Frappe?",
    "answer": "A full custom screen built using HTML, JS, and Python.",
    "module": "Desk",
    "concept": "Custom Views"
  },
  {
    "question": "What is a Report in Frappe?",
    "answer": "A structured data view created using queries, scripts, or builders.",
    "module": "Reporting",
    "concept": "Data Visualization"
  },
  {
    "question": "What are Script Reports?",
    "answer": "Reports written using Python to produce dynamic result sets.",
    "module": "Reporting",
    "concept": "Script-Based Reporting"
  },
  {
    "question": "What is frappe.throw used for?",
    "answer": "It raises a user-facing error and stops execution.",
    "module": "Core",
    "concept": "Error Handling"
  },
  {
    "question": "What is a DocEvent?",
    "answer": "A lifecycle callback triggered on create, save, or submit.",
    "module": "Hooks",
    "concept": "Document Events"
  },
  {
    "question": "What is frappe.call.promise?",
    "answer": "A promise-based client-call method for cleaner async code.",
    "module": "Client",
    "concept": "Async Calls"
  },
  {
    "question": "What is frappe.model.set_value?",
    "answer": "It updates a field value dynamically on the client side.",
    "module": "Client",
    "concept": "Field Updates"
  },
  {
    "question": "Why use before_insert?",
    "answer": "To modify data right before a document is inserted.",
    "module": "Backend",
    "concept": "Pre-Insert Logic"
  },
  {
    "question": "What is a Notification in Frappe?",
    "answer": "An automated alert triggered based on document changes.",
    "module": "Notifications",
    "concept": "Alert System"
  },
  {
    "question": "What is frappe.ui.Dialog?",
    "answer": "A modal popup enabling custom input and actions in UI.",
    "module": "Client",
    "concept": "UI Components"
  },
  {
    "question": "What is the purpose of Custom Fields?",
    "answer": "They extend existing doctypes without modifying core code.",
    "module": "Customization",
    "concept": "Extendability"
  },
  {
    "question": "What is a Web Form in Frappe?",
    "answer": "A public-facing form allowing users to submit data without login.",
    "module": "Website",
    "concept": "Public Data Entry"
  },
  {
    "question": "What is a Portal Page?",
    "answer": "A customizable page shown to logged-in website users.",
    "module": "Website",
    "concept": "User Portal"
  },
  {
    "question": "What is the use of Frappe Cache?",
    "answer": "A fast in-memory store for temporary data and lookups.",
    "module": "Cache",
    "concept": "Caching"
  },
  {
    "question": "What is frappe.enqueue?",
    "answer": "It schedules a background task to run asynchronously.",
    "module": "Background Jobs",
    "concept": "Asynchronous Processing"
  },
  {
    "question": "What is a Workflow?",
    "answer": "A rule-based approval process controlling document states.",
    "module": "Workflow",
    "concept": "State Transitions"
  },
  {
    "question": "What is a Web Template?",
    "answer": "A reusable HTML template for website components.",
    "module": "Website",
    "concept": "Reusable UI"
  },
  {
    "question": "What is a Dashboard?",
    "answer": "A visual panel displaying reports, charts, and KPIs.",
    "module": "Reporting",
    "concept": "Visualization"
  },
  {
    "question": "What is the role of DocShare?",
    "answer": "It stores document-level sharing rules for users.",
    "module": "Permissions",
    "concept": "Document Sharing"
  },
  {
    "question": "What is Link Field?",
    "answer": "A field connecting one doctype to another via reference.",
    "module": "Forms",
    "concept": "Linked Data"
  },
  {
    "question": "What is frappe.get_list?",
    "answer": "A fast way to fetch filtered records with selected fields.",
    "module": "Database",
    "concept": "Optimized Query"
  },
  {
    "question": "What is a DocType Controller?",
    "answer": "A Python class that defines server-side logic for a doctype.",
    "module": "Backend",
    "concept": "Controller Logic"
  },
  {
    "question": "What is frappe.publish_realtime?",
    "answer": "It sends real-time updates to clients over websockets.",
    "module": "Real-time",
    "concept": "Live Updates"
  },
  {
    "question": "What are Child Tables?",
    "answer": "Sub-documents stored inside a parent document as rows.",
    "module": "Models",
    "concept": "Nested Data"
  },
  {
    "question": "Why use frappe.msgprint?",
    "answer": "To display informational messages to users on the UI.",
    "module": "Client",
    "concept": "User Notification"
  },
  {
    "question": "What is a Patch in Frappe?",
    "answer": "A script executed during migrate to fix or update data.",
    "module": "Patching",
    "concept": "Data Migration"
  },
  {
    "question": "What is frappe.new_doc?",
    "answer": "It creates a new document instance without inserting it.",
    "module": "Core",
    "concept": "Document Creation"
  },
  {
    "question": "What is a Print Format?",
    "answer": "A template defining how documents appear when printed.",
    "module": "Print",
    "concept": "Document Layout"
  },
  {
    "question": "What is frappe.render_template?",
    "answer": "It renders HTML using Jinja templates and context data.",
    "module": "Website",
    "concept": "Template Rendering"
  },
  {
    "question": "What is a List View Settings doctype?",
    "answer": "It customizes columns, filters, and appearance for list views.",
    "module": "Desk",
    "concept": "View Customization"
  },
  {
    "question": "What is frappe.get_single?",
    "answer": "It loads a singleton doctype that stores global settings.",
    "module": "Core",
    "concept": "Singleton Document"
  }
]

def insert_question():
    for row in data:
        frappe.get_doc({
            "doctype": "Question",
            "question": row["question"],
            "answer": row["answer"],
            "module": row["module"],
            "concept": row["concept"]
        }).insert(ignore_permissions=True)

    frappe.db.commit()

    return "50 Questions added successfully."