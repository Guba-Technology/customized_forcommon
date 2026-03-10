frappe.ui.form.on("Asset Movement", {
    setup: (frm) => {
        // Standard Queries
        frm.set_query("to_employee", "assets", (doc) => {
            return { filters: { company: doc.company } };
        });
        frm.set_query("from_employee", "assets", (doc) => {
            return { filters: { company: doc.company } };
        });
    },

   

    onload: (frm) => {
        frm.trigger("set_required_fields");
    },

    purpose: (frm) => {
        frm.trigger("set_required_fields");
    },

    set_required_fields: (frm, cdt, cdn) => {
		let fieldnames_to_be_altered;
		if (frm.doc.purpose === "Transfer To Employee") {
			fieldnames_to_be_altered = {
				target_location: { read_only: 1, reqd: 0 },
				source_location: { read_only: 1, reqd: 0 },
				from_employee: { read_only: 1, reqd: 0 },
				to_employee: { read_only: 0, reqd: 1 },
			};
        }
        if (frm.doc.purpose === "Receipt") {
            fieldnames_to_be_altered = {
                target_location: { read_only: 0, reqd: 1 },
                source_location: { read_only: 0, reqd: 0 },
                from_employee: { read_only: 0, reqd: 0 },
                to_employee: { read_only: 1, reqd: 0 },
            };
        }

        if (fieldnames_to_be_altered) {
            Object.keys(fieldnames_to_be_altered).forEach((fieldname) => {
                let properties = fieldnames_to_be_altered[fieldname];
                Object.keys(properties).forEach((property) => {
                    frm.fields_dict["assets"].grid.update_docfield_property(fieldname, property, properties[property]);
                });
            });
            frm.refresh_field("assets");
        }
    },
});