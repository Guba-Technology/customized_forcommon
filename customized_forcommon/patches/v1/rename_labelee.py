import frappe

def execute():
    """Add translations for Plant Floor -> Production Site"""
    
    # Get meta
    meta = frappe.get_meta("Workstation Type")
    
    # Loop through fields to find section breaks
    for field in meta.fields:
        if field.fieldtype == "Section Break" and field.fieldname == "over_heads":
            frappe.db.set_value("DocField", field.name, "hidden", 1)
            break
    
    frappe.clear_cache()
    print("✅ Over Heads section hidden successfully")

    translations = [
        # Main translation
        {"source_text": "Plant Floor","translated_text": "Production Site","language": "en"},
        # Common UI strings
        {"source_text": "Plant Floor List","translated_text": "Production Site List","language": "en"},
        {"source_text": "Add Plant Floor","translated_text": "Add Production Site","language": "en"},
        {"source_text": "New Plant Floor","translated_text": "New Production Site", "language": "en"},
        {"source_text": "Plant Floor Details","translated_text": "Production Site Details","language": "en"},
        {"source_text": "Edit Plant Floor","translated_text": "Edit Production Site","language": "en"},
        {"source_text": "View Plant Floor","translated_text": "View Production Site","language": "en"},
        {"source_text": "Workstation Type", "translated_text": "Production Line", "language": "en"},
        {"source_text": "Workstation Type List", "translated_text": "Production Line List", "language": "en"},
        {"source_text": "New Workstation Type", "translated_text": "New Production Line", "language": "en"},
    ]
    
    for trans in translations:
        # Remove existing if any
        frappe.db.delete("Translation", {
            "source_text": trans["source_text"],
            "language": trans["language"]
        })
        
        # Add new translation
        try:
            doc = frappe.new_doc("Translation")
            doc.update(trans)
            doc.insert(ignore_permissions=True)
        except Exception as e:
            print(f"⚠️ Error adding {trans['source_text']}: {e}")

        
    
    frappe.db.commit()
    frappe.clear_cache()
    print("✅ All translations added successfully")