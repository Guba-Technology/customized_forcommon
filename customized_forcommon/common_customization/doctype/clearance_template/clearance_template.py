# Copyright (c) 2025, Guba Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
import re


class ClearanceTemplate(Document):
	def validate(self):
		self.validate_no_duplicate()
		self.validate_last_row()

	def validate_no_duplicate(self):
		if self.clearance_template_table:
			# Check for duplicate entries in the clearance_template_table
			unique_entries = set()
			for entry in self.clearance_template_table:
				if entry.department in unique_entries:
					frappe.throw(
						_("Duplicate department {0} found in clearance template table.").format(entry.department)
					)
				unique_entries.add(entry.department)

	

	# Validate that the last row in the clearance template table has a specific department
	def validate_last_row(self):
		accepted_depts = [
			"የሰው ሀብት ስራ አመራር መምሪያ",
			"የሰው ሀብት አመራርና ልማት መምሪያ",
			"የሰው ሀይል አስተዳደርና ልማት መምሪያ",
			"የሰው ሀብት ልማት አስተዳደር መምሪያ",
			"የሰው ሀብት አመራርና ልማት መምሪያ ኃላፊ"
		]

		if not self.clearance_template_table or len(self.clearance_template_table) < 2:
			frappe.throw(_("The clearance template table must have at least two rows."))

		last_row = self.clearance_template_table[-1]
		normalized_last = normalize_text(last_row.department)

		# Normalize all accepted depts for comparison
		normalized_accepted = [normalize_text(dept) for dept in accepted_depts]

		if normalized_last not in normalized_accepted:
			frappe.throw(
				_("The last row in the clearance template table must be one of the approved human resource departments.")
			)


# Normalize text by removing spaces and replacing commonly confused characters
def normalize_text(text):
	if not text:
		return ""

	# Normalize spacing
	text = re.sub(r'\s+', '', text)

	# Replace commonly confused characters
	replacements = {
		'ሐ': 'ሀ',
		'ሑ': 'ሀ',
		'ሒ': 'ሀ',
		'ሓ': 'ሀ',
		'ሔ': 'ሀ',
		'ሕ': 'ሀ',
		'ሖ': 'ሀ',
		'ኀ': 'ሀ',
		'ኁ': 'ሀ',
		'ኂ': 'ሀ',
		'ኃ': 'ሀ',
		'ኄ': 'ሀ',
		'ኅ': 'ሀ',
		'ኆ': 'ሀ',
		'ሰ': 'ሠ',
		'ሱ': 'ሠ',
		'ሲ': 'ሠ',
		'ሳ': 'ሠ',
		'ሴ': 'ሠ',
		'ስ': 'ሠ',
		'ሶ': 'ሠ',
		'ጸ': 'ፀ',
		'ጹ': 'ፀ',
		'ጺ': 'ፀ',
		'ጻ': 'ፀ',
		'ጼ': 'ፀ',
		'ጽ': 'ፀ',
		'ጾ': 'ፀ',
	}


	for old, new in replacements.items():
		text = text.replace(old, new)

	return text