from erpnext.stock.doctype.stock_entry.stock_entry_dashboard import get_data as get_standard_data

def get_data(data=None):
    standard_data = get_standard_data()
    standard_data["non_standard_fieldnames"].update({
        "Material Receipt for Transfer": "reference_document"
    })
    found = False
    for section in standard_data["transactions"]:
        if section["label"] == "Reference":
            if "Material Receipt for Transfer" not in section["items"]:
                section["items"].append("Material Receipt for Transfer")
            found = True
            
    return standard_data