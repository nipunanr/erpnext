# In your custom app's Python file (e.g., lead_creation.py)
import frappe
from frappe.model.document import Document

@frappe.whitelist(allow_guest=True)  # allow_guest=True for guest users to call this
def create_lead(lead_data):
    lead_data = frappe.parse_json(lead_data)

    lead = frappe.get_doc({
        'doctype': 'Lead',
        **lead_data
    })
    lead.insert(ignore_permissions=True)
    return lead.name
