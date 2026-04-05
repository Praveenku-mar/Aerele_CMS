// Copyright (c) 2026, Praveenkumar Dhanasekar and contributors
// For license information, please see license.txt

frappe.ui.form.on("Daily Test", {
    refresh(frm){
        let now = new Date();
        if (frappe.user.has_role("Mentee")) {
            add_request_button(frm);
            hide_questions(frm)
            if(frm.doc.start === 0 && frm.doc.exam_end_time > now)
            {
                frm.add_custom_button(("Start Test"), ()=>{
                    show_questions(frm)
                    frappe.confirm("The exam is alive only 60 mins, after they exam is auto submit.",
                        () =>{
                            frappe.call({
                                method: "cms.cms.doctype.daily_test.daily_test.get_or_set_session_start",
                                args: { docname: frm.doc.name },
                                callback(r) {
                                    let res = r.message;
                                    exam_timer(frm,res)
                            }
                        });
                    })
                })
            }
            else{
                frappe.call({
                    method: "cms.cms.doctype.daily_test.daily_test.get_or_set_session_start",
                    args: { docname: frm.doc.name },
                    callback(r) {
                        let res = r.message;
                        exam_timer(frm,res)
                    }
                });
            }

        }
    }
});
let exam_interval = null;

function init_exam_timer(frm, session_start) {
    if (exam_interval) clearInterval(exam_interval);

    update_timer(frm, session_start); 

    exam_interval = setInterval(() => {
        update_timer(frm, session_start);
    }, 1000);
}

function update_timer(frm, session_start) {
    if (frm.doc.docstatus == 1) {
        show_msg("🔴 Exam ended");
        clearInterval(exam_interval);
        return;
    }

    let now = new Date();
    let elapsed = now - session_start;
    let remaining = (60 * 60 * 1000) - elapsed;

    if (remaining <= 0) {
        clearInterval(exam_interval);
        frm.set_value("is_submited", 1);
        auto_submit(frm);
        return;
    }
    show_msg("🟢 Time left: <b>" + ms_to_time(remaining) + "</b>");
}
function auto_submit(frm) {
    frappe.msgprint("⏱ Time is over. Auto-submitting.");
    frm.save("Submit");
}
function add_request_button(frm) {
    console.log("Custom button")
    frm.add_custom_button(("Request"), () => {
        frappe.prompt(
            [{
                fieldname: "request_time",
                fieldtype: "Datetime",
                label: "Request Date Time",
                reqd: 1
            },
            {
                fieldname: "reason",
                fieldtype:"Data",
                label:"Reason",
                reqd:1
            }
        ],
            function (data) {
                frappe.confirm(
                    `Extend exam time to ${data.request_time}?`,
                    () => {
                        frappe.call({
                            method: "cms.cms.doctype.request.request.request_time",
                            args: {
                                date: data.request_time,
                                exam_id: frm.doc.name,
                                mentee_id: frm.doc.mentee_id,
                                reason: data.reason
                            },
                            callback() {
                                frappe.msgprint({
                                    title: "Success",
                                    message: "Your request is submitted.",
                                    indicator: "green"
                                });
                            }
                        });
                    }
                );
            }
        );
    });
}

function exam_timer(frm,res){
    setup_timer_box(frm);
                            
    if (res.status === "not_started") {
        hide_questions(frm);
        show_msg("⏳ Exam not started");
        return;
    }

    if (res.status === "ended") {
        show_msg("🔴 Exam ended");
        return;
    }

    show_questions(frm); 
    let session_start = new Date(res.session_start_time);
    init_exam_timer(frm, session_start);
}

function setup_timer_box(frm) {
    let id = "exam_timer_box";
    let box = document.getElementById(id);

    if (!box) {
        box = document.createElement("div");
        box.id = id;
        box.style =
            "padding:10px;background:#f5f5f5;border-radius:6px;font-size:16px;font-weight:bold;margin-bottom:12px;";
        frm.$wrapper.find(".form-dashboard").prepend(box);
    }
}

function show_msg(txt) {
    let box = document.getElementById("exam_timer_box");
    if (box) box.innerHTML = txt;
}

function hide_questions(frm) {
    frm.fields_dict["questions"].grid.grid_rows.forEach(row => {
        row.wrapper.hide();
        row.toggle_editable("answer", false);
    });
}

function show_questions(frm) {
    frm.fields_dict["questions"].grid.grid_rows.forEach(row => {
        row.wrapper.show();
        row.toggle_editable("answer", true);
    });
}

function ms_to_time(ms) {
    let s = Math.floor(ms / 1000);
    return `${Math.floor(s / 3600)}h ${Math.floor((s % 3600) / 60)}m ${s % 60}s`;
}