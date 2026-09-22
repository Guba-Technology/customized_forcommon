# Copyright (c) 2026, Guba Technology
# License: MIT
#
# NOTE: Frappe does not reliably call child-table controller hooks (validate,
# etc.) on every save path across versions, so the authoritative 1-5 range
# check for before_training/after_training lives in the parent controller
# (Training Assessment Response.validate -> validate_score_ranges). This class
# is kept as a normal Document subclass for consistency / future use.

from frappe.model.document import Document


class TrainingAssessmentResponseCriteria(Document):
	pass
