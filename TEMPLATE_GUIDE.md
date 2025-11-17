# Template Filling Guide

This guide explains how to use the sample JSON templates for filling DOCX templates and PDF forms.

## Files Created

1. **sample_template_data.json** - For DOCX template filling
2. **sample_form_data.json** - For PDF form autofilling

---

## 1. DOCX Template Filling

### Sample Template: `sample_template_data.json`

This template is used with the `template-fill` command to fill DOCX documents.

### How DOCX Templates Work

In your DOCX file, use `{{placeholder}}` syntax where you want data inserted:

**Example DOCX content:**
```
Invoice

Customer Name: {{name}}
Email: {{email}}
Phone: {{phone}}
Address: {{address}}, {{city}}, {{state}} {{zip}}

Invoice Number: {{invoice_number}}
Date: {{date}}

Company: {{company}}
Position: {{position}}

Amount Due: {{amount}}

Notes: {{notes}}

Signature: ____________________
           {{signature}}
Date: {{signature_date}}
```

### Usage

**CLI:**
```bash
# Fill DOCX template
python pdf_toolkit.py template-fill template.docx -o output.docx -d sample_template_data.json

# Fill DOCX and convert to PDF
python pdf_toolkit.py template-fill template.docx -o output.pdf -d sample_template_data.json --to-pdf

# Override specific values
python pdf_toolkit.py template-fill template.docx -o output.docx -d sample_template_data.json -v name="Jane Smith" -v date="2025-02-01"
```

**Click CLI:**
```bash
python cli.py fill-template --template template.docx --output output.docx --data-file sample_template_data.json
```

**GUI:**
1. Click "Template Fill" in sidebar
2. Select your DOCX template
3. Browse to select `sample_template_data.json`
4. Click "Fill Template"

### Customizing the Template

Edit `sample_template_data.json` to match your needs:

```json
{
  "name": "Your Name Here",
  "email": "your.email@example.com",
  "date": "2025-01-15",
  "amount": "$500.00"
}
```

Then in your DOCX, use:
- `{{name}}`
- `{{email}}`
- `{{date}}`
- `{{amount}}`

---

## 2. PDF Form Autofilling

### Sample Template: `sample_form_data.json`

This template is used with the `autofill` command to fill interactive PDF forms.

### How PDF Forms Work

PDF forms have predefined field names. You must use the **exact field name** from the PDF.

### Finding Field Names

**First, list all available fields in your PDF:**

```bash
python pdf_toolkit.py autofill form.pdf --list-fields
```

**Output example:**
```
📋 Form field list:
  • full_name (Text) - Page 1
  • email (Text) - Page 1, Current value:
  • phone (Text) - Page 1
  • address_line1 (Text) - Page 1
  • city (Text) - Page 1
  • state (Dropdown) - Page 1
      Options: AL, AK, AZ, AR, CA, ...
  • checkbox_agree (Checkbox) - Page 2
```

### Usage

**CLI:**
```bash
# List fields first
python pdf_toolkit.py autofill form.pdf --list-fields

# Fill form with JSON data
python pdf_toolkit.py autofill form.pdf -d sample_form_data.json -o filled.pdf

# Override specific values
python pdf_toolkit.py autofill form.pdf -d sample_form_data.json -v full_name="Jane Smith" -o filled.pdf

# Fill and flatten (make fields non-editable)
python pdf_toolkit.py autofill form.pdf -d sample_form_data.json -o filled.pdf --flatten
```

**Click CLI:**
```bash
python cli.py fill-template --template form.pdf --output filled.pdf --data-file sample_form_data.json
```

**GUI:**
1. Click "Template Fill" in sidebar
2. Select your PDF form
3. Browse to select `sample_form_data.json`
4. Optionally check "Flatten form after filling"
5. Click "Fill Template"

### Customizing for Your PDF

1. **List field names:**
   ```bash
   python pdf_toolkit.py autofill your_form.pdf --list-fields
   ```

2. **Create matching JSON:**
   Copy the field names and create a JSON file:
   ```json
   {
     "exact_field_name_1": "value 1",
     "exact_field_name_2": "value 2"
   }
   ```

3. **Fill the form:**
   ```bash
   python pdf_toolkit.py autofill your_form.pdf -d your_data.json -o filled.pdf
   ```

---

## Common Field Types

### Text Fields
```json
{
  "field_name": "Any text value"
}
```

### Checkboxes
Multiple accepted formats:
```json
{
  "checkbox_agree": "Yes",      // or "yes", "Y", "y"
  "checkbox_consent": "true",   // or "True", "1"
  "checkbox_verified": "1"      // or "On", "on"
}
```

### Radio Buttons
```json
{
  "radio_option": "Option A"    // Must match exact option name
}
```

### Dropdowns
```json
{
  "state": "NY",                // Must match exact option value
  "country": "United States"
}
```

### Date Fields
```json
{
  "date_of_birth": "01/15/1990",
  "start_date": "2025-01-15"
}
```

---

## Tips and Best Practices

### 1. **Use Descriptive Keys**
```json
// Good
{
  "customer_name": "John Doe",
  "invoice_date": "2025-01-15"
}

// Avoid
{
  "n": "John Doe",
  "d": "2025-01-15"
}
```

### 2. **Match Field Names Exactly**
For PDF forms, field names are case-sensitive:
```json
// If PDF field is "Full_Name"
{
  "Full_Name": "John Doe"    // ✅ Correct
  // "full_name": "John Doe"  // ❌ Won't work
}
```

### 3. **Comments in JSON**
While standard JSON doesn't support comments, you can add metadata:
```json
{
  "_comment": "This is a template for customer invoices",
  "_version": "1.0",
  "_last_updated": "2025-01-15",

  "customer_name": "John Doe"
}
```

### 4. **Reusable Templates**
Create templates for common scenarios:
- `invoice_template.json`
- `employee_form.json`
- `customer_info.json`

### 5. **Validation**
Before using, validate your JSON:
```bash
python -m json.tool your_data.json
```

---

## Common Issues

### Issue: "Field not found"
**Solution:** Use `--list-fields` to see exact field names

### Issue: "Checkbox not checking"
**Solution:** Try different checkbox values:
- "Yes" / "yes" / "Y" / "y"
- "true" / "True" / "1"
- "On" / "on"
- "X" / "x"

### Issue: "Invalid JSON"
**Solution:**
- Remove trailing commas
- Ensure all strings use double quotes
- Validate with: `python -m json.tool file.json`

### Issue: "Template placeholders not replaced"
**Solution:**
- Verify placeholder syntax: `{{key}}` not `{key}` or `${key}`
- Check key names match exactly (case-sensitive)

---

## Examples

### Example 1: Simple Invoice

**template.docx:**
```
INVOICE

Bill To: {{customer_name}}
Date: {{invoice_date}}
Amount: {{amount}}
```

**data.json:**
```json
{
  "customer_name": "Acme Corp",
  "invoice_date": "2025-01-15",
  "amount": "$1,500.00"
}
```

**Command:**
```bash
python pdf_toolkit.py template-fill template.docx -o invoice.pdf -d data.json --to-pdf
```

### Example 2: Employee Form

**List fields first:**
```bash
python pdf_toolkit.py autofill employee_form.pdf --list-fields
```

**Create data.json based on field names:**
```json
{
  "employee_name": "John Doe",
  "employee_id": "EMP-001",
  "department": "Engineering",
  "start_date": "01/15/2025",
  "checkbox_benefits": "Yes",
  "checkbox_401k": "Yes"
}
```

**Fill form:**
```bash
python pdf_toolkit.py autofill employee_form.pdf -d data.json -o filled_form.pdf --flatten
```

---

## Quick Reference

| Feature | Command | Template File |
|---------|---------|---------------|
| Fill DOCX | `template-fill` | sample_template_data.json |
| Fill PDF Form | `autofill` | sample_form_data.json |
| List PDF Fields | `autofill --list-fields` | - |
| Convert to PDF | `--to-pdf` flag | - |
| Flatten PDF | `--flatten` flag | - |
| Override Values | `-v key=value` | - |

---

## Need Help?

1. **View command help:**
   ```bash
   python pdf_toolkit.py template-fill --help
   python pdf_toolkit.py autofill --help
   ```

2. **Check field names:**
   ```bash
   python pdf_toolkit.py autofill your_form.pdf --list-fields
   ```

3. **Validate JSON:**
   ```bash
   python -m json.tool your_data.json
   ```

4. **GUI Mode:**
   - Launch: `python pdf_toolkit_gui.py`
   - Click "Template Fill" for visual interface
