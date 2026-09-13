import os, sys, re, csv
from python_calamine import CalamineWorkbook

RAW_DIR = "data/raw-data"
OUT_DIR = "data/clean-data"
os.makedirs(OUT_DIR, exist_ok=True)

item_master_list = []
item_spec_list = []
customer_brand_list = []

MASTER_HEADERS = [
    "item_code", "item_name", "item_group", "stock_uom", "brand", "description",
    "default_material_request_type", "standard_rate", "min_order_qty", "safety_stock",
    "disabled", "is_stock_item", "is_sales_item", "is_purchase_item",
    "customer", "customer_ref_code"
]

SPEC_HEADERS = [
    "item_code", "item_name", "custom_structure_layers", "custom_thickness_mic",
    "custom_film_width_mm", "custom_pouch_width_mm", "custom_pouch_length_mm",
    "custom_gusset_mm", "custom_cut_length_mm", "custom_print_tech",
    "custom_accessory_spec", "custom_cylinder_item",
    "custom_cylinder_code", "custom_cylinder_length_mm", "custom_cylinder_circ_mm",
    "custom_cylinder_qty", "custom_cylinder_location"
]

BRAND_HEADERS = [
    "customer_name", "brand_pattern", "color_variant",
    "applied_item_type", "default_item_code", "notes"
]


def add_item(code, name, group, uom, brand="", desc="", req_type="Manufacture",
             standard_rate=0.0, min_order_qty=0, safety_stock=0, disabled=0,
             is_stock=1, is_sales=1, is_purchase=0, customer="", ref="", spec=None):
    item_master_list.append({
        "item_code": code,
        "item_name": name,
        "item_group": group,
        "stock_uom": uom,
        "brand": brand,
        "description": desc,
        "default_material_request_type": req_type,
        "standard_rate": standard_rate,
        "min_order_qty": min_order_qty,
        "safety_stock": safety_stock,
        "disabled": disabled,
        "is_stock_item": is_stock,
        "is_sales_item": is_sales,
        "is_purchase_item": is_purchase,
        "customer": customer,
        "customer_ref_code": ref
    })
    s = {h: "" for h in SPEC_HEADERS}
    s.update({
        "item_code": code,
        "item_name": name,
        "custom_structure_layers": "",
        "custom_thickness_mic": 0,
        "custom_film_width_mm": 0,
        "custom_pouch_width_mm": 0,
        "custom_pouch_length_mm": 0,
        "custom_gusset_mm": 0,
        "custom_cut_length_mm": 0,
        "custom_print_tech": "Không in",
        "custom_accessory_spec": "Hàn kín (Không phụ kiện)",
        "custom_cylinder_item": "",
        "custom_cylinder_code": "",
        "custom_cylinder_length_mm": 0,
        "custom_cylinder_circ_mm": 0,
        "custom_cylinder_qty": 0,
        "custom_cylinder_location": ""
    })
    if spec:
        s.update(spec)
    item_spec_list.append(s)


# ==============================================================================
# 1. NHÓM TÚI NƯỚC GIẶT CÓ SẴN (NGCS - MTS)
# ==============================================================================
ngcs_colors = [
    ("Đỏ", "Đam Mê", "Hương Đam Mê"),
    ("Xanh", "Hoa Hồng", "Hương Hoa Hồng"),
    ("Tím", "Nước Hoa", "Hương Nước Hoa"),
    ("Hồng", "Cá Tính", "Hương Cá Tính"),
    ("Vàng", "Ban Mai", "Hương Nắng Ban Mai"),
]
ngcs_sizes = [
    (1, "Nhỏ", "1.8L - 2.4L", 220, 600, 220, 280, 40, 6500.0, "PET/MPET/PA/PE sữa",
     "Phôi túi nước giặt đáy đứng size nhỏ (1.8L - 2.4L), 4 lớp PET/MPET/PA/PE sữa dày 220mic, gắn vòi 16mm, in sẵn màu {c} ({f}). In lụa lần 2 brandname của khách khi có đơn hàng."),
    (6, "Trung", "3 - 3.6Kg", 230, 700, 280, 340, 45, 7368.0, "PET//PA/PE sữa",
     "Phôi túi nước giặt đáy đứng size trung (3 - 3.6Kg), 3 lớp PET//PA/PE sữa dày 230mic, KT 280x340mm, gắn vòi 16mm, in sẵn màu {c} ({f}). In lụa lần 2 brandname của khách khi có đơn hàng."),
    (11, "Lớn", "3.5L - 5Lit", 250, 800, 300, 380, 50, 9400.0, "PET/MPET/PA/PE sữa",
     "Phôi túi nước giặt đáy đứng size lớn (3.5L - 5Lit), 4 lớp PET/MPET/PA/PE sữa dày 250mic, gắn vòi 16mm, in sẵn màu {c} ({f}). In lụa lần 2 brandname của khách khi có đơn hàng."),
]
for start_idx, size_lbl, cap, thick, film_w, pw, pl, gusset, rate, layers, desc_tpl in ngcs_sizes:
    for offset, (c, sf, ff) in enumerate(ngcs_colors):
        idx = start_idx + offset
        code = f"NGCS-{idx:05d}"
        name = f"NGCS {size_lbl} {c} - {sf}"
        add_item(
            code=code, name=name, group="Túi Nước Giặt Có Sẵn (NGCS)", uom="Túi",
            brand="Vạn Phát", desc=desc_tpl.format(c=c, f=ff), req_type="Manufacture",
            standard_rate=rate, min_order_qty=500, safety_stock=2000,
            spec={
                "custom_structure_layers": layers,
                "custom_thickness_mic": thick,
                "custom_film_width_mm": film_w,
                "custom_pouch_width_mm": pw,
                "custom_pouch_length_mm": pl,
                "custom_gusset_mm": gusset,
                "custom_cut_length_mm": pl,
                "custom_print_tech": "In trục ống đồng",
                "custom_accessory_spec": "Vòi 16mm"
            }
        )

# ==============================================================================
# 2. NHÓM TÚI MÀNG ĐƠN DÙNG CHUNG (TMD - PTO / MUA NGOÀI NCC)
# ==============================================================================
tmd_items = [
    ("TMD-00001", "HD quai thỏ 17x25", 170, 250, 45, "HDPE", "Túi HD trắng sữa quai thỏ 17x25cm (Ví dụ: BV Vạn An)", 0, 65000.0),
    ("TMD-00002", "HD quai thỏ 26x40", 260, 400, 45, "HDPE", "Túi HD trắng sữa quai thỏ 26x40cm (Ví dụ: BV Vạn An)", 0, 65000.0),
    ("TMD-00003", "HD quai thỏ 30x50", 300, 500, 50, "HDPE", "Túi HD trắng sữa quai thỏ 30x50cm xếp hông (Ví dụ: Ốc Kiều)", 0, 66000.0),
    ("TMD-00004", "HD quai thỏ 26x43", 260, 430, 50, "HDPE", "Túi HD trắng sữa quai thỏ 26x43cm đựng 3kg (Ví dụ: Ms. Barun)", 0, 66000.0),
    ("TMD-00005", "HD quai thỏ 30x60", 300, 600, 55, "HDPE", "Túi HD trắng sữa quai thỏ 30x60cm đựng 5kg (Ví dụ: Ms. Barun)", 0, 66000.0),
    ("TMD-00006", "HD quai thỏ 30x20x30", 300, 300, 50, "HDPE", "Túi HD trắng sữa xếp hông đáy vuông 30x20x30cm (Ví dụ: BV Vạn An)", 100, 68000.0),
    ("TMD-00007", "PE hột xoài 20x30", 200, 300, 60, "LDPE", "Túi PE hột xoài trắng sữa 20x30cm (Ví dụ: MTBC An Hữu, Bình Phước, Vĩnh Long)", 0, 64815.0),
    ("TMD-00008", "PE hột xoài 17x22", 170, 220, 60, "LDPE", "Túi PE hột xoài trắng sữa 17x22cm (Ví dụ: PK Huỳnh Minh Thư)", 0, 65000.0),
    ("TMD-00009", "PE hột xoài 30x42", 300, 420, 70, "LDPE", "Túi PE hột xoài trắng sữa 30x42cm (Ví dụ: Nhựa Hà Linh)", 0, 65000.0),
    ("TMD-00010", "PP 32x45", 320, 450, 70, "PP", "Túi PP trong suốt 32x45cm dày 7zem (Ví dụ: LOTUS - Đặng Diều Tâm)", 0, 61111.0),
    ("TMD-00011", "PE 50x100", 500, 1000, 70, "LDPE", "Túi PE trơn khổ lớn 50x100cm dùng bọc nệm (Ví dụ: Nệm Phong Nguyên)", 0, 72222.0),
    ("TMD-00012", "PE Cây Đàn", 300, 485, 60, "LDPE", "Túi phôi màng đơn Cây Đàn (Ví dụ: JNS Việt Nam)", 0, 69444.0),
]
for code, name, w, l, thick, layers, desc, gusset, rate in tmd_items:
    add_item(
        code=code, name=name, group="Túi Màng Đơn", uom="Kg", brand="Mua ngoài",
        desc=desc, req_type="Purchase", standard_rate=rate, min_order_qty=25, safety_stock=100,
        is_purchase=1,
        spec={
            "custom_structure_layers": layers,
            "custom_thickness_mic": thick,
            "custom_film_width_mm": w * 2,
            "custom_pouch_width_mm": w,
            "custom_pouch_length_mm": l,
            "custom_gusset_mm": gusset,
            "custom_cut_length_mm": l,
            "custom_print_tech": "In lụa",
            "custom_accessory_spec": "Hàn kín (Không phụ kiện)"
        }
    )

# ==============================================================================
# 3. NHÓM TÚI MÀNG GHÉP ĐẶT RIÊNG (TP - MTO HOẶC MUA NGOÀI)
# ==============================================================================
custom_pouches = [
    # code, name, brand, cust, ref, cap, w, l, thick, layers, cyl_code, cyl_wh, cyl_l, cyl_c, cyl_q, accessory, print_tech, rate, req_type
    ("TP-00001", "888 3.2Kg Hồng", "888", "CÔNG TY CỔ PHẦN DS COSMETIC", "888-3.2KG-HONG", "3.2Kg", 280, 340, 230, "PET//PA/PE sữa", "G4006940", "Kho Kiến Tâm", 800, 564, 5, "Vòi 16mm", "In trục ống đồng", 5166.0, "Manufacture"),
    ("TP-00002", "888 3.2Kg Tím", "888", "CÔNG TY CỔ PHẦN DS COSMETIC", "888-3.2KG-TIM", "3.2Kg", 280, 340, 230, "PET//PA/PE sữa", "G4006961", "Kho Kiến Tâm", 800, 564, 5, "Vòi 16mm", "In trục ống đồng", 5166.0, "Manufacture"),
    ("TP-00003", "888 3.2Kg Đỏ", "888", "CÔNG TY CỔ PHẦN DS COSMETIC", "888-3.2KG-DO", "3.2Kg", 280, 340, 230, "PET//PA/PE sữa", "G4006960", "Kho Vạn Phát", 800, 564, 5, "Vòi 16mm", "In trục ống đồng", 5166.0, "Manufacture"),
    ("TP-00004", "888 2Kg Hồng", "888", "CÔNG TY CỔ PHẦN DS COSMETIC", "888-2KG-HONG", "2Kg", 240, 300, 210, "PET//PA/PE sữa", "G4006677", "Kho Vạn Phát", 750, 484, 5, "Vòi 16mm", "In trục ống đồng", 4500.0, "Manufacture"),
    ("TP-00005", "888 2Kg Tím", "888", "CÔNG TY CỔ PHẦN DS COSMETIC", "888-2KG-TIM", "2Kg", 240, 300, 210, "PET//PA/PE sữa", "G4005893", "Kho Vạn Phát", 750, 484, 5, "Vòi 16mm", "In trục ống đồng", 4500.0, "Manufacture"),
    ("TP-00006", "888 2Kg Đỏ", "888", "CÔNG TY CỔ PHẦN DS COSMETIC", "888-2KG-DO", "2Kg", 240, 300, 210, "PET//PA/PE sữa", "G4005897", "Kho Vạn Phát", 750, 484, 5, "Vòi 16mm", "In trục ống đồng", 4500.0, "Manufacture"),
    ("TP-00007", "888 0.6Kg Hồng", "888", "CÔNG TY CỔ PHẦN DS COSMETIC", "888-0.6KG-HONG", "0.6Kg", 180, 240, 180, "PET//PA/PE", "G4006660", "Kho Vạn Phát", 750, 456, 5, "Vòi 16mm", "In trục ống đồng", 2800.0, "Manufacture"),
    ("TP-00008", "888 0.6Kg Tím", "888", "CÔNG TY CỔ PHẦN DS COSMETIC", "888-0.6KG-TIM", "0.6Kg", 180, 240, 180, "PET//PA/PE", "G4006655", "Kho Vạn Phát", 750, 456, 5, "Vòi 16mm", "In trục ống đồng", 2800.0, "Manufacture"),
    ("TP-00009", "888 0.6Kg Đỏ", "888", "CÔNG TY CỔ PHẦN DS COSMETIC", "888-0.6KG-DO", "0.6Kg", 180, 240, 180, "PET//PA/PE", "G4005877", "Kho Vạn Phát", 750, 456, 6, "Vòi 16mm", "In trục ống đồng", 2800.0, "Manufacture"),
    ("TP-00010", "NLS 888 0.6Kg", "888", "CÔNG TY CỔ PHẦN DS COSMETIC", "888-NLS-0.6KG", "0.6Kg", 180, 240, 180, "PET//PE", "G4012417", "Kho Vạn Phát", 750, 456, 6, "Vòi 16mm", "In trục ống đồng", 2500.0, "Manufacture"),
    ("TP-00011", "NRC 888 0.6Kg", "888", "CÔNG TY CỔ PHẦN DS COSMETIC", "888-NRC-0.6KG", "0.6Kg", 180, 240, 180, "PET//PE", "G4012418", "Kho Vạn Phát", 750, 456, 5, "Vòi 16mm", "In trục ống đồng", 2500.0, "Manufacture"),
    ("TP-00012", "Minh Râu 3.2Kg Tím", "Minh Râu", "CÔNG TY CỔ PHẦN DS COSMETIC", "MINHRAU-3.2KG-TIM", "3.2Kg", 280, 340, 230, "PET//PA/PE sữa", "G4005887", "Kho Kiến Tâm", 780, 564, 6, "Vòi 16mm", "In trục ống đồng", 5166.0, "Manufacture"),
    ("TP-00013", "Minh Râu 3.2Kg Hồng", "Minh Râu", "CÔNG TY CỔ PHẦN DS COSMETIC", "MINHRAU-3.2KG-HONG", "3.2Kg", 280, 340, 230, "PET//PA/PE sữa", "G4005883", "Kho Kiến Tâm", 780, 564, 6, "Vòi 16mm", "In trục ống đồng", 5166.0, "Manufacture"),
    ("TP-00014", "Lamy 2Kg Vàng", "Lamy", "CÔNG TY CỔ PHẦN ECO WIPES VIỆT NAM", "LAMY-2KG-VANG", "2Kg", 240, 320, 200, "PET/MPET/PA/LLDPE", "", "", "", "", "", "Vòi 16mm", "In trục ống đồng", 5056.0, "Manufacture"),
    ("TP-00015", "Lamy 2Kg Xanh", "Lamy", "CÔNG TY CỔ PHẦN ECO WIPES VIỆT NAM", "LAMY-2KG-XANH", "2Kg", 240, 320, 200, "PET/MPET/PA/LLDPE", "", "", "", "", "", "Vòi 16mm", "In trục ống đồng", 5056.0, "Manufacture"),
    ("TP-00016", "BABA 3.6Kg", "BABA", "CÔNG TY TNHH MTV SX TM XNK ANH PHÁT", "BABA-3.6KG", "3.6Kg", 280, 380, 230, "PET/MPET/PA/PE sữa", "TRUC-BABA", "Kho Vạn Phát", 800, 564, 8, "Vòi 16mm", "In trục ống đồng", 6759.0, "Manufacture"),
    ("TP-00017", "Supergeo 5L", "Supergeo", "CÔNG TY TNHH CÔNG NGHỆ VẬT LIỆU TIÊN PHONG VIETCOAT", "SUPERGEO-5L", "5L", 320, 340, 240, "PET/PA/PA/PE sữa", "TRUC-SUPERGEO", "Kho Vạn Phát", 800, 564, 6, "Vòi 16mm", "In trục ống đồng", 9685.0, "Manufacture"),
    ("TP-00018", "Xốt Pho Mai KOVAA 200g", "KOVAA", "CÔNG TY TNHH SX THƯƠNG MẠI BAO BÌ KOVAA", "KOVAA-200G", "200g", 150, 220, 150, "PET/PA/PES", "", "", "", "", "", "Vòi 10mm", "In trục ống đồng", 1944.0, "Manufacture"),
    ("TP-00019", "TopGia MBTP", "TopGia", "CÔNG TY TNHH PHONG TÍN", "TOPGIA-MBTP", "Tiêu chuẩn", 200, 300, 80, "PET/PE", "", "", "", "", "", "Hàn kín (Không phụ kiện)", "In trục ống đồng", 1780.0, "Purchase"),
    ("TP-00020", "TopGia 1L Hoa Nắng", "TopGia", "CÔNG TY TNHH PHONG TÍN", "TOPGIA-1L-HN", "1L", 180, 250, 190, "PET/PA/PE", "G4011425", "Kho Kiến Tâm", 750, 404, 6, "Vòi 16mm", "In trục ống đồng", 2852.0, "Manufacture"),
    ("TP-00021", "TopGia 1L Đắm Say", "TopGia", "CÔNG TY TNHH PHONG TÍN", "TOPGIA-1L-DS", "1L", 180, 250, 190, "PET/PA/PE", "G4011427", "Kho Kiến Tâm", 750, 404, 6, "Vòi 16mm", "In trục ống đồng", 2852.0, "Manufacture"),
    ("TP-00022", "Softy 3L Tím", "Softy", "CTY TNHH SX - XNK AMYCO", "SOFTY-3L-TIM", "3L", 280, 340, 230, "PET/PA/PE sữa", "", "", "", "", "", "Vòi 16mm", "In trục ống đồng", 6500.0, "Manufacture"),
    ("TP-00023", "Sachpoong 3.2Kg", "Sachpoong", "Khách hàng Sachpoong", "SACHPOONG-3.2KG", "3.2Kg", 280, 340, 230, "PET//PA/PE sữa", "G4010806", "Kho Vạn Phát", 800, 564, 5, "Vòi 16mm", "In trục ống đồng", 6500.0, "Manufacture"),
    ("TP-00024", "Sachpoong 0.6Kg", "Sachpoong", "Khách hàng Sachpoong", "SACHPOONG-0.6KG", "0.6Kg", 180, 240, 180, "PET//PA/PE", "G4010805", "Kho Vạn Phát", 750, 456, 5, "Vòi 16mm", "In trục ống đồng", 2800.0, "Manufacture"),
    ("TP-00025", "Raptor Clean 0.6Kg", "Raptor Clean", "Khách hàng Raptor Clean", "RAPTOR-0.6KG", "0.6Kg", 180, 240, 180, "PET//PA/PE", "G4010947", "Kho Vạn Phát", 750, 456, 7, "Vòi 16mm", "In trục ống đồng", 2800.0, "Manufacture"),
    ("TP-00026", "Trần Quân 2Kg", "Trần Quân", "Khách hàng Trần Quân", "TRANQUAN-2KG", "2Kg", 240, 300, 210, "PET//PA/PE sữa", "G4011409", "Kho Vạn Phát", 750, 484, 4, "Vòi 16mm", "In trục ống đồng", 4500.0, "Manufacture"),
    ("TP-00027", "DPClean 0.6Kg", "DPClean", "Khách hàng DPClean", "DPCLEAN-0.6KG", "0.6Kg", 180, 240, 180, "PET//PA/PE", "G4011542", "Kho Vạn Phát", 750, 456, 5, "Vòi 16mm", "In trục ống đồng", 2800.0, "Manufacture"),
    ("TP-00028", "Bluum 3Kg Đen", "Bluum", "Khách hàng Bluum", "BLUUM-3KG-DEN", "3Kg", 280, 340, 230, "PET//PA/PE sữa", "G4012179", "Kho Vạn Phát", 800, 564, 5, "Vòi 16mm", "In trục ống đồng", 6500.0, "Manufacture"),
    ("TP-00029", "Bluum 3Kg Xanh", "Bluum", "Khách hàng Bluum", "BLUUM-3KG-XANH", "3Kg", 280, 340, 230, "PET//PA/PE sữa", "G4012178", "Kho Vạn Phát", 800, 564, 6, "Vòi 16mm", "In trục ống đồng", 6500.0, "Manufacture"),
    ("TP-00030", "Premium 3.2Kg Tím", "Premium", "Khách hàng Premium", "PREMIUM-3.2KG-TIM", "3.2Kg", 280, 340, 230, "PET//PA/PE sữa", "G4006905", "Kho Kiến Tâm", 800, 564, 5, "Vòi 16mm", "In trục ống đồng", 6500.0, "Manufacture"),
    ("TP-00031", "Premium 3.2Kg Đỏ", "Premium", "Khách hàng Premium", "PREMIUM-3.2KG-DO", "3.2Kg", 280, 340, 230, "PET//PA/PE sữa", "G4006924", "Kho Vạn Phát", 800, 564, 5, "Vòi 16mm", "In trục ống đồng", 6500.0, "Manufacture"),
    ("TP-00032", "Yumi Care 3.6L", "Yumi Care", "Khách hàng Yumi Care", "YUMICARE-3.6L", "3.6L", 280, 350, 230, "PET//PA/PE sữa", "G631383", "Kho Vạn Phát", 900, 568, 5, "Vòi 16mm", "In trục ống đồng", 7200.0, "Manufacture"),
    ("TP-00033", "Sofia 3Kg Xanh", "Sofia", "Khách hàng Sofia", "SOFIA-3KG-XANH", "3Kg", 280, 340, 230, "PET//PA/PE sữa", "G4002697", "Kho Vạn Phát", 850, 526, 5, "Vòi 16mm", "In trục ống đồng", 6500.0, "Manufacture"),
    ("TP-00034", "Clean 3.6L", "Clean", "Khách hàng Clean", "CLEAN-3.6L", "3.6L", 280, 350, 230, "PET//PA/PE sữa", "Z418556", "Kho Vạn Phát", 900, 568, 8, "Vòi 16mm", "In trục ống đồng", 7200.0, "Manufacture"),
    ("TP-00035", "Clean 2L", "Clean", "Khách hàng Clean", "CLEAN-2L", "2L", 240, 300, 210, "PET//PA/PE sữa", "G630657", "Kho Vạn Phát", 800, 466, 8, "Vòi 16mm", "In trục ống đồng", 4500.0, "Manufacture"),
    ("TP-00036", "Futa True 3Kg", "Futa True", "Khách hàng Futa True", "FUTA-3KG", "3Kg", 280, 340, 230, "PET//PA/PE sữa", "G4013050", "Kho Trang Tín", 900, 544, 6, "Vòi 16mm", "In trục ống đồng", 6500.0, "Manufacture"),
    ("TP-00037", "Chakari Louis 3.2Kg", "Chakari", "Khách hàng Chakari", "CHAKARI-3.2KG", "3.2Kg", 280, 340, 230, "PET//PA/PE sữa", "G4014585", "Kho Trang Tín", 850, 846, 7, "Vòi 16mm", "In trục ống đồng", 6500.0, "Manufacture"),
    # CÁC MÃ BỔ SUNG MỚI TỪ ĐƠN CỌC CHƯA GIAO
    ("TP-00038", "Chloe'ly 2L", "Chloe'ly", "CÔNG TY TNHH SẢN XUẤT - XUẤT NHẬP KHẨU AMYCO", "CHLOELY-2L", "2L", 240, 300, 210, "PET/MPET/PA/PE sữa", "", "", "", "", "", "Vòi 16mm", "In trục ống đồng", 5074.0, "Manufacture"),
    ("TP-00039", "SKX Đậu Nành 16x23.5", "SKX", "CÔNG TY CỔ PHẦN DINH DƯỠNG SKX", "SKX-DAUNANH", "500g", 160, 235, 160, "OPPMalt/PE", "G652829", "Kho Vạn Phát", 650, 470, 4, "Hàn kín (Không phụ kiện)", "In trục ống đồng", 1290.0, "Manufacture"),
    ("TP-00040", "Enzy Hạt Nêm 900g", "Enzy", "CÔNG TY TNHH ENZY FOOD", "ENZY-900G", "900g", 250, 300, 150, "PET/AL/PE", "G4012180", "Kho Vạn Phát", 750, 500, 6, "Khóa Zipper", "In trục ống đồng", 3963.0, "Manufacture"),
    ("TP-00041", "Enzy Hạt Nêm 450g", "Enzy", "CÔNG TY TNHH ENZY FOOD", "ENZY-450G", "450g", 200, 260, 140, "PET/AL/PE", "", "", "", "", "", "Khóa Zipper", "In trục ống đồng", 3037.0, "Manufacture"),
    ("TP-00042", "Enzy Hạt Nêm 220g", "Enzy", "CÔNG TY TNHH ENZY FOOD", "ENZY-220G", "220g", 170, 220, 120, "PET/AL/PE", "", "", "", "", "", "Khóa Zipper", "In trục ống đồng", 2111.0, "Manufacture"),
    ("TP-00043", "Enzy Rắc Cơm 11x17", "Enzy", "CÔNG TY TNHH ENZY FOOD", "ENZY-RACCOM", "100g", 110, 170, 100, "PET/AL/PE", "", "", "", "", "", "Khóa Zipper", "In trục ống đồng", 1315.0, "Manufacture"),
    ("TP-00044", "Trang Uyên 2L Không Trục", "Trang Uyên", "CÔNG TY TNHH MTV TM TRANG UYÊN", "TRANGUYEN-2L", "2L", 240, 300, 200, "PET/PA/PE sữa", "", "", "", "", "", "Vòi 16mm", "In offset (Không trục)", 6880.0, "Manufacture"),
    ("TP-00045", "Sofia 2L Ngọc Lan", "Sofia", "CÔNG TY CỔ PHẦN EZ COSMETIC VIỆT NAM – CHI NHÁNH LONG AN", "SOFIA-2L-NL", "2L", 240, 300, 210, "PET/PA/PE sữa", "TRUC-SOFIA2L", "Kho Vạn Phát", 750, 484, 5, "Vòi 16mm", "In trục ống đồng", 5537.0, "Manufacture"),
]
discontinued_codes = {"TP-00007", "TP-00008", "TP-00009", "TP-00010", "TP-00011"}
for code, name, brand, cust, ref, cap, w, l, thick, layers, cyl_code, cyl_wh, cyl_l, cyl_c, cyl_q, accessory, print_tech, rate, req_type in custom_pouches:
    cyl_item = f"TRUC-{cyl_code}" if cyl_code and cyl_code not in ["TRUC-BABA", "TRUC-SUPERGEO", "TRUC-SOFIA2L"] else (cyl_code if cyl_code else "")
    dis = code in discontinued_codes
    desc = f"Túi màng ghép {cap} đặt riêng cho {cust}, cấu trúc {layers} dày {thick}mic, KT {w}x{l}mm. Phụ kiện: {accessory}."
    if dis: desc = f"[NGỪNG BÁN THƯƠNG MẠI] {desc}"
    add_item(
        code=code, name=name, group="Túi Màng Ghép Đặt Riêng", uom="Túi", brand=brand,
        desc=desc, req_type=req_type, standard_rate=rate, min_order_qty=5000, safety_stock=0,
        disabled=1 if dis else 0, is_sales=0 if dis else 1, is_purchase=1 if req_type == "Purchase" else 0,
        customer=cust, ref=ref,
        spec={
            "custom_structure_layers": layers,
            "custom_thickness_mic": thick,
            "custom_film_width_mm": w * 2 + 100,
            "custom_pouch_width_mm": w,
            "custom_pouch_length_mm": l,
            "custom_gusset_mm": 45,
            "custom_cut_length_mm": l,
            "custom_print_tech": print_tech,
            "custom_accessory_spec": accessory,
            "custom_cylinder_item": cyl_item
        }
    )

# ==============================================================================
# 4. NHÓM TRỤC IN ỐNG ĐỒNG (TRUC - CÔNG CỤ TRỤC IN)
# ==============================================================================
def clean_cylinder_title(raw_sp, ma_truc):
    text = raw_sp.strip()
    for p in ['TÚI NƯỚC GIẶT XẢ ', 'TÚI NƯỚC GIẶT ', 'TÚI NƯỚC LAU SÀN ', 'TÚI NƯỚC RỬA CHÉN ', 'TÚI ĐỰNG ', 'CUỘN MÀNG ', 'TÚI MÀNG ', 'TÚI ']:
        if text.upper().startswith(p):
            text = text[len(p):]
            break
    text = re.sub(r'\s*\([^)]*(KT|MÀU|MẪU|ZIPPER|PHỦ MỜ|TRỤC CŨ|ĐÁY ĐỨNG|TIỆT TRÙNG|4 LỚP|NỀN|24\*30|22\*28)[^)]*\)', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\s*-\s*IN\s+\d+\s+MÀU.*', '', text, flags=re.IGNORECASE).strip(' -+')
    words = text.split()
    title = (' '.join(words[:3]) if len(words) > 3 else text).title()
    return f"Trục {title} ({ma_truc})" if ma_truc else f"Trục {title}"

wb_truc = CalamineWorkbook.from_path(os.path.join(RAW_DIR, "THÔNG TIN TRỤC IN.xlsx"))
truc_rows = wb_truc.get_sheet_by_name("Sheet1").to_python()
for idx, r in enumerate(truc_rows[1:], 1):
    if not any(r) or not r[2] or str(r[2]).strip() in ["", "None"]:
        continue
    kho, sp, ma_truc = str(r[1] or "").strip(), str(r[2] or "").strip(), str(r[3] or "").strip()
    cd, cv, sl = r[4], r[5], r[6]
    note = str(r[7] or "").strip() if len(r) > 7 and r[7] else ""
    if ma_truc and ma_truc != "None":
        item_code = f"TRUC-{ma_truc}"
    else:
        u = sp.upper()
        item_code = "TRUC-WAX500G" if "WAX" in u else ("TRUC-KEM-DUANON" if "DỪA" in u else ("TRUC-LUCKYSTAR" if "LUCKY" in u else f"TRUC-PENDING-{idx:03d}"))
    name = clean_cylinder_title(sp, ma_truc)
    add_item(
        code=item_code, name=name, group="Trục In Ống Đồng", uom="Cây", brand="Trục in",
        desc=f"Bộ trục in ống đồng: {sp}. Mã laser: {ma_truc}, Kho: {kho}, SL: {sl} cây. {note}",
        req_type="Purchase", standard_rate=3000000.0, is_purchase=1, ref=ma_truc,
        spec={
            "custom_structure_layers": "Thép mạ đồng crom",
            "custom_print_tech": "In trục ống đồng",
            "custom_accessory_spec": "Hàn kín (Không phụ kiện)",
            "custom_cylinder_code": ma_truc,
            "custom_cylinder_length_mm": cd if isinstance(cd, (int, float)) else 0,
            "custom_cylinder_circ_mm": cv if isinstance(cv, (int, float)) else 0,
            "custom_cylinder_qty": sl if isinstance(sl, int) else (int(sl) if str(sl).isdigit() else 0),
            "custom_cylinder_location": f"Kho {kho}" if kho else "Kho Vạn Phát"
        }
    )

# Thêm 3 bộ trục mới từ đơn cọc
additional_cylinders = [
    ("TRUC-SUPERGEO", "Trục Supergeo 5L", "TRUC-SUPERGEO", 6, 800, 564, "Kho Vạn Phát", 3800000.0),
    ("TRUC-BABA", "Trục BABA 3.6Kg", "TRUC-BABA", 8, 800, 564, "Kho Vạn Phát", 3148148.0),
    ("TRUC-SOFIA2L", "Trục Sửa Sofia 2L", "TRUC-SOFIA2L", 2, 750, 484, "Kho Vạn Phát", 2700000.0),
]
for c_code, c_name, c_laser, c_qty, c_len, c_circ, c_loc, c_rate in additional_cylinders:
    add_item(
        code=c_code, name=c_name, group="Trục In Ống Đồng", uom="Cây", brand="Trục in",
        desc=f"Bộ trục in ống đồng: {c_name}. Số lượng: {c_qty} cây.",
        req_type="Purchase", standard_rate=c_rate, is_purchase=1, ref=c_laser,
        spec={
            "custom_structure_layers": "Thép mạ đồng crom",
            "custom_print_tech": "In trục ống đồng",
            "custom_accessory_spec": "Hàn kín (Không phụ kiện)",
            "custom_cylinder_code": c_laser,
            "custom_cylinder_length_mm": c_len,
            "custom_cylinder_circ_mm": c_circ,
            "custom_cylinder_qty": c_qty,
            "custom_cylinder_location": c_loc
        }
    )

# ==============================================================================
# 5. NHÓM MÀNG THÔ NVL & HÓA CHẤT KEO GHÉP
# ==============================================================================
nvl_items = [
    ("NVL-00001", "PE sữa K700 160mic", "PE sữa", 160, 700, "Kg", 58000.0),
    ("NVL-00002", "PE sữa K700 190mic", "PE sữa", 190, 700, "Kg", 58000.0),
    ("NVL-00003", "PE sữa K740 190mic", "PE sữa", 190, 740, "Kg", 58000.0),
    ("NVL-00004", "PE sữa K750 190mic", "PE sữa", 190, 750, "Kg", 58000.0),
    ("NVL-00005", "PE sữa K740 50mic", "PE sữa", 50, 740, "Kg", 62000.0),
    ("NVL-00006", "PA K700 15mic", "PA", 15, 700, "Kg", 78000.0),
    ("NVL-00007", "PA K740 15mic", "PA", 15, 740, "Kg", 78000.0),
    ("NVL-00008", "PA K760 15mic", "PA", 15, 760, "Kg", 78000.0),
    ("NVL-00009", "PA K800 15mic", "PA", 15, 800, "Kg", 78000.0),
    ("NVL-00010", "PA K380 15mic", "PA", 15, 380, "Kg", 78000.0),
    ("NVL-00011", "PET K560 12mic", "PET", 12, 560, "Kg", 48000.0),
    ("NVL-00012", "PET K610 12mic", "PET", 12, 610, "Kg", 48000.0),
    ("NVL-00013", "PET K700 12mic", "PET", 12, 700, "Kg", 48000.0),
    ("NVL-00014", "PET K740 12mic", "PET", 12, 740, "Kg", 48000.0),
    ("NVL-00015", "PET K800 12mic", "PET", 12, 800, "Kg", 48000.0),
    ("NVL-00016", "PET K790 190mic", "PET", 190, 790, "Kg", 52000.0),
    ("NVL-00017", "MPET K540 12mic", "MPET", 12, 540, "Kg", 55000.0),
    ("NVL-00018", "MPET K800 12mic", "MPET", 12, 800, "Kg", 55000.0),
    ("NVL-00019", "AL K560 6mic", "AL", 6, 560, "Kg", 120000.0),
    ("NVL-00020", "PE trong K720 70mic", "PE trong", 70, 720, "Kg", 56000.0),
    ("NVL-00021", "PE trong K660 75mic", "PE trong", 75, 660, "Kg", 56000.0),
    ("NVL-00022", "PE trong K700 150mic", "PE trong", 150, 700, "Kg", 56000.0),
    ("NVL-00023", "OPP K375 30mic", "OPP", 30, 375, "Kg", 52000.0),
    ("NVL-00024", "Màng Ngọc K800 40mic", "Pearlescent BOPP", 40, 800, "Kg", 58000.0),
    ("NVL-00025", "Keo D-9700", "Polyurethane Adhesive", 0, 0, "Kg", 85000.0),
    ("NVL-00026", "Chất Đóng Rắn CL-3192K", "Curing Agent", 0, 0, "Kg", 110000.0),
    ("NVL-00027", "Dung Môi Ethyl Acetate", "Ethyl Acetate (EA)", 0, 0, "Kg", 32000.0),
]
for code, name, layer, thick, w, uom, rate in nvl_items:
    is_chem = code in ["NVL-00025", "NVL-00026", "NVL-00027"]
    grp = "Hóa Chất & Keo Ghép" if is_chem else "Màng Thô NVL"
    desc = f"Hóa chất / Keo ghép màng: {name}." if is_chem else f"Nguyên vật liệu cuộn màng thô: {name}."
    add_item(
        code=code, name=name, group=grp, uom=uom, brand="NVL", desc=desc,
        req_type="Purchase", standard_rate=rate, is_sales=0, is_purchase=1,
        spec={
            "custom_structure_layers": layer,
            "custom_thickness_mic": thick,
            "custom_film_width_mm": w,
            "custom_print_tech": "Không in",
            "custom_accessory_spec": "Hàn kín (Không phụ kiện)"
        }
    )

# ==============================================================================
# 6. NHÓM MÀNG IN NVL (MUA TỪ NCC IN VỀ GHÉP)
# ==============================================================================
pet_in_items = [
    ("NVL-00028", "PET in 888 - Phấn Thơm", "PET in", 800, 12, "Màng PET đã in ống đồng mẫu 888 - Phấn Thơm (Khổ 800mm)", "m", 4200.0),
    ("NVL-00029", "PET in 888 - Huyền Bí", "PET in", 800, 12, "Màng PET đã in ống đồng mẫu 888 - Huyền Bí Xanh (Khổ 800mm)", "m", 4200.0),
    ("NVL-00030", "PET in 888 - Đam Mê", "PET in", 800, 12, "Màng PET đã in ống đồng mẫu 888 - Đam Mê Đỏ (Khổ 800mm)", "m", 4200.0),
    ("NVL-00031", "PET in NGCS Đỏ - Tím", "PET in", 800, 12, "Màng PET in mẫu NGCS Đỏ - Tím (Khổ 800mm)", "m", 4000.0),
    ("NVL-00032", "PET in NGCS Hồng - Xanh", "PET in", 800, 12, "Màng PET in mẫu NGCS Hồng - Xanh (Khổ 800mm)", "m", 4000.0),
    ("NVL-00033", "PET in Minh Râu Tím", "PET in", 780, 12, "Màng PET in mẫu Minh Râu Tím (Khổ 780mm)", "m", 4200.0),
    ("NVL-00034", "PET in TopGia 2L", "PET in", 750, 12, "Màng PET in mẫu TopGia 2L (Khổ 750mm)", "m", 4000.0),
    ("NVL-00035", "PET in Softy 3L", "PET in", 800, 12, "Màng PET in mẫu Softy 3L Nền Tím (Khổ 800mm)", "m", 4200.0),
    ("NVL-00036", "PET in FUTA Xanh MT", "PET in", 900, 12, "Màng PET in FUTA Xanh mặt trước (Khổ 900mm)", "m", 4500.0),
    ("NVL-00037", "PET in FUTA Xanh MS", "PET in", 900, 12, "Màng PET in FUTA Xanh mặt sau (Khổ 900mm)", "m", 4500.0),
    ("NVL-00038", "PET in FUTA Tím MT", "PET in", 900, 12, "Màng PET in FUTA Tím mặt trước (Khổ 900mm)", "m", 4500.0),
    ("NVL-00039", "PET in FUTA Tím MS", "PET in", 900, 12, "Màng PET in FUTA Tím mặt sau (Khổ 900mm)", "m", 4500.0),
    ("NVL-00045", "PET in BABA", "PET in", 800, 12, "Màng PET in mẫu BABA 3.6Kg (Khổ 800mm)", "m", 4500.0),
    ("NVL-00046", "PET in Năm Tàu", "PET in", 800, 12, "Màng PET in mẫu thực phẩm Năm Tàu", "m", 4200.0),
    ("NVL-00047", "PET in TopGia 1L Đắm Say", "PET in", 750, 12, "Màng PET in mẫu TopGia 1L Đắm Say (Khổ 750mm)", "m", 4000.0),
]
for code, name, layer, w, thick, desc, uom, rate in pet_in_items:
    add_item(
        code=code, name=name, group="Màng In Ống Đồng", uom=uom, brand="Màng in",
        desc=desc, req_type="Purchase", standard_rate=rate, is_sales=0, is_purchase=1,
        spec={
            "custom_structure_layers": layer,
            "custom_thickness_mic": thick,
            "custom_film_width_mm": w,
            "custom_print_tech": "In trục ống đồng",
            "custom_accessory_spec": "Hàn kín (Không phụ kiện)"
        }
    )

# ==============================================================================
# 7. NHÓM CUỘN MÀNG GHÉP BTP (XƯỞNG GHÉP XONG -> BÁN CUỘN HOẶC CẮT TÚI)
# ==============================================================================
btp_items = [
    ("BTP-00001", "Cuộn 888 - Phấn Thơm", "PET//PA/PE sữa", 800, 230, "Cuộn màng ghép hoàn thiện 3 lớp mẫu 888 Phấn Thơm (Input máy cắt túi hoặc bán cuộn)", "m", 12500.0),
    ("BTP-00002", "Cuộn 888 - Huyền Bí", "PET//PA/PE sữa", 800, 230, "Cuộn màng ghép hoàn thiện 3 lớp mẫu 888 Huyền Bí Xanh", "m", 12500.0),
    ("BTP-00003", "Cuộn 888 - Đam Mê", "PET//PA/PE sữa", 800, 230, "Cuộn màng ghép hoàn thiện 3 lớp mẫu 888 Đam Mê Đỏ", "m", 12500.0),
    ("BTP-00004", "Cuộn NGCS Đỏ - Tím", "PET//PA/PE sữa", 800, 230, "Cuộn màng ghép hoàn thiện NGCS Đỏ - Tím", "m", 12000.0),
    ("BTP-00005", "Cuộn NGCS Hồng - Xanh", "PET//PA/PE sữa", 800, 230, "Cuộn màng ghép hoàn thiện NGCS Hồng - Xanh", "m", 12000.0),
    ("BTP-00006", "Cuộn Minh Râu Tím", "PET//PA/PE sữa", 780, 230, "Cuộn màng ghép hoàn thiện Minh Râu Tím", "m", 12500.0),
    ("BTP-00007", "Cuộn TopGia 2L", "PET/PA/PE", 750, 190, "Cuộn màng ghép hoàn thiện TopGia 2L", "m", 11000.0),
    ("BTP-00008", "Cuộn Softy 3L", "PET/PA/PE sữa", 800, 230, "Cuộn màng ghép hoàn thiện Softy 3L", "m", 12500.0),
    ("BTP-00009", "Cuộn FUTA Xanh MT", "PET//PA/PE sữa", 900, 230, "Cuộn màng ghép FUTA Xanh mặt trước", "m", 13500.0),
    ("BTP-00010", "Cuộn FUTA Xanh MS", "PET//PA/PE sữa", 900, 230, "Cuộn màng ghép FUTA Xanh mặt sau", "m", 13500.0),
    ("BTP-00011", "Cuộn FUTA Tím MT", "PET//PA/PE sữa", 900, 230, "Cuộn màng ghép FUTA Tím mặt trước", "m", 13500.0),
    ("BTP-00012", "Cuộn FUTA Tím MS", "PET//PA/PE sữa", 900, 230, "Cuộn màng ghép FUTA Tím mặt sau", "m", 13500.0),
    ("BTP-00013", "Cuộn màng đáy 3.2Kg", "PET/PE sữa", 180, 150, "Cuộn màng ghép chuyên dụng cắt đáy đứng túi 3.2Kg", "m", 5500.0),
    ("BTP-00014", "Cuộn BABA 3.6Kg", "PET/MPET/PA/PE sữa", 800, 230, "Cuộn màng ghép hoàn thiện mẫu BABA 3.6Kg", "m", 13000.0),
    ("BTP-00015", "Cuộn Năm Tàu", "PET/PA/PE", 800, 200, "Cuộn màng ghép hoàn thiện mẫu Năm Tàu", "m", 12000.0),
    ("BTP-00016", "Cuộn TopGia 1L Đắm Say", "PET/PA/PE", 750, 190, "Cuộn màng ghép hoàn thiện TopGia 1L Đắm Say", "m", 11000.0),
]
for code, name, layer, w, thick, desc, uom, rate in btp_items:
    add_item(
        code=code, name=name, group="Cuộn Màng Ghép BTP", uom=uom, brand="Cuộn ghép",
        desc=desc, req_type="Manufacture", standard_rate=rate, is_sales=1, is_purchase=0,
        spec={
            "custom_structure_layers": layer,
            "custom_thickness_mic": thick,
            "custom_film_width_mm": w,
            "custom_print_tech": "In trục ống đồng",
            "custom_accessory_spec": "Hàn kín (Không phụ kiện)"
        }
    )

# ==============================================================================
# 8. NHÓM PHỤ KIỆN BAO BÌ (VẬT TƯ TRONG BOM)
# ==============================================================================
pk_items = [
    ("NVL-00040", "Vòi 16mm", "Cái", "Vòi nhựa phi 16mm kèm nắp chống tràn cho túi nước giặt.", 600.0),
    ("NVL-00041", "Vòi 10mm", "Cái", "Vòi nhựa phi 10mm kèm nắp cho túi thể tích nhỏ / xốt mỹ phẩm.", 500.0),
    ("NVL-00043", "Dây Zipper", "m", "Cuộn dây khóa zipper dán nhiệt cho túi 3 biên / túi đáy đứng.", 450.0),
    ("NVL-00044", "Thùng carton đựng túi", "Cái", "Thùng carton 3 lớp / 5 lớp đóng gói giao hàng túi thành phẩm.", 18000.0),
]
for code, name, uom, desc, rate in pk_items:
    add_item(
        code=code, name=name, group="Phụ Kiện Bao Bì", uom=uom, brand="Phụ kiện",
        desc=desc, req_type="Purchase", standard_rate=rate, is_sales=0, is_purchase=1,
        spec={
            "custom_structure_layers": "Nhựa PP/PE hoặc Carton",
            "custom_print_tech": "Không in",
            "custom_accessory_spec": name if "Vòi" in name else ("Khóa Zipper" if "Zipper" in name else "Hàn kín (Không phụ kiện)")
        }
    )

# ==============================================================================
# 9. NHÓM PHẾ LIỆU THU HỒI
# ==============================================================================
scrap_items = [
    ("NVL-P01", "Phế liệu PE sữa", "Kg", "Phế liệu màng PE sữa phát sinh từ xén biên và chạy máy.", 15000.0),
    ("NVL-P02", "Phế liệu màng ghép", "Kg", "Phế liệu màng ghép phức hợp phát sinh trong quá trình ghép và cắt túi.", 8000.0),
]
for code, name, uom, desc, rate in scrap_items:
    add_item(
        code=code, name=name, group="Phế Liệu Thu Hồi", uom=uom, brand="Phế liệu",
        desc=desc, req_type="Manufacture", standard_rate=rate, is_sales=1, is_purchase=0,
        spec={
            "custom_print_tech": "Không in",
            "custom_accessory_spec": "Hàn kín (Không phụ kiện)"
        }
    )

# ==============================================================================
# 10. CUSTOMER BRAND MATRIX
# ==============================================================================
customer_brand_matrix_raw = [
    ("CÔNG TY TNHH SẢN XUẤT THƯƠNG MẠI DỊCH VỤ TỔNG HỢP THÁI DƯƠNG", "KYROS", "Xanh Dương / Đỏ", "Túi NGCS Lớn (3.5L - 5L)", "NGCS-00012", "In lụa 1-2 màu lên phôi NGCS Lớn"),
    ("CÔNG TY TNHH SẢN XUẤT VÀ KINH DOANH NHẬT QUANG VINA", "Vinplus", "Hồng / Xanh Dương", "Túi NGCS Lớn (3.5L - 5L)", "NGCS-00014", "In lụa 1-2 màu lên phôi NGCS Lớn"),
    ("CÔNG TY CP QUỐC TẾ VMT GROUP", "NEMO", "Tím / Vàng", "Túi NGCS Lớn (3.5L - 5L)", "NGCS-00013", "In lụa 1-2 màu lên phôi NGCS Lớn"),
    ("CÔNG TY CP ĐT LIÊN DOANH SX HÓA MỸ PHẨM CAO CẤP VIỆT NHẬT", "FUSIMI / FUSHIMI", "Đỏ / Tím", "Túi NGCS Lớn (3.5L - 5L)", "NGCS-00011", "In lụa 1-2 màu lên phôi NGCS Lớn"),
    ("Công ty TNHH sản xuất và thương mại Anh Lâm", "DEGO", "Đỏ / Tím", "Túi NGCS Lớn (3.5L - 5L)", "NGCS-00011", "In lụa 1-2 màu lên phôi NGCS Lớn"),
    ("CÔNG TY TNHH TM-DV HÓA MỸ PHẨM LÂM GIA", "SuperClean", "Đỏ / Tím", "Túi NGCS Lớn (3.5L - 5L)", "NGCS-00011", "In lụa 1-2 màu lên phôi NGCS Lớn"),
    ("CÔNG TY TNHH PHÁT TRIỂN THƯƠNG MẠI NHAN GIA PHÁT", "CLEANS", "Xanh Dương", "Túi NGCS Lớn (3.5L - 5L)", "NGCS-00012", "In lụa lên phôi NGCS Lớn"),
    ("CÔNG TY CP PHÚC HƯNG PHÚC", "M'LIFE", "Đỏ", "Túi NGCS Lớn (3.5L - 5L)", "NGCS-00011", "In lụa lên phôi NGCS Lớn"),
    ("CÔNG TY TNHH HÓA PHẨM NAM GIA PHÁT", "KIREI", "Đỏ", "Túi NGCS Lớn (3.5L - 5L)", "NGCS-00011", "In lụa lên phôi NGCS Lớn"),
    ("CÔNG TY TNHH HÓA MỸ PHẨM VIO", "VIO", "Đỏ", "Túi NGCS Lớn (3.5L - 5L)", "NGCS-00011", "In lụa lên phôi NGCS Lớn"),
    ("CÔNG TY TNHHSẢNXUẤT VÀ THƯƠNGMẠITUẤN PHÁT", "FIROLA", "Đỏ", "Túi NGCS Lớn (3.5L - 5L)", "NGCS-00011", "In lụa lên phôi NGCS Lớn"),
    ("CÔNG TY TNHH PHÁT TRIỂN THƯƠNG MẠI CHÂU LONG", "VN MARK", "Vàng", "Túi NGCS Lớn (3.5L - 5L)", "NGCS-00015", "In lụa lên phôi NGCS Lớn"),
    ("CÔNG TY TNHH SX& ĐẦU TƯ PHÚ THÀNH", "RICH CITY", "Vàng / Hồng", "Túi NGCS Lớn (3.5L - 5L)", "NGCS-00015", "In lụa lên phôi NGCS Lớn"),
    ("CÔNG TY TNHH SẢN XUẤT VÀ THƯƠNG MẠI RIOS VIỆT NAM", "RISO", "Tím", "Túi NGCS Lớn (3.5L - 5L)", "NGCS-00013", "In lụa lên phôi NGCS Lớn"),
    ("CÔNG TY TNHH TM-DV THANH TẠO PHÁT", "MYO", "Tím", "Túi NGCS Lớn (3.5L - 5L)", "NGCS-00013", "In lụa lên phôi NGCS Lớn"),
    ("CÔNG TY TNHH THƯƠNG MẠI -XNK T&Đ VIỆT NAM", "CHOOSE ME", "Xanh Dương / Hồng", "Túi NGCS Lớn (3.5L - 5L)", "NGCS-00012", "In lụa lên phôi NGCS Lớn"),
    ("DOANH NGHIỆP THẾ KỶ VÀNG", "OKAY", "Hồng Mới / Tím Mới", "Túi NGCS Trung (3 - 3.6Kg)", "NGCS-00009", "In lụa 1 màu lên phôi NGCS Trung"),
    ("CÔNG TY TNHH HÓA MỸ PHẨM LINH PHƯƠNG", "LINH PHƯƠNG", "Tím Mới", "Túi NGCS Trung (3 - 3.6Kg)", "NGCS-00008", "In lụa 1 màu lên phôi NGCS Trung"),
    ("Công ty TNHH chăm sóc sức khỏe Huy Hoàng", "Huy Hoàng", "Hồng Mới", "Túi NGCS Trung (3 - 3.6Kg)", "NGCS-00009", "In lụa 1 màu lên phôi NGCS Trung"),
    ("CÔNG TY TNHH SẢN XUẤT MỸ PHẨM AN NHIÊN", "AN PERFUN", "Vàng 2 Lít", "Túi NGCS Nhỏ (1.8L - 2.4L)", "NGCS-00005", "In lụa 1 màu lên phôi NGCS Nhỏ"),
    ("CÔNG TY TNHH kinh doanh đầu tư và dịch vụ phan gia bích", "MIGHTY", "Vàng 2 Lít", "Túi NGCS Nhỏ (1.8L - 2.4L)", "NGCS-00005", "In lụa 1 màu lên phôi NGCS Nhỏ"),
    ("Khách hàng Anh Khoa", "MTBC An Hữu", "Đỏ (1 màu 1 mặt)", "Túi PE hột xoài 20x30", "TMD-00007", "In lụa PK Nhi Đồng Sài Gòn MTBC An Hữu"),
    ("Khách hàng Anh Khoa", "MTBC Bình Phước", "Đỏ (1 màu 1 mặt)", "Túi PE hột xoài 20x30", "TMD-00007", "In lụa PK Nhi Đồng Sài Gòn MTBC Bình Phước"),
    ("Khách hàng Anh Khoa", "MTBC Vĩnh Long", "Đỏ (1 màu 1 mặt)", "Túi PE hột xoài 20x30", "TMD-00007", "In lụa PK Nhi Đồng Sài Gòn Vĩnh Long"),
    ("Khách hàng Anh Khoa", "MTBC Củ Chi", "Đỏ (1 màu 1 mặt)", "Túi PE hột xoài 20x30", "TMD-00007", "In lụa PK Nhi Đồng Sài Gòn Củ Chi"),
    ("Khách hàng Anh Khoa", "MTBC Thủ Đức", "Đỏ (1 màu 1 mặt)", "Túi PE hột xoài 20x30", "TMD-00007", "In lụa PK Nhi Đồng Sài Gòn Thủ Đức"),
    ("Phòng khám chuyên khoa Nhi Huỳnh Minh Thư", "Huỳnh Minh Thư", "Đỏ (1 màu 1 mặt)", "Túi PE hột xoài 17x22", "TMD-00008", "In lụa PK Nhi Huỳnh Minh Thư"),
    ("CÔNG TY CỔ PHẦN BỆNH VIỆN VẠN AN", "Bệnh viện Vạn An", "Xanh / Tím (1 màu 1 mặt)", "Túi HD quai thỏ 17x25", "TMD-00001", "In lụa BV Vạn An"),
    ("CÔNG TY CỔ PHẦN BỆNH VIỆN VẠN AN", "Bệnh viện Vạn An", "Xanh / Tím (1 màu 1 mặt)", "Túi HD quai thỏ 26x40", "TMD-00002", "In lụa BV Vạn An"),
    ("CÔNG TY CỔ PHẦN BỆNH VIỆN VẠN AN", "Bệnh viện Vạn An Mẫu Mới", "Xanh / Tím", "Túi HD quai thỏ 30x20x30", "TMD-00006", "In lụa BV Vạn An đáy vuông"),
    ("Hải sản tươi sống Ốc Kiều", "Ốc Kiều", "1 màu 1 mặt", "Túi HD quai thỏ 30x50", "TMD-00003", "In lụa Hải sản Ốc Kiều"),
    ("Khách hàng Ms. Barun", "Ms. Barun 3kg", "1 màu 1 mặt", "Túi HD quai thỏ 26x43", "TMD-00004", "In lụa Ms. Barun"),
    ("Khách hàng Ms. Barun", "Ms. Barun 5kg", "1 màu 1 mặt", "Túi HD quai thỏ 30x60", "TMD-00005", "In lụa Ms. Barun"),
    ("CÔNG TY TNHH NHỰA HÀ LINH", "Nhựa Hà Linh", "Màu đỏ (1 màu 1 mặt)", "Túi PE hột xoài 30x42", "TMD-00009", "In lụa Nhựa Hà Linh"),
    ("HỘ KINH DOANH ĐẶNG DIỀU TÂM", "LOTUS", "1 màu", "Túi PP 32x45", "TMD-00010", "In lụa thương hiệu Lotus"),
    ("CÔNG TY TNHH SẢN XUẤT NỆM PHONG NGUYÊN", "Nệm Phong Nguyên", "Chữ in Nệm Phong Nguyên", "Túi PE trơn 50x100", "TMD-00011", "In lụa bọc nệm"),
    ("CÔNG TY TNHH THƯƠNG MẠI JNS VIỆT NAM", "JNS Cây Đàn", "Flexo / Lụa", "Túi Cây Đàn", "TMD-00012", "In thương hiệu Cây Đàn"),
]
for row in customer_brand_matrix_raw:
    customer_brand_list.append({
        "customer_name": row[0], "brand_pattern": row[1], "color_variant": row[2],
        "applied_item_type": row[3], "default_item_code": row[4], "notes": row[5]
    })


def write_csv(filename, rows, headers):
    path = os.path.join(OUT_DIR, filename)
    with open(path, mode="w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=headers)
        w.writeheader()
        w.writerows(rows)
    print(f" Xuất thành công {len(rows)} dòng vào: {path}")

write_csv("item_master.csv", item_master_list, MASTER_HEADERS)
write_csv("item_spec.csv", item_spec_list, SPEC_HEADERS)
write_csv("customer_brand_matrix.csv", customer_brand_list, BRAND_HEADERS)

