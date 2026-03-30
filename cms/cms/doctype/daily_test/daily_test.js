// Copyright (c) 2026, Praveenkumar Dhanasekar and contributors
// For license information, please see license.txt

frappe.ui.form.on("Daily Test", {
    onload(frm) {
        if (frappe.user.has_role("Mentee")){
            frm.add_custom_button(("Request"), () =>{
                frappe.prompt(
                    [
                        {
                            fieldname:"request_time",
                            fieldtype:"Datetime",
                            label:"Request Date Time",
                            reqd:1
                        }
                    ],
                    function(data){
                        frappe.confirm(`Are you sure you want to extend exam time ${data.request_time} ?`,
                            () => {
                                frappe.call({
                                    method:"cms.cms.doctype.request.request.request_time",
                                    args:{
                                        date:data.request_time,
                                        exam_id : frm.doc.name,
                                        mentee_id : frm.doc.mentee_id
                                    },
                                    callback: function(r){
                                        if(!r.exc){
                                            frape.msgprint({
                                                title:"Success",
                                                message:"Your request is submitted.",
                                                indicator:"green"
                                            });
                                        }}
                                })
                            }
                        );
                    }
                );
            })
        frappe.call({
            method: "cms.cms.doctype.daily_test.daily_test.get_or_set_session_start",
            args: { docname: frm.doc.name },
            callback(r) {
                let res = r.message;
                if (res.status === "not_started") {
                    hide_questions(frm);
                    setup_timer_box(frm)
                    show_msg("⏳ Exam not started",frm);
                    return;
                }

                if (res.status === "ended") {
                    setup_timer_box(frm)
                    show_msg("🔴 Exam ended",frm);
                    return;
                }

                // Running state
                let session_start = new Date(res.session_start_time);
                start_timer(frm, session_start);
            }
        });
    }
}
});

function start_timer(frm, session_start) {
    let timer_box = setup_timer_box(frm);

    function tick() {
        let now = new Date();
        let elapsed = now - session_start;
        let remaining = (60 * 60 * 1000) - elapsed;

        if (remaining <= 0) {
            frm.set_value("is_submited",1)
            auto_submit(frm);
        }

        show_questions(frm);
        timer_box.innerHTML = "🟢 Time left: <b>" + ms_to_time(remaining) + "</b>";
    }
    if (remaining != 0){
    tick();
    setInterval(tick, 1000);
    }
}

function auto_submit(frm) {
    frappe.msgprint("⏱ Time is over. Auto-submitting.");
    frm.save("Submit");
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
    return box;
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

function show_msg(txt) {
    let id = "exam_timer_box";
    let box = document.getElementById(id);
    box.innerHTML = txt
}

function ms_to_time(ms) {
    let s = Math.floor(ms / 1000);
    return `${Math.floor(s/3600)}h ${Math.floor((s%3600)/60)}m ${s%60}s`;
}