import frappe
from frappe.utils import nowdate

def execute():
    today = nowdate()
    frappe.log_error(f"Scheduler script executed at {today}", "Scheduler Test")

    offers = frappe.get_all(
        "Offers",
        filters={
            "end_date": ("<=", today),
            "active": 1
        },
        fields=["name"]
    )

    for offer in offers:
        frappe.db.set_value("Offers", offer.name, "active", 0)

    frappe.db.commit()
