import frappe

def run_patch(patch_path):
    try:
        module_path, function_name = patch_path.rsplit('.', 1)
        patch_module = __import__(module_path, fromlist=[function_name])
        getattr(patch_module, function_name)()
        #print(f"✅ Executed patch: {patch_path}")
    except Exception as e:
        print(f"❌ Failed to execute patch: {patch_path}")
        print(f"Error: {e}")

def execute():
    patches = [
        "customized_forcommon.patches.v1.employee_custom_fields.execute",
        "customized_forcommon.patches.v1.sales_invoice_custom_fields.execute",
        "customized_forcommon.patches.v1.purchase_invoice_custom_fields.execute",
        "customized_forcommon.patches.v1.company_custom_fields.execute"
        #you can add more patches here from the V2 folder also
        #you don't need to change anything else, or make new migrations. only the patches will be executed
        #no need to create new versions for every updates done in different doctypes
    ]

    for patch in patches:
        run_patch(patch)
