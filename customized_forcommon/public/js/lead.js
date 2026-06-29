frappe.ui.form.on('Lead', {
    refresh(frm) {
        const fields = [
            "first_name",
            "middle_name",
            "last_name",
            "job_title",
            "gender",
            "source"
        ];

        fields.forEach(field => {
            const value = frm.doc[field];

            // If value already exists → make field read-only
            if (value) {
                frm.set_df_property(field, "read_only", 1);
            } else {
                // If empty → allow editing
                frm.set_df_property(field, "read_only", 0);
            }
        });
    },

    before_save(frm) {
        const fields = [
            "first_name",
            "middle_name",
            "last_name",
            "job_title",
            "gender",
            "source"
        ];

        // Optional extra protection: prevent clearing after set
        fields.forEach(field => {
            if (frm.doc.__unsaved && frm.doc.__original && frm.doc.__original[field]) {
                frm.doc[field] = frm.doc.__original[field];
            }
        });
    }
});