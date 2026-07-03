import frappe
from frappe import _
from erpnext.assets.doctype.asset_movement.asset_movement import AssetMovement
from erpnext.assets.doctype.asset_activity.asset_activity import add_asset_activity

class CustomAssetMovement(AssetMovement):
    def validate(self):
        super().validate()
        # get asset condition from Asset doctype and compare with the condition in Asset Movement Item table as default value
        for item in self.assets:
            if not item.custom_asset_condition:
                asset_condition = frappe.db.get_value("Asset", item.asset, "custom_asset_condition")
                item.custom_asset_condition = asset_condition
            else:
                asset_condition = frappe.db.get_value("Asset", item.asset, "custom_asset_condition")
                if item.custom_asset_condition != asset_condition:
                    frappe.warning(_("Asset {0} has a different condition in Asset Movement Item ({1}) than in Asset doctype ({2}).").format(item.asset, item.custom_asset_condition, asset_condition))
           
        if self.purpose == "Transfer To Employee":
            for ii in self.assets:
                if ii.from_employee == ii.to_employee:
                    frappe.throw(_("From Employee and To Employee cannot be the same for Asset {0}").format(ii.asset))
        if self.purpose in ["Issue", "Transfer and Issue"]:
            for item in self.assets:
                self.check_if_can_be_issued(item.asset)
    
    def on_submit(self):
        super().on_submit()
        for item in self.assets:
            previous_condition = frappe.db.get_value("Asset", item.asset, "custom_asset_condition")
            if item.custom_asset_condition and previous_condition != item.custom_asset_condition:
                # update the asset condition in the Asset doctype
                frappe.db.set_value("Asset", item.asset, "custom_asset_condition", item.custom_asset_condition)
                # log the asset condition change in the Asset Activity doctype
                if item.from_employee:
                    self.log_asset_condition(item.asset, previous_condition, item.custom_asset_condition)
            
                
    def log_asset_condition(self, asset_id, previous_condition, custom_asset_condition):
        add_asset_activity(asset_id, _("Asset condition updated from {0} to {1}").format(previous_condition, custom_asset_condition))

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