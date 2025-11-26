import frappe

def update_invoice_state(doc, method):
    # اجمع كل الدفعات المرتبطة بالفواتير في هذا Payment
    for pi in getattr(doc, "payment_invoices", []):
        invoice_name = pi.invoice
        doctype = "Invoice" if pi.invoice_type == "Invoice" else "Purchase invoce"
        
        # احصل على إجمالي الفاتورة
        total_field = "total_amount" if doctype == "Invoice" else "grand_total"
        invoice_total = frappe.db.get_value(doctype, invoice_name, total_field) or 0

        # جلب كل مستندات Payment المعتمدة المرتبطة بهذه الفاتورة
        payments = frappe.get_all("Payment", filters={"docstatus": 1}, fields=["name"])
        total_paid = 0
        details = []

        for p in payments:
            payment_doc = frappe.get_doc("Payment", p.name)
            for pi2 in getattr(payment_doc, "payment_invoices", []):
                if pi2.invoice == invoice_name:
                    paid_amount = pi2.paid_amount or 0
                    total_paid += paid_amount
                    details.append(f"- سند الدفع {payment_doc.name}: {paid_amount}")

        # تحديد حالة الفاتورة
        if total_paid >= invoice_total:
            state = "تم الدفع"
        elif total_paid > 0:
            state = "مدفوعة جزئيا"
        else:
            state = "قيد الانتظار"

        # تحديث حالة الفاتورة في جدولها الصحيح
        try:
            frappe.db.set_value(doctype, invoice_name, "state", state, update_modified=False)
            frappe.msgprint(
                f"تم تحديث حالة الفاتورة {invoice_name} إلى: {state}\nتفاصيل الدفعات:\n" + "\n".join(details)
            )
        except Exception as e:
            frappe.msgprint(f"حدث خطأ عند تحديث الفاتورة {invoice_name}: {e}")
