from erpnext.stock.doctype.quality_inspection.quality_inspection import QualityInspection

import frappe

class CustomQualityInspection(QualityInspection):
    def validate(self):
        self.set_status_of_readings_table()
        super().validate()
     
    def set_status_of_readings_table(self):
        if self.readings:
            for row in self.readings:
                if (
                    row.custom_no_of_accepted_quantity is not None
                    and row.custom_no_of_rejected_quantity is not None
                    and row.custom_no_of_rework is not None
                ):
                    row.status = ""


