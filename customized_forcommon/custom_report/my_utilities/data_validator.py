import frappe
import json
from customized_forcommon.custom_report.my_utilities.get_company_info import GetCompanyInfo
get_company_info = GetCompanyInfo()
@frappe.whitelist()
def validate_tax_type(taxes):
    accounts = json.loads(taxes)
    vat_receivable = get_company_info.get_vat_receivable_account()
    vat_payable = get_company_info.get_vat_payable_account()
    withholding_payable = get_company_info.get_withholding_payable_account()
    withholding_receivable = get_company_info.get_withholding_receivable_account()
    vat = False
    withhold = False
    vat_not_exist = False
    wh_not_exist = False
    for acc in accounts:
        if acc == vat_receivable or acc == vat_payable:
            vat = True
        elif acc == withholding_payable or acc == withholding_receivable:
            withhold = True
        elif "vat" in acc.lower():
            vat = True
            vat_not_exist = True
            # frappe.msgprint("<b style='color:red'>Unregistered VAT Account detected</b>. <br>Please enter a valid VAT Account. <br>otherwise, all the reports related to this invoice will show you wrong output. <br>or you may not get the desired outcome.")

        elif "withhold" in acc.lower() or "withholding" in acc.lower():
            withhold = True
            wh_not_exist = True
            # frappe.msgprint("<b style='color:red'>Unregistered Withholding Account detected</b>. <br>Please enter a valid withholding Account. <br>otherwise, all the reports related to this invoice will show you wrong output. <br>or you may not get the desired outcome.")

        
    return {
        "vat": vat,
        "withhold": withhold,
        "vat_not_exist": vat_not_exist,
        "wh_not_exist": wh_not_exist
    }

