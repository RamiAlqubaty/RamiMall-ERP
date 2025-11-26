import frappe

# =============================
# تحديث Bin بعد حفظ Stock Entry
# =============================
def update_bin_after_stock_entry(doc, method):
    """
    تحديث Bin بعد حفظ Stock Entry لجميع أنواع الحركة
    """
    source_wh = getattr(doc, "warehouse", None)  # اسم الحقل في الرأس
    if not source_wh:
        frappe.throw("❌ المخزن (warehouse) غير محدد في Stock Entry")

    for row in getattr(doc, "products", []) or []:
        product = getattr(row, "product", None)
        qty = getattr(row, "qty", 0.0)
        target_wh = getattr(row, "target_warehouse", None)

        if not product:
            continue

        # دالة لإنشاء Bin إذا لم يوجد
        def get_or_create_bin(prod, wh):
            bin_doc = frappe.get_value(
                "Bin",
                {"product": prod, "warehouse": wh},
                ["name", "actual_qty"],
                as_dict=True
            )
            if not bin_doc:
                new_bin = frappe.get_doc({
                    "doctype": "Bin",
                    "product": prod,
                    "warehouse": wh,
                    "actual_qty": 0.0
                })
                new_bin.insert(ignore_permissions=True)
                frappe.db.commit()
                bin_doc = {"name": new_bin.name, "actual_qty": 0.0}
            return bin_doc

        # تحديث Bin حسب نوع الحركة
        if doc.entry_type == "ادخال":
            bin_doc = get_or_create_bin(product, source_wh)
            frappe.db.set_value("Bin", bin_doc["name"], "actual_qty", bin_doc["actual_qty"] + qty)

        elif doc.entry_type == "اخراج":
            bin_doc = get_or_create_bin(product, source_wh)
            if bin_doc["actual_qty"] < qty:
                frappe.throw(
                    f"❌ الكمية غير كافية للمنتج {product} في المخزن {source_wh}. "
                    f"المتاح: {bin_doc['actual_qty']}, المطلوب: {qty}"
                )
            frappe.db.set_value("Bin", bin_doc["name"], "actual_qty", bin_doc["actual_qty"] - qty)

        elif doc.entry_type == "نقل":
            if not target_wh:
                frappe.throw(f"❌ يجب تحديد target_warehouse للمنتج {product} عند النقل")

            # خصم من المخزن الأصلي
            bin_source = get_or_create_bin(product, source_wh)
            if bin_source["actual_qty"] < qty:
                frappe.throw(
                    f"❌ الكمية غير كافية للمنتج {product} في المخزن {source_wh} للمخزن الهدف {target_wh}"
                )
            frappe.db.set_value("Bin", bin_source["name"], "actual_qty", bin_source["actual_qty"] - qty)

            # إضافة إلى المخزن الهدف
            bin_target = get_or_create_bin(product, target_wh)
            frappe.db.set_value("Bin", bin_target["name"], "actual_qty", bin_target["actual_qty"] + qty)


# =============================
# منع تعديل Stock Entry بعد الحفظ أو التأكيد
# =============================
def prevent_edit(doc, method):
    """
    منع تعديل Stock Entry بعد حفظه أول مرة
    """
    if frappe.db.exists("Stock Entry", doc.name):
        frappe.throw("❌ لا يمكن تعديل هذا المستند بعد حفظه أول مرة.")



# =============================
# منع حذف Stock Entry
# =============================
def prevent_delete(doc, method):
    """
    منع حذف Stock Entry بعد حفظه أول مرة
    """
    if doc.name and frappe.db.exists("Stock Entry", doc.name):
        # اجعل المستند غير قابل للحذف برمجيًا
        doc.allow_delete = False
        frappe.throw("❌ لا يمكن حذف هذا المستند بعد حفظه أول مرة.")
