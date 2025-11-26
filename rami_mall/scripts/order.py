import frappe

def update_bin_after_order(doc, method):
    """
    خصم الكميات المطلوبة من Bin عند تأكيد الطلب
    """
    for item in doc.products_order:  # استخدم اسم التشايلد تيبل الصحيح
        product = item.product
        qty_needed = item.qty
        warehouse = item.warehouse  # المخزن موجود داخل الصف نفسه

        # الحصول على Bin للمنتج في المخزن
        bin_doc = frappe.get_value(
            "Bin",
            {"product": product, "warehouse": warehouse},
            ["name", "actual_qty"],
            as_dict=True
        )
        
        if not bin_doc:
            frappe.throw(f"❌ لا يوجد Bin للمنتج {product} في المخزن {warehouse}")
        
        if bin_doc.actual_qty < qty_needed:
            frappe.throw(
                f"❌ الكمية غير كافية للمنتج {product} في المخزن {warehouse}. "
                f"المتاح: {bin_doc.actual_qty}, المطلوب: {qty_needed}"
            )
        
        # تحديث الكمية في Bin
        new_qty = bin_doc.actual_qty - qty_needed
        frappe.db.set_value("Bin", bin_doc["name"], "actual_qty", new_qty)
