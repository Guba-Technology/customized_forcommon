//public/js/training_program_custom.js
// Trigger for Training Program
frappe.ui.form.on('Training Program', {
    onload: function(frm) {
        if (frm.is_new() && frm.doc.custom_training_plan) {
            fetch_trainers(frm);
        }
    },
    custom_training_plan: function(frm) {
        if (frm.doc.custom_training_plan) {
            fetch_trainers(frm);
        } else {
            frm.set_value("trainer_name", "");
        }
    }
});

// Trigger for Training Event
frappe.ui.form.on('Training Event', {
    onload: function(frm) {
        if (frm.is_new() && frm.doc.training_program) {
            fetch_trainers(frm);
        }
    },
    training_program: function(frm) {
        if (frm.doc.training_program) {
            fetch_trainers(frm);
        } else {
            // Clear all trainer-related fields if program is removed
            frm.set_value({
                "trainer_name": "",
                "trainer_email": "",
                "trainer_contact_number": "",
                "trainer_supplier": ""
            });
        }
    }
});

function fetch_trainers(frm) {
    if (frm.doctype === "Training Program") {
        frappe.db.get_value("Training Plan", frm.doc.custom_training_plan, "trainer")
            .then(r => {
                if (r && r.message) {
                    frm.set_value("trainer_name", r.message.trainer);
                }
            });
    }

    if (frm.doctype === "Training Event") {
        console.log("Fetching details from Training Program:", frm.doc.training_program);
        
        const source_fields = ["trainer_name", "trainer_email", "contact_number", "supplier"];
        
        frappe.db.get_value("Training Program", frm.doc.training_program, source_fields)
            .then(r => {
                if (r && r.message) {
                    const msg = r.message;
                    
                    frm.set_value({
                        "trainer_name": msg.trainer_name,
                        "trainer_email": msg.trainer_email,
                        "contact_number": msg.contact_number,
                        "supplier": msg.supplier,
                        "location": msg.location
                    });
                }
            })
            .catch(err => {
                console.error("Error in Training Event fetch:", err);
            });
    }
}