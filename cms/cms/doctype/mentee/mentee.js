// Copyright (c) 2026, Praveenkumar Dhanasekar and contributors
// For license information, please see license.txt

frappe.ui.form.on("Mentee", {
	refresh(frm) {
        frappe.call({
            method:"cms.cms.doctype.question.question.get_mentor",
            callback: function(r){
                frm.set_query("mentor_id",function(){
                    return {
                        filters:{
                            name:['in',r.message]
                        }
                    }
                })
            }
        })

	},
});
