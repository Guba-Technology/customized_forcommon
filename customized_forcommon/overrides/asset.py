import frappe
from erpnext.assets.doctype.asset.asset import Asset as ERPNextAsset

class Asset(ERPNextAsset):

    def get_indicator(self):
        # Custom indicator
        if self.status == "Borrowed":
            return ("Borrowed", "orange", "status,=,Borrowed")

        # Default ERPNext behavior
        return super().get_indicator()
