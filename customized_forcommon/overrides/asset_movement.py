import frappe
from frappe import _
from erpnext.assets.doctype.asset_movement.asset_movement import AssetMovement
from erpnext.assets.doctype.asset_activity.asset_activity import add_asset_activity

class CustomAssetMovement(AssetMovement):
    def validate(self):
        super().validate()
        
        # Pull all asset IDs to fetch their conditions in a single bulk query
        asset_ids = [item.asset for item in self.assets if item.asset]
        asset_conditions = {}
        if asset_ids:
            asset_conditions = dict(
                frappe.get_all("Asset", filters={"name": ["in", asset_ids]}, fields=["name", "custom_asset_condition"], as_list=1)
            )

        for item in self.assets:
            db_condition = asset_conditions.get(item.asset)
            
            # If item condition is empty, set default from Asset Doctype
            if not item.custom_asset_condition:
                item.custom_asset_condition = db_condition
            else:
                if item.custom_asset_condition != db_condition:
                    frappe.msgprint(_("Asset {0} has a different condition in Asset Movement Item ({1}) than in Asset doctype ({2}).").format(
                        item.asset, item.custom_asset_condition, db_condition
                    ))
            
            # Validation for Transfer To Employee
            if self.purpose == "Transfer To Employee" and item.from_employee == item.to_employee:
                frappe.throw(_("From Employee and To Employee cannot be the same for Asset {0}").format(item.asset))
                
            # Validation for Issuance
            if self.purpose in ["Issue", "Transfer and Issue"]:
                self.check_if_can_be_issued(item.asset)
                
                
    def validate_movement(self, d):
        if self.purpose == "Transfer and Issue":
            self.validate_location_and_employee(d)
        elif self.purpose in ["Receipt", "Transfer", "Return"]:
            self.validate_location(d)
        else:
            self.validate_employee(d)
    
    def validate_location_and_employee(self, d):
        self.validate_location(d)
        self.validate_employee(d)
    def validate_location(self, d):
        if self.purpose in ["Transfer", "Transfer and Issue"]:
            current_location = frappe.db.get_value("Asset", d.asset, "location")
            if d.source_location:
                if current_location != d.source_location:
                    frappe.throw(
						_("Asset {0} does not belong to the location {1}").format(d.asset, d.source_location)
					)
            else:
                d.source_location = current_location
            if not d.target_location:
                frappe.throw(_("Target Location is required for transferring Asset {0}").format(d.asset))
            if d.source_location == d.target_location:
                frappe.throw(_("Source and Target Location cannot be same"))
        if self.purpose == "Receipt":
            if not d.target_location:
                frappe.throw(_("Target Location is required while receiving Asset {0}").format(d.asset))
            if d.to_employee and frappe.db.get_value("Employee", d.to_employee, "company") != self.company:
                frappe.throw(
					_("Employee {0} does not belong to the company {1}").format(d.to_employee, self.company)
				)
        if self.purpose == "Return":
            if not d.target_location:
                frappe.throw(_("Target Location is required while returning Asset {0}").format(d.asset))
            if d.from_employee and frappe.db.get_value("Employee", d.from_employee, "company") != self.company:
                frappe.throw(
                    _("Employee {0} does not belong to the company {1}").format(d.from_employee, self.company)
                )
    def validate_employee(self, d):
        if self.purpose == "Transfer and Issue":
            if not d.from_employee:
                frappe.throw(_("From Employee is required while issuing Asset {0}").format(d.asset))
            if d.from_employee:
                current_custodian = frappe.db.get_value("Asset", d.asset, "custodian")
            if current_custodian != d.from_employee:
                frappe.throw(
					_("Asset {0} does not belong to the custodian {1}").format(d.asset, d.from_employee)
				)
        if not d.to_employee:
            frappe.throw(_("Employee is required while issuing Asset {0}").format(d.asset))
        if d.to_employee and frappe.db.get_value("Employee", d.to_employee, "company") != self.company:
            frappe.throw(
				_("Employee {0} does not belong to the company {1}").format(d.to_employee, self.company)
			)
        if self.purpose == "Return":
            if not d.from_employee:
                frappe.throw(_("From Employee is required while returning Asset {0}").format(d.asset))
            if d.from_employee and frappe.db.get_value("Employee", d.from_employee, "company") != self.company:
                frappe.throw(
                    _("Employee {0} does not belong to the company {1}").format(d.from_employee, self.company)
                )
    
    def on_submit(self):
        super().on_submit()
        for item in self.assets:
            previous_condition = frappe.db.get_value("Asset", item.asset, "custom_asset_condition")
            
            if item.custom_asset_condition and previous_condition != item.custom_asset_condition:
                # Update the asset condition in the Asset doctype
                frappe.db.set_value("Asset", item.asset, "custom_asset_condition", item.custom_asset_condition)
                
                # Log activity regardless of employee presence
                self.log_asset_condition(item.asset, previous_condition, item.custom_asset_condition)
                
    def log_asset_condition(self, asset_id, previous_condition, custom_asset_condition):
        add_asset_activity(asset_id, _("Asset condition updated from {0} to {1}").format(previous_condition, custom_asset_condition))

    def check_if_can_be_issued(self, asset_id):
        # Crucial bugfix: added p.docstatus = 1 to ensure we only look at submitted records
        movements = frappe.db.sql("""
            SELECT p.purpose 
            FROM `tabAsset Movement Item` i
            JOIN `tabAsset Movement` p ON i.parent = p.name
            WHERE i.asset = %s 
            AND i.parent != %s 
            AND p.docstatus = 1
        """, (asset_id, self.name), as_dict=True)

        issued_count = 0
        receipt_count = 0

        for m in movements:
            if m.purpose in ["Issue", "Transfer and Issue"]:
                issued_count += 1
            elif m.purpose == "Receipt":
                receipt_count += 1

        if issued_count > receipt_count:
            # Bugfix: Added {1} and {2} back to the error message string
            frappe.throw(_(
                "Asset {0} is currently Issued (Issued: {1}, Received: {2}). "
                "Please submit a 'Receipt' before issuing again."
            ).format(asset_id, issued_count, receipt_count))
            
        return True