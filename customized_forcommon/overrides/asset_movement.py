import frappe
from frappe import _
from erpnext.assets.doctype.asset_movement.asset_movement import AssetMovement

class CustomAssetMovement(AssetMovement):
    def validate(self):
        super().validate()
        if self.purpose == "Transfer To Employee":
            for ii in self.assets:
                if ii.from_employee == ii.to_employee:
                    frappe.throw(_("From Employee and To Employee cannot be the same for Asset {0}").format(ii.asset))
        if self.purpose in ["Issue", "Transfer and Issue"]:
            for item in self.assets:
                self.check_if_can_be_issued(item.asset)
        

    def check_if_can_be_issued(self, asset_id):
        movements = frappe.db.sql("""
            SELECT p.purpose 
            FROM `tabAsset Movement Item` i
            JOIN `tabAsset Movement` p ON i.parent = p.name
            WHERE i.asset = %s 
            AND i.parent != %s 
        """, (asset_id, self.name), as_dict=True)

        issued_count = 0
        receipt_count = 0

        for m in movements:
            if m.purpose in ["Issue", "Transfer and Issue"]:
                issued_count += 1
            elif m.purpose == "Receipt":
                receipt_count += 1

        if issued_count > receipt_count:
            frappe.throw(_(
                "Asset {0} is currently Issued. "
                "Please submit a 'Receipt' before issuing again."
            ).format(asset_id, issued_count, receipt_count))
            
        return True