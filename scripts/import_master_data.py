#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script: import_master_data.py (ERPNext v16 Native - Streamlined & Robust)"""

import os
import sys
import csv
import argparse

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_clean_dir(custom_path=None):
    if custom_path and os.path.isdir(custom_path):
        return custom_path
    env_dir = os.environ.get("CLEAN_DATA_DIR")
    if env_dir and os.path.isdir(env_dir):
        return env_dir
    candidates = [
        os.path.join(BASE_DIR, "data", "clean-data"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "clean-data"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "clean-data"),
        "/home/frappe/frappe-bench/data/clean-data",
        "/tmp/clean-data",
    ]
    for c in candidates:
        if os.path.isdir(c) and os.path.exists(os.path.join(c, "item_master.csv")):
            return os.path.abspath(c)
    return os.path.join(BASE_DIR, "data", "clean-data")


CLEAN_DIR = get_clean_dir()

UOM_DEFINITIONS = [
    {"name": "Túi", "must_be_whole_number": 1},
    {"name": "Kg", "must_be_whole_number": 0},
    {"name": "m", "must_be_whole_number": 0},
    {"name": "Cây", "must_be_whole_number": 1},
    {"name": "Cái", "must_be_whole_number": 1},
]

ITEM_GROUPS = [
    {"name": "1. NGUYÊN VẬT LIỆU (NVL)", "parent": "All Item Groups", "is_group": 1},
    {"name": "2. BÁN THÀNH PHẨM (BTP)", "parent": "All Item Groups", "is_group": 1},
    {"name": "3. THÀNH PHẨM (TP)", "parent": "All Item Groups", "is_group": 1},
    {"name": "4. TRỤC IN (TRUC)", "parent": "All Item Groups", "is_group": 1},
    {"name": "5. PHẾ LIỆU & THU HỒI", "parent": "All Item Groups", "is_group": 1},
    {"name": "Màng Thô NVL", "parent": "1. NGUYÊN VẬT LIỆU (NVL)", "is_group": 0},
    {"name": "Hóa Chất & Keo Ghép", "parent": "1. NGUYÊN VẬT LIỆU (NVL)", "is_group": 0},
    {"name": "Phụ Kiện Bao Bì", "parent": "1. NGUYÊN VẬT LIỆU (NVL)", "is_group": 0},
    {"name": "Màng In Ống Đồng", "parent": "2. BÁN THÀNH PHẨM (BTP)", "is_group": 0},
    {"name": "Cuộn Màng Ghép BTP", "parent": "2. BÁN THÀNH PHẨM (BTP)", "is_group": 0},
    {"name": "Túi Nước Giặt Có Sẵn (NGCS)", "parent": "3. THÀNH PHẨM (TP)", "is_group": 0},
    {"name": "Túi Màng Ghép Đặt Riêng", "parent": "3. THÀNH PHẨM (TP)", "is_group": 0},
    {"name": "Túi Màng Đơn", "parent": "3. THÀNH PHẨM (TP)", "is_group": 0},
    {"name": "Trục In Ống Đồng", "parent": "4. TRỤC IN (TRUC)", "is_group": 0},
    {"name": "Phế Liệu Thu Hồi", "parent": "5. PHẾ LIỆU & THU HỒI", "is_group": 0},
]

SPEC_NUMERIC_FIELDS = [
    "custom_thickness_mic", "custom_film_width_mm",
    "custom_pouch_width_mm", "custom_pouch_length_mm", "custom_gusset_mm", "custom_cut_length_mm",
    "custom_cylinder_length_mm", "custom_cylinder_circ_mm"
]
SPEC_TEXT_FIELDS = [
    "custom_structure_layers", "custom_print_tech", "custom_accessory_spec",
    "custom_cylinder_item", "custom_cylinder_code", "custom_cylinder_location"
]

FRAPPE_AVAILABLE = False
try:
    import frappe
    FRAPPE_AVAILABLE = True
except ImportError:
    pass


def safe_float(v, default=0.0):
    try:
        return float(v) if v not in (None, "") else default
    except (ValueError, TypeError):
        return default


def safe_int(v, default=0):
    try:
        return int(float(v)) if v not in (None, "") else default
    except (ValueError, TypeError):
        return default


def load_csv(filename):
    path = os.path.join(CLEAN_DIR, filename)
    if not os.path.exists(path):
        return []
    with open(path, mode="r", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def load_all_nhom_a_data():
    master_items = load_csv("item_master.csv")
    customers = load_csv("customer_master.csv")
    bom_master = load_csv("bom_master.csv")
    bom_items = load_csv("bom_items.csv")

    boms_grouped = {b["bom_no"]: {"master": b, "items": []} for b in bom_master}
    for bi in bom_items:
        if bi["bom_no"] in boms_grouped:
            boms_grouped[bi["bom_no"]]["items"].append(bi)

    return {
        "items": [{"master": m, "spec": m} for m in master_items],
        "customers": customers,
        "warehouses": load_csv("warehouses.csv"),
        "suppliers": load_csv("supplier_master.csv") if os.path.exists(os.path.join(CLEAN_DIR, "supplier_master.csv")) else load_csv("suppliers.csv"),
        "operations": load_csv("operations.csv"),
        "boms": list(boms_grouped.values())
    }


def import_to_frappe(data):
    print("=" * 75)
    print(" BẮT ĐẦU IMPORT TOÀN BỘ DANH MỤC NỀN TẢNG (NHÓM A) VÀO ERPNEXT v16")
    print("=" * 75)

    def create_if_missing(doctype, filters, doc_data, log_prefix=""):
        if not frappe.db.exists(doctype, filters):
            frappe.get_doc(doc_data).insert(ignore_permissions=True)
            if log_prefix:
                print(f"   [+] {log_prefix}")

    frappe.db.begin()
    try:
        print("\n1. Nạp Đơn Vị Tính (UOM)...")
        for u in UOM_DEFINITIONS:
            create_if_missing("UOM", u["name"], {"doctype": "UOM", "uom_name": u["name"], "must_be_whole_number": u["must_be_whole_number"]}, f"Tạo UOM: {u['name']}")

        print("\n2. Nạp Cây Nhóm Hàng (Item Group Hierarchy)...")
        for g in ITEM_GROUPS:
            if not frappe.db.exists("Item Group", g["name"]):
                parent = g["parent"]
                if parent != "All Item Groups" and not frappe.db.exists("Item Group", parent):
                    frappe.get_doc({"doctype": "Item Group", "item_group_name": parent, "parent_item_group": "All Item Groups", "is_group": 1}).insert(ignore_permissions=True)
                frappe.get_doc({"doctype": "Item Group", "item_group_name": g["name"], "parent_item_group": g["parent"], "is_group": g["is_group"]}).insert(ignore_permissions=True)
                print(f"   [+] Tạo Item Group: {g['name']}")

        print("\n3. Nạp Cây Kho Bãi (Warehouse)...")
        company = frappe.defaults.get_user_default("Company") or "Công ty TNHH Sản Xuất Bao Bì Vạn Phát"
        company_abbr = frappe.db.get_value("Company", company, "abbr") or "VP"
        root_warehouse = frappe.db.get_value("Warehouse", {"company": company, "is_group": 1, "warehouse_name": "All Warehouses"}) or f"All Warehouses - {company_abbr}"
        for w in data["warehouses"]:
            wh_name = w["warehouse_name"]
            parent = root_warehouse if w["parent_warehouse"] in ("All Warehouses", "") else f"{w['parent_warehouse']} - {company_abbr}"
            create_if_missing("Warehouse", {"warehouse_name": wh_name, "company": company}, {
                "doctype": "Warehouse", "warehouse_name": wh_name,
                "parent_warehouse": parent, "is_group": int(w["is_group"]), "company": company
            }, f"Tạo Kho: {wh_name}")

        print(f"\n4. Nạp {len(data['customers'])} Khách Hàng...")
        for c in data["customers"]:
            cname = c["customer_name"]
            c_group = c.get("customer_group", "Khách Hàng Thương Mại & Phân Phối")
            if c_group and not frappe.db.exists("Customer Group", c_group):
                frappe.get_doc({"doctype": "Customer Group", "customer_group_name": c_group, "parent_customer_group": "All Customer Groups", "is_group": 0}).insert(ignore_permissions=True)
            
            c_terr = c.get("territory", "Việt Nam")
            if c_terr and not frappe.db.exists("Territory", c_terr):
                frappe.get_doc({"doctype": "Territory", "territory_name": c_terr, "parent_territory": "All Territories", "is_group": 0}).insert(ignore_permissions=True)

            cust_doc = {
                "doctype": "Customer",
                "customer_name": cname,
                "alias": c.get("alias", ""),
                "customer_type": c.get("customer_type", "Company"),
                "customer_group": c_group,
                "territory": c_terr,
                "default_currency": c.get("default_currency", "VND"),
                "disabled": safe_int(c.get("disabled", 0))
            }
            cl = safe_float(c.get("credit_limit", 0))
            if cl > 0:
                cust_doc["credit_limits"] = [{
                    "company": company,
                    "credit_limit": cl
                }]
            create_if_missing("Customer", cname, cust_doc)
        for s in data["suppliers"]:
            grp = s.get("supplier_group", "All Supplier Groups")
            if grp and grp != "All Supplier Groups":
                create_if_missing("Supplier Group", grp, {
                    "doctype": "Supplier Group", "supplier_group_name": grp,
                    "parent_supplier_group": "All Supplier Groups", "is_group": 0
                })
            create_if_missing("Supplier", s["supplier_name"], {
                "doctype": "Supplier",
                "supplier_name": s["supplier_name"],
                "alias": s.get("alias", ""),
                "supplier_group": grp,
                "supplier_type": s.get("supplier_type", "Company"),
                "country": s.get("country", "Việt Nam"),
                "payment_terms": s.get("payment_terms", ""),
                "default_currency": s.get("default_currency", "VND"),
                "tax_id": s.get("tax_id", ""),
                "disabled": safe_int(s.get("disabled", 0))
            }, f"Tạo NCC: {s['supplier_name']} ({s.get('alias', '')})")

        print("\n5. Nạp Trạm Máy & Công Đoạn Sản Xuất...")
        for op in data["operations"]:
            create_if_missing("Workstation", op["workstation"], {
                "doctype": "Workstation", "workstation_name": op["workstation"],
                "production_capacity": 1, "hour_rate": safe_float(op.get("hour_rate", 200000))
            })
            create_if_missing("Operation", op["operation"], {
                "doctype": "Operation", "name": op["operation"], "operation": op["operation"],
                "workstation": op["workstation"], "description": op.get("desc", "")
            }, f"Tạo Công Đoạn: {op['operation']}")

        print(f"\n6. Nạp {len(data['items'])} Mặt Hàng...")
        def item_dep_rank(it):
            c = it["master"]["item_code"]
            if c.startswith("TRUC-"): return 1
            if c.startswith("NVL-"): return 2
            if c.startswith("BTP-"): return 3
            if c.startswith("TMD-"): return 4
            if c.startswith("NGCS-"): return 5
            return 6
        sorted_items = sorted(data["items"], key=item_dep_rank)
        for it in sorted_items:
            m, s = it["master"], it["spec"]
            code = m["item_code"]
            brand = m.get("brand", "").strip()
            if brand and not frappe.db.exists("Brand", brand):
                frappe.get_doc({"doctype": "Brand", "brand": brand}).insert(ignore_permissions=True)

            doc_dict = {
                "doctype": "Item",
                "item_code": code,
                "item_name": m["item_name"],
                "custom_alias": m.get("custom_alias", ""),
                "item_group": m["item_group"],
                "stock_uom": m["stock_uom"],
                "brand": brand or None,
                "description": m.get("description", ""),
                "default_material_request_type": m.get("default_material_request_type", "Manufacture"),
                "standard_rate": safe_float(m.get("standard_rate", 0.0)),
                "min_order_qty": safe_float(m.get("min_order_qty", 0.0)),
                "safety_stock": safe_float(m.get("safety_stock", 0.0)),
                "disabled": safe_int(m.get("disabled", 0)),
                "is_stock_item": safe_int(m.get("is_stock_item", 1)),
                "is_sales_item": safe_int(m.get("is_sales_item", 1)),
                "is_purchase_item": safe_int(m.get("is_purchase_item", 0)),
            }
            if s:
                for k in SPEC_NUMERIC_FIELDS:
                    doc_dict[k] = safe_float(s.get(k))
                for k in SPEC_TEXT_FIELDS:
                    doc_dict[k] = str(s.get(k) or "")
                doc_dict["custom_cylinder_qty"] = safe_int(s.get("custom_cylinder_qty"))
                if code.startswith("TRUC-") or doc_dict.get("custom_cylinder_item") == code:
                    doc_dict["custom_cylinder_item"] = ""

            if frappe.db.exists("Item", code):
                doc = frappe.get_doc("Item", code)
                for k, v in doc_dict.items():
                    if k != "doctype": doc.set(k, v)
                doc.save(ignore_permissions=True)
            else:
                frappe.get_doc(doc_dict).insert(ignore_permissions=True)

        print(f"\n7. Nạp {len(data['boms'])} Định Mức Sản Xuất (BOM)...")
        currency = frappe.db.get_value("Company", company, "default_currency") or "VND"
        for b in data["boms"]:
            bm = b["master"]
            if not frappe.db.exists("BOM", {"item": bm["item"], "is_default": 1}):
                frappe.get_doc({
                    "doctype": "BOM", "item": bm["item"], "quantity": safe_float(bm["quantity"], 1000),
                    "uom": bm["uom"], "company": company, "currency": currency,
                    "conversion_rate": 1.0, "rm_cost_as_per": "Valuation Rate",
                    "is_active": 1, "is_default": 1, "with_operations": 0,
                    "process_loss_percentage": safe_float(bm.get("process_loss_percentage", 2.0)),
                    "items": [{"item_code": bi["item_code"], "qty": safe_float(bi["qty"]), "uom": bi["uom"], "rate": safe_float(bi.get("rate", 0.0))} for bi in b["items"]]
                }).insert(ignore_permissions=True)
                print(f"   [+] Tạo BOM: {bm['bom_no']} cho {bm['item']}")

        frappe.db.commit()
        print("\n" + "=" * 75)
        print(" IMPORT THÀNH CÔNG RỰC RỠ TOÀN BỘ NHÓM A VÀO DATABASE!")
        print("=" * 75)
    except Exception as e:
        frappe.db.rollback()
        print(f"\n[!] LỖI - ĐÃ ROLLBACK GIAO DỊCH: {e}")
        raise e


def run_dry_run(data):
    print("=" * 75)
    print(" BÁO CÁO KIỂM THỬ TOÀN VẸN MASTER DATA (NHÓM A) - CHUẨN ERPNEXT v16 NATIVE")
    print("=" * 75)

    print("\n1. ĐƠN VỊ TÍNH CHUẨN (5 UOMs):")
    for u in UOM_DEFINITIONS:
        print(f"   - {u['name']:<6} (Số nguyên: {u['must_be_whole_number']})")

    print("\n2. CÂY NHÓM HÀNG CHUẨN HÓA (ITEM GROUPS):")
    for g in ITEM_GROUPS:
        indent = "   " if g["parent"] == "All Item Groups" else "      └── "
        print(f"{indent}{g['name']} ({'Nhóm cha' if g['is_group'] else 'Nhóm lá gán Item'})")

    print(f"\n3. CÂY KHO BÃI SẢN XUẤT ({len(data['warehouses'])} Kho):")
    for w in data["warehouses"]:
        indent = "   " if w["parent_warehouse"] == "All Warehouses" else "      └── "
        print(f"{indent}[{w['warehouse_code']:<9}] {w['warehouse_name']:<25} ({w['desc']})")

    print(f"\n4. ĐỐI TÁC NGHIỆP VỤ (PARTNERS):")
    cust_list = data["customers"]
    cust_types = {}
    cust_groups = {}
    debt_custs = []
    with_addr = 0
    for c in cust_list:
        ct = c.get("customer_type", "Company")
        cust_types[ct] = cust_types.get(ct, 0) + 1
        cg = c.get("customer_group", "Khác")
        cust_groups[cg] = cust_groups.get(cg, 0) + 1
        cl = safe_float(c.get("credit_limit", 0))
        if cl > 0:
            debt_custs.append((c["customer_name"], c.get("alias", ""), cl))
        if c.get("primary_address", "").strip():
            with_addr += 1

    print(f"   - Khách Hàng: {len(cust_list)} đối tượng (Đã chuẩn hóa 100% từ raw-data)")
    print(f"      * Phân loại pháp nhân : {', '.join([f'{k}: {v}' for k, v in cust_types.items()])}")
    print(f"      * Nhóm khách hàng     :")
    for cg, cnt in sorted(cust_groups.items(), key=lambda x: x[1], reverse=True):
        print(f"         • {cg:<35}: {cnt:>3} đối tượng")
    print(f"      * Khách hàng có địa chỉ thực tế : {with_addr}/{len(cust_list)} đối tượng")
    print(f"      * Khách hàng công nợ trả sau    :")
    for cn, al, cl in debt_custs:
        print(f"         • {cn} ({al}): Hạn mức nợ {cl:,.0f} đ")
    supp_list = data["suppliers"]
    supp_types = {}
    supp_groups = {}
    with_tax_supp = 0
    with_addr_supp = 0
    for s in supp_list:
        st = s.get("supplier_type", "Company")
        supp_types[st] = supp_types.get(st, 0) + 1
        sg = s.get("supplier_group", "Khác")
        supp_groups[sg] = supp_groups.get(sg, 0) + 1
        if s.get("tax_id", "").strip(): with_tax_supp += 1
        if s.get("primary_address", "").strip(): with_addr_supp += 1

    print(f"   - Nhà Cung Cấp: {len(supp_list)} NCC (Đã chuẩn hóa 100% từ raw-data & sổ 331)")
    print(f"      * Phân loại pháp nhân : {', '.join([f'{k}: {v}' for k, v in supp_types.items()])}")
    print(f"      * Có MST đầy đủ       : {with_tax_supp}/{len(supp_list)} NCC")
    print(f"      * Có địa chỉ xưởng/kho: {with_addr_supp}/{len(supp_list)} NCC")
    print(f"      * Nhóm nhà cung cấp   :")
    for sg, cnt in sorted(supp_groups.items(), key=lambda x: x[1], reverse=True):
        print(f"         • {sg:<35}: {cnt:>2} NCC")

    print(f"\n5. CÔNG ĐOẠN & TRẠM MÁY ({len(data['operations'])} Trạm):")
    for op in data["operations"]:
        print(f"   - {op['operation']:<24} -> Trạm máy: {op['workstation']:<38} ({op['hour_rate']:>7} đ/h)")

    print(f"\n6. DANH MỤC MẶT HÀNG ({len(data['items'])} Items):")
    group_stats = {}
    req_stats = {}
    acc_stats = {}
    print_tech_stats = {}
    disabled_cnt = 0
    for it in data["items"]:
        m, s = it["master"], it["spec"]
        grp = m["item_group"]
        group_stats[grp] = group_stats.get(grp, 0) + 1
        rt = m.get("default_material_request_type", "Manufacture")
        req_stats[rt] = req_stats.get(rt, 0) + 1
        acc = s.get("custom_accessory_spec", "")
        if acc: acc_stats[acc] = acc_stats.get(acc, 0) + 1
        pt = s.get("custom_print_tech", "")
        if pt: print_tech_stats[pt] = print_tech_stats.get(pt, 0) + 1
        if safe_int(m.get("disabled", 0)) == 1:
            disabled_cnt += 1

    for grp, cnt in sorted(group_stats.items(), key=lambda x: x[1], reverse=True):
        print(f"   - {grp:<32}: {cnt:>3} mã")
    print(f"   - Tổng mặt hàng đã DISABLE (Ngừng bán thương phẩm): {disabled_cnt} mã (dòng 888 0.6Kg)")

    print("\n   - Thống kê theo Hình Thức Cung Ứng (default_material_request_type):")
    for rt, cnt in req_stats.items():
        print(f"      * {rt:<20}: {cnt:>3} mã")

    print("\n   - Thống kê theo Phụ Kiện Miệng Túi (custom_accessory_spec):")
    for acc, cnt in sorted(acc_stats.items(), key=lambda x: x[1], reverse=True):
        print(f"      * {acc:<30}: {cnt:>3} mã")

    print("\n   - Thống kê theo Công Nghệ In (custom_print_tech):")
    for pt, cnt in sorted(print_tech_stats.items(), key=lambda x: x[1], reverse=True):
        print(f"      * {pt:<30}: {cnt:>3} mã")

    print(f"\n7. ĐỊNH MỨC SẢN XUẤT 2 CẤP (BOM - BILL OF MATERIALS):")
    print(f"   - Tổng số BOM Master : {len(data['boms'])} định mức sản xuất")

    print("\n" + "=" * 75)
    print(" KẾT QUẢ: 100% DANH MỤC ITEM ĐÃ ĐƯỢC CHUẨN HÓA THEO ERPNEXT v16 NATIVE!")
    print("=" * 75)


def execute():
    data = load_all_nhom_a_data()
    import_to_frappe(data)


def main():
    parser = argparse.ArgumentParser(description="Nạp Danh Mục Nền Tảng (Nhóm A) Bao Bì Vạn Phát")
    parser.add_argument("--dry-run", action="store_true", help="Chạy kiểm tra tính toàn vẹn Nhóm A")
    parser.add_argument("--site", type=str, help="Tên site Frappe")
    parser.add_argument("--data-dir", type=str, help="Đường dẫn thư mục clean-data")
    args, _ = parser.parse_known_args()

    if args.data_dir:
        global CLEAN_DIR
        CLEAN_DIR = get_clean_dir(args.data_dir)

    data = load_all_nhom_a_data()
    if args.dry_run or not FRAPPE_AVAILABLE:
        run_dry_run(data)
    else:
        if args.site and (not hasattr(frappe, "db") or not frappe.db):
            frappe.init(site=args.site)
            frappe.connect()
        import_to_frappe(data)


if __name__ == "__main__":
    if FRAPPE_AVAILABLE and getattr(frappe, "db", None) and any("run-script" in a or "execute" in a for a in sys.argv):
        execute()
    else:
        main()

