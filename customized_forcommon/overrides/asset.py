import frappe
from frappe import _
from erpnext.assets.doctype.asset.asset import Asset
from frappe.utils import cint, flt
from erpnext.assets.doctype.asset_activity.asset_activity import add_asset_activity

class CustomAsset(Asset):  
   

    def update_existing_asset(self, remaining_qty, new_asset_names):
        """
        Updates the parent asset with reduced values proportional to remaining quantity.
        """
        # Calculate ratio before changing the asset quantity
        ratio = flt(remaining_qty) / flt(self.asset_quantity)
        
        self.asset_quantity = remaining_qty
        self.gross_purchase_amount = flt(self.gross_purchase_amount * ratio)
        if self.purchase_amount:
            self.purchase_amount = flt(self.purchase_amount * ratio)
            
        self.opening_accumulated_depreciation = flt(self.opening_accumulated_depreciation * ratio)
        self.value_after_depreciation = flt(self.value_after_depreciation * ratio, self.precision("gross_purchase_amount"))

        for row in self.get("finance_books"):
            row.value_after_depreciation = flt(row.value_after_depreciation * ratio)
            row.expected_value_after_useful_life = flt(row.expected_value_after_useful_life * ratio)

        # Bypass restrictions since parent asset is already submitted (docstatus=1)
        self.flags.ignore_validate_update_after_submit = True
        self.save()
        
        add_asset_activity(
            self.name,
            _("Asset split up. Quantities adjusted. Created draft records: {0}").format(new_asset_names),
        )


def create_new_asset_after_split(asset, split_qty):
    """
    Standalone helper function to initialize, scale values, 
    and save the new asset safely in 'Draft' status.
    """
    new_asset = frappe.copy_doc(asset)
    
    # Calculate reduction ratio based on current iteration quantity allocation
    ratio = flt(split_qty) / flt(asset.asset_quantity)
    
    new_gross_purchase_amount = flt(asset.gross_purchase_amount * ratio)
    opening_accumulated_depreciation = flt(asset.opening_accumulated_depreciation * ratio)

    new_asset.gross_purchase_amount = new_gross_purchase_amount
    if asset.purchase_amount:
        new_asset.purchase_amount = new_gross_purchase_amount
        
    new_asset.opening_accumulated_depreciation = opening_accumulated_depreciation
    new_asset.asset_quantity = split_qty
    new_asset.split_from = asset.name
    new_asset.value_after_depreciation = flt(
        asset.value_after_depreciation * ratio,
        asset.precision("gross_purchase_amount"),
    )

    for row in new_asset.get("finance_books"):
        row.value_after_depreciation = flt(row.value_after_depreciation * ratio)
        row.expected_value_after_useful_life = flt(row.expected_value_after_useful_life * ratio)

    # CRITICAL: Force the document status back to Draft before insertion
    new_asset.docstatus = 0
    new_asset.insert()
    
    # Setup standard activity history log
    add_asset_activity(
        new_asset.name,
        _("Asset created from split of {0}. Quantity: {1}").format(asset.name, split_qty),
    )

    return new_asset

@frappe.whitelist()
def split_asset(asset_name, split_qty,split_type="Individual"):
    """
    Overridden split_asset method handling:
    1. Draft status preservation.
    2. Grouped vs Individual record splitting strategy.
    """
    # 'self' already represents the asset instance if called on a document object
    
    split_qty = cint(split_qty)

    asset = frappe.get_doc("Asset", asset_name)
    if split_qty >= asset.asset_quantity:
        frappe.throw(_("Split qty cannot be greater than or equal to asset qty"))
        
    if split_qty <= 0:
        frappe.throw(_("Split qty must be greater than 0"))

    remaining_qty = asset.asset_quantity - split_qty
    new_assets_created = []

    if split_type == "Individual":
        # Loop N times creating individual asset records with a quantity of 1
        for i in range(split_qty):
            new_asset = create_new_asset_after_split(asset, 1)
            new_assets_created.append(new_asset.name)
    else:
        # Grouped behavior: single new asset holding the entire split quantity
        new_asset = create_new_asset_after_split(asset, split_qty)
        new_assets_created.append(new_asset.name)

    # Update the original parent asset balance
    linked_names = ", ".join(new_assets_created)
    asset.update_existing_asset(remaining_qty, linked_names)

    return new_assets_created