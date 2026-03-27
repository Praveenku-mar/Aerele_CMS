// Copyright (c) 2026, Praveenkumar Dhanasekar and contributors
// For license information, please see license.txt

frappe.ui.form.on("Daily Test", {
    refresh(frm) {
        // Run timer only once per form load
        if (!frm.exam_timer_started && frm.doc.docstatus != 1) {
            frm.exam_timer_started = true;
            start_exam_timer(frm);
        }
    }
});

let current_mode = null; // Track state changes

function start_exam_timer(frm) {
    if (!frm.doc.exam_start_time || !frm.doc.exam_end_time) return;

    // Create timer box UI
    let timer_id = "exam_timer_box";
    let timer_box = document.getElementById(timer_id);

    if (!timer_box) {
        timer_box = document.createElement("div");
        timer_box.id = timer_id;
        timer_box.style =
            "padding:10px; background:#f5f5f5; border-radius:6px; font-size:16px; font-weight:bold; margin-bottom:12px;";
        frm.$wrapper.find(".form-dashboard").prepend(timer_box);
    }

    function updateTimer() {
        let now = new Date();
        let start = new Date(frm.doc.exam_start_time);
        let end = new Date(frm.doc.exam_end_time);

        let new_mode;

        if (now < start) new_mode = "not_started";
        else if (now >= start && now <= end) new_mode = "running";
        else new_mode = "ended";

        // Only run lock/unlock when mode changes (prevents field refresh issues!)
        if (new_mode !== current_mode) {
            current_mode = new_mode;

            if (new_mode === "not_started") {
                lock_answers(frm);
                frm.disable_save();
            }
            else if (new_mode === "running") {
                unlock_answers(frm);
                frm.enable_save();
            }
            else {
                lock_answers(frm);
                frm.disable_save();
            }
        }

        update_timer_ui(new_mode, start, end, now, timer_id);
    }

    updateTimer();
    setInterval(updateTimer, 1000);
}

// ---------------- UI UPDATE ONLY (NO IMPACT ON ANSWER FIELD TYPING) ----------------
function update_timer_ui(mode, start, end, now, timer_id) {
    let box = document.getElementById(timer_id);
    if (!box) return;

    if (mode === "not_started") {
        box.innerHTML =
            "⏳ Exam starts in: <b>" + ms_to_time(start - now) + "</b>";
    }
    else if (mode === "running") {
        box.innerHTML =
            "🟢 Exam running — Time left: <b>" + ms_to_time(end - now) + "</b>";
    }
    else {
        box.innerHTML = "🔴 Exam Ended";
    }
}

// ---------------- LOCK / UNLOCK ONLY WHEN MODE CHANGES ----------------
function lock_answers(frm) {
    (frm.fields_dict["questions"].grid.grid_rows || []).forEach(row => {
        row.toggle_editable("answer", false);
    });
}

function unlock_answers(frm) {
    (frm.fields_dict["questions"].grid.grid_rows || []).forEach(row => {
        row.toggle_editable("answer", true);
    });
}

// ---------------- TIME FORMAT ----------------
function ms_to_time(ms) {
    let sec = Math.floor(ms / 1000);
    let m = Math.floor(sec / 60);
    let h = Math.floor(m / 60);
    return `${h}h ${m % 60}m ${sec % 60}s`;
}