import frappe

def purchase_invoice_on_submit(doc, method):
    """
    عند اعتماد فاتورة شراء:
    1. زيادة رصيد المورد
    2. تحديث مخزون الـ Bin لكل منتج
    """
    # 1️⃣ تحديث رصيد المورد
    try:
        if doc.supplier and doc.grand_total:
            supplier_doc = frappe.get_doc("Supplier", doc.supplier)
            current_due = supplier_doc.total_due or 0
            supplier_doc.total_due = current_due + doc.grand_total
            supplier_doc.save(ignore_permissions=True)

            frappe.msgprint(
                f"✅ تم زيادة رصيد المورد ({doc.supplier}) بمقدار {doc.grand_total}. الرصيد الجديد: {supplier_doc.total_due}"
            )
    except Exception as e:
        frappe.throw(f"❌ خطأ أثناء تحديث رصيد المورد من فاتورة الشراء: {e}")

    # 2️⃣ تحديث Bin لكل منتج
    try:
        if getattr(doc, "products", []):
            for item in doc.products:
                if not item.warehouse:
                    frappe.throw(f"⚠ الرجاء تحديد المخزن للمنتج: {item.product}")

                # تحقق من وجود Bin للمنتج في المخزن
                bin_doc = frappe.db.get_value(
                    "Bin",
                    {"product": item.product, "warehouse": item.warehouse},
                    ["name", "actual_qty"],
                    as_dict=True
                )

                if bin_doc:
                    frappe.db.set_value("Bin", bin_doc["name"], "actual_qty", bin_doc["actual_qty"] + item.qty)
                else:
                    new_bin = frappe.get_doc({
                        "doctype": "Bin",
                        "product": item.product,
                        "warehouse": item.warehouse,
                        "actual_qty": item.qty
                    })
                    new_bin.insert()
    except Exception as e:
        frappe.throw(f"❌ خطأ أثناء تحديث المخزون: {e}")
