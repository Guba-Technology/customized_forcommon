# 📊 Customized Forcommon – Tax Reporting Branch

Custom enhancements for ERP tax compliance and financial reporting.

---

## 🧾 Overview

This branch includes specialized reports and field-level customizations to support:

- Income Tax Reporting
- Sales & Purchase VAT Reports
- Pension Contribution Reports
- Withholding Tax Reports
- VAT Declaration Reports

These tools are designed to simplify regulatory reporting and improve fiscal data accuracy.

---

## ⚙️ Setup Instructions

Before applying patches, remove any existing custom fields from the following doctypes:

- `Sales Invoice`
- `Purchase Invoice`
- `Employee`
- `Company`

### 🔧 Apply Patches

Run each patch file using the following command format:

```bash
bench --site [your-site-name] execute customized_forcommon.patches.v1.[patch_name].execute
```
the command above will run the patch file `customized_forcommon/patches/v1/[patch_name].execute`

---
patche files are `employee_custom_fields.py`, `sales_invoice_custom_fields.py`, `purchase_invoice_custom_fields.py`, 