# custom_purchase_analytics.py
from erpnext.selling.report.sales_analytics.sales_analytics import Analytics
import frappe

class CustomPurchaseAnalytics(Analytics):
    def __init__(self, filters=None):
        self.filters = frappe._dict(filters or {})
        
    def run(self, args=None):
        # Get the base data
        data = super().run(args)
        
        # If based_on is Purchase Order and custom_purchase_type filter is applied
        if self.filters.based_on == "Purchase Order" and self.filters.get("custom_purchase_type"):
            # Post-process the data to filter by custom_purchase_type
            # This depends on how you want to filter
            filtered_data = []
            for row in data[0]:  # data is usually [data, columns, message, chart]
                # Add your filtering logic here
                # This is tricky because the data might be aggregated
                pass
        
        return data

def execute(filters=None):
    # Create a custom filters object
    custom_filters = frappe._dict(filters or {})
    
    # If custom_purchase_type is set, we need to modify the query
    if custom_filters.get("custom_purchase_type") and custom_filters.based_on == "Purchase Order":
        # You might need to set a flag or modify the filters
        pass
    
    return CustomPurchaseAnalytics(custom_filters).run()