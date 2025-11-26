import frappe

def update_supplier_due_on_payment_submit(doc, method):
    """
    خصم المبلغ من رصيد المورد عند اعتماد سند الدفع
    """
    if doc.doctype != "Payment" or doc.docstatus != 1:
        return

    for row in getattr(doc, "payment_invoices", []):
        if not row.invoice:
            continue

        try:
            invoice_doc = frappe.get_doc("Purchase invoce", row.invoice)
        except frappe.DoesNotExistError:
            frappe.msgprint(f"⚠ الفاتورة {row.invoice} غير موجودة، تخطي")
            continue

        supplier = invoice_doc.supplier
        if not supplier:
            frappe.msgprint(f"⚠ الفاتورة {row.invoice} لا تحتوي على مورد، تخطي")
            continue

        paid_amount = row.paid_amount or 0

        supplier_doc = frappe.get_doc("Supplier", supplier)
        current_due = supplier_doc.total_due or 0
        new_due = max(0, current_due - paid_amount)
        supplier_doc.total_due = new_due
        supplier_doc.save(ignore_permissions=True)
        frappe.db.commit()  # ضمان تطبيق التغيير مباشرة

        frappe.msgprint(
            f"💰 تم خصم {paid_amount} من رصيد المورد ({supplier}). الرصيد الجديد: {new_due}"
        )
