import frappe
from rami_mall.scripts import payment_update, supplier_pay

def payment_on_submit(doc, method):
    # تحديث حالة الفواتير
    payment_update.update_invoice_state(doc, method)

    # خصم المبلغ من رصيد المورد
    supplier_pay.update_supplier_due_on_payment_submit(doc, method)
