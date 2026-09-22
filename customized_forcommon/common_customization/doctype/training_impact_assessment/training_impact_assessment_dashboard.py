# Copyright (c) 2026, Guba Technology
# License: MIT

from frappe import _


def get_data():
	return {
		"fieldname": "training_impact_assessment",
		"transactions": [
			{"label": _("Responses"), "items": ["Training Assessment Response"]},
			{"label": _("Report"), "items": ["Training Impact Assessment Report"]},
		],
	}
