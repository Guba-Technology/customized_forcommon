#doc_events/employee_referal.py
import frappe

def handle_referral_fields(doc, method=None):
    """
    Dynamically toggles the 'mandatory' status based on the outsider checkbox.
    """
    target_fields = ["referrer"]
    if doc.get("custom_is_referrer_outsider_employee"):
        for field in doc.meta.fields:
            if field.fieldname in target_fields:
                field.reqd = 0
    else:
        for field in doc.meta.fields:
            if field.fieldname in target_fields:
                field.reqd = 1