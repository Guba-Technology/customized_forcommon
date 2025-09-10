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

Before applying patches, remove any existing custom fields from the following doctypes: under the custom report module


- `Sales Invoice`
- `Purchase Invoice`
- `Employee`
- `Company`

### 🔧 Apply Patches
To run the bulk patcher, use the following command format: This program updates the listed doctypes whenever new custom fields are added. However, during migration, it won’t make any changes to those doctypes after the patches have already been applied
```bash

bench --site [your-site-name] execute customized_forcommon.patcher.execute
```
the command above will run the patch file `customized_forcommon/patches/v1/[patch_name].execute`

---
patche files are `employee_custom_fields.py`, `sales_invoice_custom_fields.py`, `purchase_invoice_custom_fields.py`, 

you can add more patch files in `customized_forcommon/patches/v1/` folder, to be executed together with `customized_forcommon.patcher.execute`
