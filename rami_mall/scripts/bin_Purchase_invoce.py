import frappe

def update_bin_on_submit(doc, method):
    if doc.products:  # استبدل باسم الـ Child Table عندك
        for item in doc.products:
            if not item.warehouse:
                frappe.throw(f"الرجاء تحديد المخزن للمنتج: {item.product}")

            # تحقق من وجود Bin للمنتج في المخزن
            bin_doc = frappe.db.get_value("Bin",
                {"product": item.product, "warehouse": item.warehouse},
                ["name", "actual_qty"], as_dict=True
            )

            if bin_doc:
                frappe.db.set_value("Bin", bin_doc.name, "actual_qty", bin_doc.actual_qty + item.qty)
            else:
                new_bin = frappe.get_doc({
                    "doctype": "Bin",
                    "product": item.product,
                    "warehouse": item.warehouse,
                    "actual_qty": item.qty
                })
                new_bin.insert()
