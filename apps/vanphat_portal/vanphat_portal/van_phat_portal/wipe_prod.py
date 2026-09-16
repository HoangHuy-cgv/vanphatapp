#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Wipe master data cũ + chứng từ test trên PROD trước khi import clean-data.
Sếp duyệt 2026-09-15: wipe hết masters + chứng từ, giữ Company/Users/schema.
GIỮ NGUYÊN: Custom Fields fixtures, UOM, Item Group, Company + năm tài chính,
Warehouse, Users/Roles, Territory/Group root, Price List, Payment Terms.
CHỈ XÓA: chứng từ phát sinh + BOM + Item + Customer + Supplier + Operation/
Workstation + Brand (import dựng lại từ CSV).

Chạy: bench --site app.vanphat.io.vn execute vanphat_portal.van_phat_portal.wipe_prod.wipe --kwargs '{"confirm":"WIPE"}'
Khóa: bắt confirm=WIPE. Backup prod đã có trước khi chạy.
"""
import frappe


def wipe(confirm=""):
    assert confirm == "WIPE", "Thieu confirm=WIPE — tu choi xoa"
    site = frappe.local.site
    print(f"Wipe tren site: {site}")

    tx = ["Payment Entry", "Sales Invoice", "Delivery Note", "Purchase Receipt",
          "Purchase Order", "Work Order", "Sales Order", "Quotation",
          "Stock Entry", "Material Request"]
    for dt in tx:
        try:
            names = frappe.get_all(dt, pluck="name")
        except Exception as e:
            print(f"  [?] {dt}: bo qua ({e})")
            continue
        for n in names:
            frappe.delete_doc(dt, n, force=1)
        if names:
            print(f"  [x] {dt}: {len(names)}")

    for n in frappe.get_all("BOM", pluck="name"):
        frappe.delete_doc("BOM", n, force=1)
    print("  [x] BOM")
    for n in frappe.get_all("Item", pluck="name"):
        frappe.delete_doc("Item", n, force=1)
    print("  [x] Item")
    for n in frappe.get_all("Customer", pluck="name"):
        frappe.delete_doc("Customer", n, force=1)
    print("  [x] Customer")
    for n in frappe.get_all("Supplier", pluck="name"):
        frappe.delete_doc("Supplier", n, force=1)
    print("  [x] Supplier")
    for n in frappe.get_all("Operation", pluck="name"):
        frappe.delete_doc("Operation", n, force=1)
    for n in frappe.get_all("Workstation", pluck="name"):
        frappe.delete_doc("Workstation", n, force=1)
    print("  [x] Operation + Workstation")
    for n in frappe.get_all("Brand", pluck="name"):
        frappe.delete_doc("Brand", n, force=1)
    print("  [x] Brand")

    frappe.db.commit()
    print("WIPE XONG tren", site)
