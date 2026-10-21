# Copyright (c) 2026, Guba Technology
# License: MIT

import frappe

from customized_forcommon.patches.v3.seed_procurement_masters import execute as seed_masters


def run():
	"""Seed the tender-management setup masters after every migrate (idempotent)."""
	if not frappe.db.exists("DocType", "Procurement Type"):
		return
	seed_masters()
	frappe.db.commit()
