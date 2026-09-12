#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script: generate_packaging_boms.py (Simplified & Clean Architecture)"""

import os
import csv

CLEAN_DIR = "data/clean-data"
os.makedirs(CLEAN_DIR, exist_ok=True)

# 1. DANH MỤC CÂY KHO BÃI (5 Kho tinh gọn)
warehouses = [
    {"warehouse_name": "Kho Nguyên Vật Liệu", "warehouse_code": "NVL", "parent_warehouse": "All Warehouses", "is_group": 0, "desc": "Lưu trữ cuộn màng thô, hạt nhựa, keo ghép, dung môi, vòi và phụ kiện."},
    {"warehouse_name": "Kho Bán Thành Phẩm", "warehouse_code": "BTP", "parent_warehouse": "All Warehouses", "is_group": 0, "desc": "Lưu trữ cuộn màng đã in ống đồng và cuộn màng ghép hoàn thiện chờ cắt túi."},
    {"warehouse_name": "Kho Thành Phẩm", "warehouse_code": "TP", "parent_warehouse": "All Warehouses", "is_group": 0, "desc": "Lưu trữ túi thành phẩm (NGCS và túi đặt riêng) đã đóng thùng chờ giao hàng."},
    {"warehouse_name": "Kho Phế Liệu & Thu Hồi", "warehouse_code": "PHE-LIEU", "parent_warehouse": "All Warehouses", "is_group": 0, "desc": "Lưu trữ phế liệu màng biên xén, màng lỗi test máy và phế phẩm thu hồi."},
    {"warehouse_name": "Kho Trục In", "warehouse_code": "TRUC", "parent_warehouse": "All Warehouses", "is_group": 0, "desc": "Quản lý lưu trữ các bộ trục in ống đồng của khách hàng."},
]

# 2. DANH MỤC NHÀ CUNG CẤP (10 NCC verified)
suppliers = [
    {"supplier_name": "CÔNG TY CỔ PHẦN QUỐC TẾ UNLIMITED ACCESS VIỆT NAM", "supplier_group": "Phụ Kiện & Vòi", "supplier_type": "Company", "country": "Vietnam", "products": "Vòi 16mm, Vòi 10mm, Vòi 22mm, Nắp niêm phong"},
    {"supplier_name": "CÔNG TY TNHH BAO BÌ GIẤY TIỀN PHÁT", "supplier_group": "Bao Bì Đóng Gói", "supplier_type": "Company", "country": "Vietnam", "products": "Thùng carton 60x40x40, thùng đóng gói túi"},
    {"supplier_name": "công ty tnhh sản xuất bao bì nhựa tuệ nhi", "supplier_group": "Màng Đơn & Gia Công", "supplier_type": "Company", "country": "Vietnam", "products": "Màng đơn PE sữa, màng PA, gia công thổi màng"},
    {"supplier_name": "CÔNG TY TNHH MTV SUNGDO VINA", "supplier_group": "Màng & In Ấn", "supplier_type": "Company", "country": "Vietnam", "products": "Màng in PET, màng ghép OPP, dịch vụ gia công in"},
    {"supplier_name": "CÔNG TY TNHH MTV SX TM Tạ Minh", "supplier_group": "Hóa Chất & Keo Ghép", "supplier_type": "Company", "country": "Vietnam", "products": "Keo ghép D-9700, chất đóng rắn CL-3192K, dung môi Ethyl Acetate"},
    {"supplier_name": "CÔNG TY TNHH THỊNH ĐẠT BÌNH DƯƠNG", "supplier_group": "Màng & Hạt Nhựa", "supplier_type": "Company", "country": "Vietnam", "products": "Màng OPP, hạt nhựa LLDPE, màng ngọc"},
    {"supplier_name": "CÔNG TY TNHH MTV SX TM VẬT LIỆU MỚI TRANG TÍN", "supplier_group": "Màng Đơn & Trục", "supplier_type": "Company", "country": "Vietnam", "products": "Màng PET, màng nhôm AL, màng MPET, giữ trục in"},
    {"supplier_name": "DOYUNG YOU", "supplier_group": "Chế Bản Trục In", "supplier_type": "Company", "country": "Vietnam", "products": "Khắc laser trục in ống đồng G-code & Z-code"},
    {"supplier_name": "CÔNG TY TNHH THƯƠNG MẠI MÁY MÓC THIẾT BỊ KIM MINH", "supplier_group": "Máy Móc & Phụ Tùng", "supplier_type": "Company", "country": "Vietnam", "products": "Phụ tùng máy cắt, dao cắt dán túi, cảm biến mắt đọc"},
    {"supplier_name": "CÔNG TY TNHH HÓA CHẤT GIA PHÁT", "supplier_group": "Hóa Chất & Keo Ghép", "supplier_type": "Company", "country": "Vietnam", "products": "Dung môi công nghiệp, mực in ống đồng"},
]

# 3. DANH MỤC CÔNG ĐOẠN & TRẠM MÁY (5 Trạm)
operations = [
    {"operation": "In Ống Đồng", "workstation": "Máy In Ống Đồng 8 Màu (Rotogravure)", "hour_rate": 250000, "desc": "In mẫu thiết kế lên mặt trong màng PET/OPP bằng trục in ống đồng."},
    {"operation": "Ghép Màng Khô", "workstation": "Máy Ghép Màng Khô Không Dung Môi", "hour_rate": 220000, "desc": "Ghép màng in PET với màng PA/AL và màng PE sữa bằng keo polyurethane."},
    {"operation": "Chia Cuộn", "workstation": "Máy Chia Cuộn Tốc Độ Cao", "hour_rate": 120000, "desc": "Xén biên màng và chia cuộn màng ghép theo đúng khổ dao cắt túi."},
    {"operation": "Cắt Dán Túi Đáy Đứng", "workstation": "Máy Cắt Túi Đáy Đứng Tự Động (Totani)", "hour_rate": 180000, "desc": "Gập đáy đứng/hàn đáy rời, hàn nhiệt 3 biên thân túi và cắt dao theo bước L_cut."},
    {"operation": "Đóng Vòi Rót", "workstation": "Máy Hàn Vòi Tự Động Cao Tần", "hour_rate": 150000, "desc": "Hàn nhiệt vòi nhựa 16mm/10mm vào đỉnh hoặc góc xéo 45 độ của túi."},
]

# 4. TÍNH TOÁN BOM
def load_csv_dict(filename, key="item_code"):
    path = os.path.join("data/clean-data", filename)
    with open(path, mode="r", encoding="utf-8-sig") as f:
        return {r[key]: r for r in csv.DictReader(f)}

items_spec = load_csv_dict("item_spec.csv")
items_master = load_csv_dict("item_master.csv")

bom_master_list = []
bom_items_list = []

def add_bom_item(bom_no, code, name, qty, uom, scrap_pct, note=""):
    bom_items_list.append({
        "bom_no": bom_no, "item_code": code, "item_name": name,
        "qty": qty, "uom": uom, "scrap_pct": scrap_pct, "note": note
    })

btp_roll_map = {
    "NGCS": {"Đỏ": "BTP-00004", "Tím": "BTP-00004", "Hồng": "BTP-00005", "Xanh": "BTP-00005", "Vàng": "BTP-00004"},
    "TP-00001": "BTP-00001", "TP-00002": "BTP-00002", "TP-00003": "BTP-00003",
    "TP-00004": "BTP-00001", "TP-00005": "BTP-00002", "TP-00006": "BTP-00003",
    "TP-00012": "BTP-00006", "TP-00013": "BTP-00006",
    "TP-00020": "BTP-00007", "TP-00021": "BTP-00007",
    "TP-00022": "BTP-00008", "TP-00036": "BTP-00009",
}

SPOUT_MAP = {
    "16mm": ("NVL-00040", "Vòi 16mm"),
    "10mm": ("NVL-00041", "Vòi 10mm"),
    "22mm": ("NVL-00042", "Vòi 22mm"),
}

# 4.1. BOM Túi Thành Phẩm (NGCS & TP)
pouch_codes = [c for c, m in items_master.items() if c.startswith("NGCS-") or (c.startswith("TP-") and int(m.get("disabled", 0)) == 0)]

for code in pouch_codes:
    m = items_master[code]
    s = items_spec[code]
    bom_no = f"BOM-{code}-001"
    item_name = m["item_name"]
    pouch_len_mm = float(s.get("custom_cut_length_mm") or s.get("custom_pouch_length_mm") or 300)
    pouch_w_mm = float(s.get("custom_pouch_width_mm") or 240)
    spout_type = s.get("custom_spout_type", "")
    closure_type = s.get("custom_closure_type", "")

    # Xác định cuộn BTP
    btp_code = "BTP-00005"
    if code.startswith("NGCS-"):
        for color, btp in btp_roll_map["NGCS"].items():
            if color in item_name:
                btp_code = btp
                break
    else:
        btp_code = btp_roll_map.get(code, "BTP-00001")

    film_m = (pouch_len_mm * 1000.0) / 1000.0
    film_scrap = 2.5
    total_film_m = round(film_m * (1 + film_scrap / 100.0), 2)

    bom_master_list.append({
        "bom_no": bom_no, "item": code, "item_name": item_name, "quantity": 1000,
        "uom": "Túi", "is_active": 1, "is_default": 1, "process_loss_percentage": film_scrap,
        "operations": "Cắt dán túi đáy đứng -> Đóng vòi -> Đóng thùng",
        "description": f"Định mức sản xuất 1.000 túi {item_name} (Hao hụt cắt dán {film_scrap}%)."
    })

    # Vật tư 1: Cuộn màng BTP
    add_bom_item(bom_no, btp_code, items_master.get(btp_code, {}).get("item_name", "Cuộn màng ghép BTP"),
                 total_film_m, "m", film_scrap, f"Bước cắt dao {pouch_len_mm}mm x 1.000 túi + {film_scrap}% hao hụt biên/mối nối")

    # Vật tư 2: Vòi rót
    for k, (v_code, v_name) in SPOUT_MAP.items():
        if k in spout_type or k in closure_type:
            add_bom_item(bom_no, v_code, v_name, 1010, "Cái", 1.0, f"1 vòi/túi + 1% hao hụt máy dán vòi")
            break

    # Vật tư 3: Dây Zipper
    if "Zipper" in closure_type:
        zip_m = round(((pouch_w_mm * 1000.0) / 1000.0) * 1.03, 2)
        add_bom_item(bom_no, "NVL-00043", "Dây Zipper", zip_m, "m", 3.0, f"Khổ ngang túi {pouch_w_mm}mm x 1000 túi + 3% hao hụt")

    # Vật tư 4: Thùng carton
    add_bom_item(bom_no, "NVL-00044", "Thùng carton đựng túi", 2, "Cái", 0, "Đóng gói tiêu chuẩn 500 túi/thùng")

# 4.2. Sub-BOM Cuộn Màng Ghép BTP (13 mã)
btp_codes = [c for c in items_master.keys() if c.startswith("BTP-")]
for code in btp_codes:
    m = items_master[code]
    item_name = m["item_name"]
    bom_no = f"BOM-{code}-001"

    bom_master_list.append({
        "bom_no": bom_no, "item": code, "item_name": item_name, "quantity": 1000,
        "uom": "m", "is_active": 1, "is_default": 1, "process_loss_percentage": 2.0,
        "operations": "Ghép màng khô -> Chia cuộn",
        "description": f"Định mức sản xuất 1.000m cuộn màng ghép {item_name} (Hao hụt ghép 2%)."
    })

    pet_in_code = "NVL-00028"
    for p_code, p_m in items_master.items():
        if p_code.startswith("NVL-") and p_m.get("item_group") == "Màng In Ống Đồng":
            if item_name.replace("Cuộn ", "") in p_m["item_name"]:
                pet_in_code = p_code
                break

    # 6 Vật tư chuẩn của cuộn ghép
    sub_materials = [
        (pet_in_code, items_master.get(pet_in_code, {}).get("item_name", "Màng in PET"), 1020.0, "m", 2.0, "Lớp màng ngoài in ống đồng"),
        ("NVL-00009", "PA K800 15mic", 13.9, "Kg", 2.0, "Lớp màng rào cản PA dẻo dai"),
        ("NVL-00004", "PE sữa K750 190mic", 135.2, "Kg", 2.0, "Lớp màng hàn dán trong cùng"),
        ("NVL-00025", "Keo D-9700", 3.6, "Kg", 3.0, "Định mức keo ghép 2 lớp màng"),
        ("NVL-00026", "Chất Đóng Rắn CL-3192K", 0.72, "Kg", 3.0, "Chất đóng rắn Isocyanate"),
        ("NVL-00027", "Dung Môi Ethyl Acetate", 5.4, "Kg", 5.0, "Dung môi pha keo ghép màng khô"),
    ]
    for mat_code, mat_name, qty, uom, scrap, note in sub_materials:
        add_bom_item(bom_no, mat_code, mat_name, qty, uom, scrap, note)

# 5. XUẤT CSV
def write_csv(filename, rows, headers):
    path = os.path.join(CLEAN_DIR, filename)
    with open(path, mode="w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=headers)
        w.writeheader()
        w.writerows(rows)
    print(f" [v] Xuất thành công {len(rows)} dòng vào: {path}")

write_csv("warehouses.csv", warehouses, ["warehouse_name", "warehouse_code", "parent_warehouse", "is_group", "desc"])
write_csv("suppliers.csv", suppliers, ["supplier_name", "supplier_group", "supplier_type", "country", "products"])
write_csv("operations.csv", operations, ["operation", "workstation", "hour_rate", "desc"])
write_csv("bom_master.csv", bom_master_list, ["bom_no", "item", "item_name", "quantity", "uom", "is_active", "is_default", "process_loss_percentage", "operations", "description"])
write_csv("bom_items.csv", bom_items_list, ["bom_no", "item_code", "item_name", "qty", "uom", "scrap_pct", "note"])
