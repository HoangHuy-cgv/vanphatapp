import os, sys, re, csv
from python_calamine import CalamineWorkbook

RAW_DIR = "data/raw-data"
OUT_DIR = "data/clean-data"
os.makedirs(OUT_DIR, exist_ok=True)

item_master_list = []
item_spec_list = []
customer_brand_list = []

MASTER_HEADERS = [
    "item_code", "item_name", "item_group", "stock_uom", "disabled",
    "is_stock_item", "is_sales_item", "is_purchase_item",
    "customer", "customer_ref_code", "description"
]

SPEC_HEADERS = [
    "item_code", "item_name", "packaging_type", "custom_structure_layers",
    "custom_thickness_mic", "custom_film_width_mm", "custom_density_g_cm3",
    "custom_pouch_width_mm", "custom_pouch_length_mm", "custom_cut_length_mm",
    "custom_capacity", "custom_bottom_type", "custom_gusset_mm",
    "custom_closure_type", "custom_spout_type", "custom_spout_position",
    "custom_handle_type", "custom_print_method", "custom_print_colors",
    "custom_design_variant", "custom_cylinder_item", "cylinder_code",
    "cylinder_length_mm", "cylinder_circ_mm", "cylinder_qty", "cylinder_warehouse"
]

BRAND_HEADERS = [
    "customer_name", "brand_pattern", "color_variant",
    "applied_item_type", "default_item_code", "notes"
]


def add_item(code, name, group, uom, desc="", is_stock=1, is_sales=1, is_purchase=0,
             customer="", ref="", disabled=0, spec=None):
    item_master_list.append({
        "item_code": code, "item_name": name, "item_group": group, "stock_uom": uom,
        "disabled": disabled, "is_stock_item": is_stock, "is_sales_item": is_sales,
        "is_purchase_item": is_purchase, "customer": customer, "customer_ref_code": ref,
        "description": desc
    })
    s = {h: "" for h in SPEC_HEADERS}
    s.update({
        "item_code": code, "item_name": name, "packaging_type": "Túi Màng Ghép",
        "custom_bottom_type": "Không", "custom_spout_type": "Không Vòi",
        "custom_spout_position": "Không", "custom_handle_type": "Không",
        "custom_print_method": "Không In (Màng/Túi Trơn)", "custom_print_colors": 0,
        "custom_thickness_mic": 0, "custom_film_width_mm": 0, "custom_density_g_cm3": 0,
        "custom_pouch_width_mm": 0, "custom_pouch_length_mm": 0, "custom_cut_length_mm": 0,
        "custom_gusset_mm": 0,
    })
    if spec:
        s.update(spec)
    item_spec_list.append(s)


# 1. TÚI NƯỚC GIẶT CÓ SẴN (NGCS)
ngcs_colors = [
    ("Đỏ", "Đam Mê", "Hương Đam Mê"),
    ("Xanh", "Hoa Hồng", "Hương Hoa Hồng"),
    ("Tím", "Nước Hoa", "Hương Nước Hoa"),
    ("Hồng", "Cá Tính", "Hương Cá Tính"),
    ("Vàng", "Ban Mai", "Hương Nắng Ban Mai"),
]
ngcs_sizes = [
    (1, "Nhỏ", "1.8L - 2.4L", 220, 600, 220, 280, 40, 5, "PET/MPET/PA/PE sữa", 1.15,
     "Phôi túi nước giặt đáy đứng size nhỏ (1.8L - 2.4L), 4 lớp PET/MPET/PA/PE sữa dày 220mic, gắn vòi 16mm, in sẵn màu {c} ({f}). In lụa lần 2 brandname của khách khi có đơn hàng."),
    (6, "Trung", "3 - 3.6Kg", 230, 700, 280, 340, 45, 5, "PET//PA/PE sữa", 1.10,
     "Phôi túi nước giặt đáy đứng size trung (3 - 3.6Kg), 3 lớp PET//PA/PE sữa dày 230mic, KT 280x340mm, gắn vòi 16mm, in sẵn màu {c} ({f}). In lụa lần 2 brandname của khách khi có đơn hàng."),
    (11, "Lớn", "3.5L - 5Lit", 250, 800, 300, 380, 50, 6, "PET/MPET/PA/PE sữa", 1.15,
     "Phôi túi nước giặt đáy đứng size lớn (3.5L - 5Lit), 4 lớp PET/MPET/PA/PE sữa dày 250mic, gắn vòi 16mm, in sẵn màu {c} ({f}). In lụa lần 2 brandname của khách khi có đơn hàng."),
]
for start_idx, size_lbl, cap, thick, film_w, pw, pl, gusset, colors, layers, density, desc_tpl in ngcs_sizes:
    for offset, (c, sf, ff) in enumerate(ngcs_colors):
        idx = start_idx + offset
        code = f"NGCS-{idx:05d}"
        name = f"NGCS {size_lbl} {c} - {sf}"
        add_item(code, name, "Túi Nước Giặt Có Sẵn (NGCS)", "Túi", desc=desc_tpl.format(c=c, f=ff), spec={
            "packaging_type": "Túi Màng Ghép", "custom_structure_layers": layers,
            "custom_thickness_mic": thick, "custom_film_width_mm": film_w, "custom_density_g_cm3": density,
            "custom_pouch_width_mm": pw, "custom_pouch_length_mm": pl, "custom_cut_length_mm": pl,
            "custom_capacity": cap, "custom_bottom_type": "Đáy Đứng", "custom_gusset_mm": gusset,
            "custom_closure_type": "Vòi Rót", "custom_spout_type": "Vòi 16mm",
            "custom_spout_position": "Chính Giữa Miệng Túi", "custom_handle_type": "Không Quai",
            "custom_print_method": "In Ống Đồng (Rotogravure)", "custom_print_colors": colors,
            "custom_design_variant": f"{c} ({ff})"
        })

# 2. TÚI MÀNG ĐƠN DÙNG CHUNG (TMD)
tmd_items = [
    ("TMD-00001", "HD quai thỏ 17x25", 170, 250, 45, "HDPE", "Quai Thỏ (Quai Xách)", "500g", "Túi HD trắng sữa quai thỏ 17x25cm dày 4-5zem (Mẫu in ví dụ: BV Vạn An)", 0),
    ("TMD-00002", "HD quai thỏ 26x40", 260, 400, 45, "HDPE", "Quai Thỏ (Quai Xách)", "1.5 - 2Kg", "Túi HD trắng sữa quai thỏ 26x40cm dày 4-5zem (Mẫu in ví dụ: BV Vạn An)", 0),
    ("TMD-00003", "HD quai thỏ 30x50", 300, 500, 50, "HDPE", "Quai Thỏ (Quai Xách)", "3 - 5Kg", "Túi HD trắng sữa quai thỏ 30x50cm xếp hông (Mẫu in ví dụ: Hải sản Ốc Kiều)", 0),
    ("TMD-00004", "HD quai thỏ 26x43", 260, 430, 50, "HDPE", "Quai Thỏ (Quai Xách)", "3Kg", "Túi HD trắng sữa quai thỏ 26x43cm đựng 3kg (Mẫu in ví dụ: Ms. Barun)", 0),
    ("TMD-00005", "HD quai thỏ 30x60", 300, 600, 55, "HDPE", "Quai Thỏ (Quai Xách)", "5Kg", "Túi HD trắng sữa quai thỏ 30x60cm đựng 5kg (Mẫu in ví dụ: Ms. Barun)", 0),
    ("TMD-00006", "HD quai thỏ 30x20x30", 300, 300, 50, "HDPE", "Quai Thỏ (Quai Xách)", "Hộp quà / Thuốc", "Túi HD trắng sữa xếp hông đáy vuông 30x20x30cm mẫu mới (Mẫu in ví dụ: BV Vạn An)", 100),
    ("TMD-00007", "PE hột xoài 20x30", 200, 300, 60, "LDPE", "Đục Lỗ Hột Xoài", "1Kg", "Túi PE hột xoài trắng sữa 20x30cm (Mẫu in ví dụ: MTBC An Hữu, MTBC Bình Phước, MTBC Vĩnh Long)", 0),
    ("TMD-00008", "PE hột xoài 17x22", 170, 220, 60, "LDPE", "Đục Lỗ Hột Xoài", "500g", "Túi PE hột xoài trắng sữa 17x22cm (Mẫu in ví dụ: PK Huỳnh Minh Thư)", 0),
    ("TMD-00009", "PE hột xoài 30x42", 300, 420, 70, "LDPE", "Đục Lỗ Hột Xoài", "3Kg", "Túi PE hột xoài trắng sữa 30x42cm (Mẫu in ví dụ: Nhựa Hà Linh)", 0),
    ("TMD-00010", "PP 32x45", 320, 450, 70, "PP", "Không Quai", "May mặc / Đóng gói", "Túi PP trong suốt 32x45cm dày 7zem (Mẫu in ví dụ: LOTUS - Đặng Diều Tâm)", 0),
    ("TMD-00011", "PE 50x100", 500, 1000, 70, "LDPE", "Không Quai", "Bọc Nệm / Công nghiệp", "Túi PE trơn khổ lớn 50x100cm dùng bọc nệm (Ví dụ: Nệm Phong Nguyên)", 0),
    ("TMD-00012", "PE Cây Đàn", 300, 485, 60, "LDPE", "Quai Thỏ (Quai Xách)", "Chuyên dụng", "Túi phôi màng đơn Cây Đàn (Mẫu in ví dụ: JNS Việt Nam)", 0),
]
for code, name, w, l, thick, layers, handle, cap, desc, gusset in tmd_items:
    add_item(code, name, "Túi Màng Đơn", "Kg", desc=desc, spec={
        "packaging_type": "Túi Màng Đơn", "custom_structure_layers": layers,
        "custom_thickness_mic": thick, "custom_film_width_mm": w * 2,
        "custom_density_g_cm3": 0.95 if "HD" in layers else 0.92,
        "custom_pouch_width_mm": w, "custom_pouch_length_mm": l, "custom_cut_length_mm": l,
        "custom_capacity": cap, "custom_bottom_type": "3 Biên", "custom_gusset_mm": gusset,
        "custom_closure_type": "Hàn Nhiệt Kín", "custom_spout_type": "Không Vòi",
        "custom_spout_position": "Không Đóng Vòi", "custom_handle_type": handle,
        "custom_print_method": "In Lụa (Screen Printing)", "custom_print_colors": 1,
        "custom_design_variant": "Phôi trắng dùng chung"
    })

# 3. TÚI MÀNG GHÉP ĐẶT RIÊNG (TP)
custom_pouches = [
    ("TP-00001", "888 3.2Kg Hồng", "CÔNG TY CỔ PHẦN DS COSMETIC", "888-3.2KG-HONG", "3.2Kg", 280, 340, 230, "PET//PA/PE sữa", "G4006940", "Kho Kiến Tâm", 800, 564, 5, "Hồng (Phấn Thơm)", "Chính Giữa Miệng Túi"),
    ("TP-00002", "888 3.2Kg Tím", "CÔNG TY CỔ PHẦN DS COSMETIC", "888-3.2KG-TIM", "3.2Kg", 280, 340, 230, "PET//PA/PE sữa", "G4006961", "Kho Kiến Tâm", 800, 564, 5, "Tím (Huyền Bí)", "Chính Giữa Miệng Túi"),
    ("TP-00003", "888 3.2Kg Đỏ", "CÔNG TY CỔ PHẦN DS COSMETIC", "888-3.2KG-DO", "3.2Kg", 280, 340, 230, "PET//PA/PE sữa", "G4006960", "Kho Vạn Phát", 800, 564, 5, "Đỏ (Đam Mê)", "Chính Giữa Miệng Túi"),
    ("TP-00004", "888 2Kg Hồng", "CÔNG TY CỔ PHẦN DS COSMETIC", "888-2KG-HONG", "2Kg", 240, 300, 210, "PET//PA/PE sữa", "G4006677", "Kho Vạn Phát", 750, 484, 5, "Hồng", "Chính Giữa Miệng Túi"),
    ("TP-00005", "888 2Kg Tím", "CÔNG TY CỔ PHẦN DS COSMETIC", "888-2KG-TIM", "2Kg", 240, 300, 210, "PET//PA/PE sữa", "G4005893", "Kho Vạn Phát", 750, 484, 5, "Tím", "Chính Giữa Miệng Túi"),
    ("TP-00006", "888 2Kg Đỏ", "CÔNG TY CỔ PHẦN DS COSMETIC", "888-2KG-DO", "2Kg", 240, 300, 210, "PET//PA/PE sữa", "G4005897", "Kho Vạn Phát", 750, 484, 5, "Đỏ", "Chính Giữa Miệng Túi"),
    ("TP-00007", "888 0.6Kg Hồng", "CÔNG TY CỔ PHẦN DS COSMETIC", "888-0.6KG-HONG", "0.6Kg", 180, 240, 180, "PET//PA/PE", "G4006660", "Kho Vạn Phát", 750, 456, 5, "Hồng", "Góc Xéo Túi (45 độ)"),
    ("TP-00008", "888 0.6Kg Tím", "CÔNG TY CỔ PHẦN DS COSMETIC", "888-0.6KG-TIM", "0.6Kg", 180, 240, 180, "PET//PA/PE", "G4006655", "Kho Vạn Phát", 750, 456, 5, "Tím", "Góc Xéo Túi (45 độ)"),
    ("TP-00009", "888 0.6Kg Đỏ", "CÔNG TY CỔ PHẦN DS COSMETIC", "888-0.6KG-DO", "0.6Kg", 180, 240, 180, "PET//PA/PE", "G4005877", "Kho Vạn Phát", 750, 456, 6, "Đỏ", "Góc Xéo Túi (45 độ)"),
    ("TP-00010", "NLS 888 0.6Kg", "CÔNG TY CỔ PHẦN DS COSMETIC", "888-NLS-0.6KG", "0.6Kg", 180, 240, 180, "PET//PE", "G4012417", "Kho Vạn Phát", 750, 456, 6, "Nước Lau Sàn", "Góc Xéo Túi (45 độ)"),
    ("TP-00011", "NRC 888 0.6Kg", "CÔNG TY CỔ PHẦN DS COSMETIC", "888-NRC-0.6KG", "0.6Kg", 180, 240, 180, "PET//PE", "G4012418", "Kho Vạn Phát", 750, 456, 5, "Nước Rửa Chén", "Góc Xéo Túi (45 độ)"),
    ("TP-00012", "Minh Râu 3.2Kg Tím", "CÔNG TY CỔ PHẦN DS COSMETIC", "MINHRAU-3.2KG-TIM", "3.2Kg", 280, 340, 230, "PET//PA/PE sữa", "G4005887", "Kho Kiến Tâm", 780, 564, 6, "Tím", "Chính Giữa Miệng Túi"),
    ("TP-00013", "Minh Râu 3.2Kg Hồng", "CÔNG TY CỔ PHẦN DS COSMETIC", "MINHRAU-3.2KG-HONG", "3.2Kg", 280, 340, 230, "PET//PA/PE sữa", "G4005883", "Kho Kiến Tâm", 780, 564, 6, "Hồng", "Chính Giữa Miệng Túi"),
    ("TP-00014", "Lamy 2Kg Vàng", "CÔNG TY CỔ PHẦN ECO WIPES VIỆT NAM", "LAMY-2KG-VANG", "2Kg", 240, 300, 210, "PET//PA/PE sữa", "", "", "", "", "", "Vàng", "Chính Giữa Miệng Túi"),
    ("TP-00015", "Lamy 2Kg Xanh", "CÔNG TY CỔ PHẦN ECO WIPES VIỆT NAM", "LAMY-2KG-XANH", "2Kg", 240, 300, 210, "PET//PA/PE sữa", "", "", "", "", "", "Xanh", "Chính Giữa Miệng Túi"),
    ("TP-00016", "BABA 3.6Kg", "CÔNG TY TNHH MTV SX TM XNK ANH PHÁT", "BABA-3.6KG", "3.6Kg", 280, 350, 230, "PET/PA/PE sữa", "", "", "", "", "", "BABA", "Chính Giữa Miệng Túi"),
    ("TP-00017", "Vietcoat 5L", "CÔNG TY TNHH CÔNG NGHỆ VẬT LIỆU TIÊN PHONG VIETCOAT", "VIETCOAT-5L", "5L", 300, 380, 250, "PET/PA/PE", "", "", "", "", "", "Keo Dán Gạch", "Góc Xéo Túi (45 độ)"),
    ("TP-00018", "Pho Mai KOVAA 200g", "CÔNG TY TNHH SX THƯƠNG MẠI BAO BÌ KOVAA", "KOVAA-200G", "200g", 120, 180, 120, "PET/AL/PE", "", "", "", "", "", "Xốt Pho Mai", "Góc Xéo Túi (45 độ)"),
    ("TP-00019", "TopGia MBTP", "CÔNG TY TNHH PHONG TÍN", "TOPGIA-MBTP", "Tiêu chuẩn", 200, 300, 80, "PET/PE", "", "", "", "", "", "Màng Bọc Thực Phẩm", "Không Đóng Vòi"),
    ("TP-00020", "TopGia 1L Hoa Nắng", "CÔNG TY TNHH PHONG TÍN", "TOPGIA-1L-HN", "1L", 180, 250, 190, "PET/PA/PE", "G4011425", "Kho Kiến Tâm", 750, 404, 6, "Hoa Nắng", "Góc Xéo Túi (45 độ)"),
    ("TP-00021", "TopGia 1L Đắm Say", "CÔNG TY TNHH PHONG TÍN", "TOPGIA-1L-DS", "1L", 180, 250, 190, "PET/PA/PE", "G4011427", "Kho Kiến Tâm", 750, 404, 6, "Đắm Say", "Góc Xéo Túi (45 độ)"),
    ("TP-00022", "Softy 3L Tím", "CTY TNHH SX - XNK AMYCO", "SOFTY-3L-TIM", "3L", 280, 340, 230, "PET/PA/PE sữa", "", "", "", "", "", "Nền Tím", "Chính Giữa Miệng Túi"),
    ("TP-00023", "Sachpoong 3.2Kg", "Khách hàng Sachpoong", "SACHPOONG-3.2KG", "3.2Kg", 280, 340, 230, "PET//PA/PE sữa", "G4010806", "Kho Vạn Phát", 800, 564, 5, "Sachpoong 3.2Kg", "Chính Giữa Miệng Túi"),
    ("TP-00024", "Sachpoong 0.6Kg", "Khách hàng Sachpoong", "SACHPOONG-0.6KG", "0.6Kg", 180, 240, 180, "PET//PA/PE", "G4010805", "Kho Vạn Phát", 750, 456, 5, "Sachpoong 0.6Kg", "Góc Xéo Túi (45 độ)"),
    ("TP-00025", "Raptor Clean 0.6Kg", "Khách hàng Raptor Clean", "RAPTOR-0.6KG", "0.6Kg", 180, 240, 180, "PET//PA/PE", "G4010947", "Kho Vạn Phát", 750, 456, 7, "Raptor Clean 0.6Kg", "Góc Xéo Túi (45 độ)"),
    ("TP-00026", "Trần Quân 2Kg", "Khách hàng Trần Quân", "TRANQUAN-2KG", "2Kg", 240, 300, 210, "PET//PA/PE sữa", "G4011409", "Kho Vạn Phát", 750, 484, 4, "Trần Quân 2Kg", "Chính Giữa Miệng Túi"),
    ("TP-00027", "DPClean 0.6Kg", "Khách hàng DPClean", "DPCLEAN-0.6KG", "0.6Kg", 180, 240, 180, "PET//PA/PE", "G4011542", "Kho Vạn Phát", 750, 456, 5, "DPClean 0.6Kg", "Góc Xéo Túi (45 độ)"),
    ("TP-00028", "Bluum 3Kg Đen", "Khách hàng Bluum", "BLUUM-3KG-DEN", "3Kg", 280, 340, 230, "PET//PA/PE sữa", "G4012179", "Kho Vạn Phát", 800, 564, 5, "Đen", "Chính Giữa Miệng Túi"),
    ("TP-00029", "Bluum 3Kg Xanh", "Khách hàng Bluum", "BLUUM-3KG-XANH", "3Kg", 280, 340, 230, "PET//PA/PE sữa", "G4012178", "Kho Vạn Phát", 800, 564, 6, "Xanh", "Chính Giữa Miệng Túi"),
    ("TP-00030", "Premium 3.2Kg Tím", "Khách hàng Premium", "PREMIUM-3.2KG-TIM", "3.2Kg", 280, 340, 230, "PET//PA/PE sữa", "G4006905", "Kho Kiến Tâm", 800, 564, 5, "Tím", "Chính Giữa Miệng Túi"),
    ("TP-00031", "Premium 3.2Kg Đỏ", "Khách hàng Premium", "PREMIUM-3.2KG-DO", "3.2Kg", 280, 340, 230, "PET//PA/PE sữa", "G4006924", "Kho Vạn Phát", 800, 564, 5, "Đỏ", "Chính Giữa Miệng Túi"),
    ("TP-00032", "Yumi Care 3.6L", "Khách hàng Yumi Care", "YUMICARE-3.6L", "3.6L", 280, 350, 230, "PET//PA/PE sữa", "G631383", "Kho Vạn Phát", 900, 568, 5, "Yumi Care 3.6L", "Chính Giữa Miệng Túi"),
    ("TP-00033", "Sofia 3Kg Xanh", "Khách hàng Sofia", "SOFIA-3KG-XANH", "3Kg", 280, 340, 230, "PET//PA/PE sữa", "G4002697", "Kho Vạn Phát", 850, 526, 5, "Xanh (Hương LyLy)", "Chính Giữa Miệng Túi"),
    ("TP-00034", "Clean 3.6L", "Khách hàng Clean", "CLEAN-3.6L", "3.6L", 280, 350, 230, "PET//PA/PE sữa", "Z418556", "Kho Vạn Phát", 900, 568, 8, "Clean 3.6L", "Chính Giữa Miệng Túi"),
    ("TP-00035", "Clean 2L", "Khách hàng Clean", "CLEAN-2L", "2L", 240, 300, 210, "PET//PA/PE sữa", "G630657", "Kho Vạn Phát", 800, 466, 8, "Clean 2L", "Chính Giữa Miệng Túi"),
    ("TP-00036", "Futa True 3Kg", "Khách hàng Futa True", "FUTA-3KG", "3Kg", 280, 340, 230, "PET//PA/PE sữa", "G4013050", "Kho Trang Tín", 900, 544, 6, "Futa True 3Kg", "Chính Giữa Miệng Túi"),
    ("TP-00037", "Chakari Louis 3.2Kg", "Khách hàng Chakari", "CHAKARI-3.2KG", "3.2Kg", 280, 340, 230, "PET//PA/PE sữa", "G4014585", "Kho Trang Tín", 850, 846, 7, "Chakari Louis 3.2Kg", "Chính Giữa Miệng Túi"),
]
discontinued_codes = {"TP-00007", "TP-00008", "TP-00009", "TP-00010", "TP-00011"}
for code, name, cust, ref, cap, w, l, thick, layers, cyl_code, cyl_wh, cyl_l, cyl_c, cyl_q, variant, spout_pos in custom_pouches:
    cyl_item = f"TRUC-{cyl_code}" if cyl_code else ""
    dis = code in discontinued_codes
    desc = f"Túi màng ghép {cap} đặt riêng cho {cust}, cấu trúc {layers} dày {thick}mic, KT {w}x{l}mm. Mẫu in: {variant}."
    if dis: desc = f"[NGỪNG BÁN THƯƠNG MẠI] {desc}"
    add_item(code, name, "Túi Màng Ghép Đặt Riêng", "Túi", desc=desc, disabled=1 if dis else 0,
             is_sales=0 if dis else 1, customer=cust, ref=ref, spec={
        "packaging_type": "Túi Màng Ghép", "custom_structure_layers": layers,
        "custom_thickness_mic": thick, "custom_film_width_mm": w * 2 + 100,
        "custom_density_g_cm3": 1.12, "custom_pouch_width_mm": w, "custom_pouch_length_mm": l,
        "custom_cut_length_mm": l, "custom_capacity": cap, "custom_bottom_type": "Đáy Đứng",
        "custom_gusset_mm": 45, "custom_closure_type": "Vòi Rót" if spout_pos != "Không Đóng Vòi" else "Hàn Nhiệt Kín",
        "custom_spout_type": "Vòi 16mm" if spout_pos != "Không Đóng Vòi" else "Không Vòi",
        "custom_spout_position": spout_pos, "custom_handle_type": "Không Quai",
        "custom_print_method": "In Ống Đồng (Rotogravure)", "custom_print_colors": cyl_q if cyl_q else 6,
        "custom_design_variant": variant, "custom_cylinder_item": cyl_item, "cylinder_code": cyl_code,
        "cylinder_length_mm": cyl_l, "cylinder_circ_mm": cyl_c, "cylinder_qty": cyl_q,
        "cylinder_warehouse": cyl_wh
    })

# 4. TRỤC IN ỐNG ĐỒNG
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
    add_item(item_code, name, "Trục In Ống Đồng", "Cây", is_purchase=1, ref=ma_truc,
             desc=f"Bộ trục in ống đồng: {sp}. Mã trục: {ma_truc}, Kho: {kho}, SL: {sl} cây. {note}",
             spec={
                 "packaging_type": "Trục In", "custom_structure_layers": "Thép Mạ Đồng Crom",
                 "custom_film_width_mm": cd if isinstance(cd, (int, float)) else 0,
                 "custom_density_g_cm3": 7.85, "custom_print_method": "In Ống Đồng (Rotogravure)",
                 "custom_print_colors": sl if isinstance(sl, int) else 0,
                 "custom_design_variant": sp, "custom_cylinder_item": item_code,
                 "cylinder_code": ma_truc, "cylinder_length_mm": cd if cd else "",
                 "cylinder_circ_mm": cv if cv else "", "cylinder_qty": sl if sl else "",
                 "cylinder_warehouse": f"Kho {kho}" if kho else "Kho Vạn Phát"
             })

# 5. MÀNG ĐƠN NVL
nvl_items = [
    ("NVL-00001", "PE sữa K700 160mic", "PE sữa", 160, 700, "Kg", 0.93),
    ("NVL-00002", "PE sữa K700 190mic", "PE sữa", 190, 700, "Kg", 0.93),
    ("NVL-00003", "PE sữa K740 190mic", "PE sữa", 190, 740, "Kg", 0.93),
    ("NVL-00004", "PE sữa K750 190mic", "PE sữa", 190, 750, "Kg", 0.93),
    ("NVL-00005", "PE sữa K740 50mic", "PE sữa", 50, 740, "Kg", 0.93),
    ("NVL-00006", "PA K700 15mic", "PA", 15, 700, "Kg", 1.14),
    ("NVL-00007", "PA K740 15mic", "PA", 15, 740, "Kg", 1.14),
    ("NVL-00008", "PA K760 15mic", "PA", 15, 760, "Kg", 1.14),
    ("NVL-00009", "PA K800 15mic", "PA", 15, 800, "Kg", 1.14),
    ("NVL-00010", "PA K380 15mic", "PA", 15, 380, "Kg", 1.14),
    ("NVL-00011", "PET K560 12mic", "PET", 12, 560, "Kg", 1.34),
    ("NVL-00012", "PET K610 12mic", "PET", 12, 610, "Kg", 1.34),
    ("NVL-00013", "PET K700 12mic", "PET", 12, 700, "Kg", 1.34),
    ("NVL-00014", "PET K740 12mic", "PET", 12, 740, "Kg", 1.34),
    ("NVL-00015", "PET K800 12mic", "PET", 12, 800, "Kg", 1.34),
    ("NVL-00016", "PET K790 190mic", "PET", 190, 790, "Kg", 1.34),
    ("NVL-00017", "MPET K540 12mic", "MPET", 12, 540, "Kg", 1.40),
    ("NVL-00018", "MPET K800 12mic", "MPET", 12, 800, "Kg", 1.40),
    ("NVL-00019", "AL K560 6mic", "AL", 6, 560, "Kg", 2.70),
    ("NVL-00020", "PE trong K720 70mic", "PE trong", 70, 720, "Kg", 0.925),
    ("NVL-00021", "PE trong K660 75mic", "PE trong", 75, 660, "Kg", 0.925),
    ("NVL-00022", "PE trong K700 150mic", "PE trong", 150, 700, "Kg", 0.925),
    ("NVL-00023", "OPP K375 30mic", "OPP", 30, 375, "Kg", 0.91),
    ("NVL-00024", "Màng Ngọc K800 40mic", "Pearlescent BOPP", 40, 800, "Kg", 0.75),
    ("NVL-00025", "Keo D-9700", "Polyurethane Adhesive", 0, 0, "Kg", 1.05),
    ("NVL-00026", "Chất Đóng Rắn CL-3192K", "Curing Agent / Isocyanate", 0, 0, "Kg", 1.15),
    ("NVL-00027", "Dung Môi Ethyl Acetate", "Ethyl Acetate (EA)", 0, 0, "Kg", 0.902),
]
for code, name, layer, thick, w, uom, density in nvl_items:
    is_chem = code in ["NVL-00025", "NVL-00026", "NVL-00027"]
    grp = "Hóa Chất & Keo Ghép" if is_chem else "Màng Thô NVL"
    pkg = "Hóa Chất & Keo" if is_chem else "Màng Thô NVL"
    desc = f"Hóa chất / Keo ghép màng: {name}." if is_chem else f"Nguyên vật liệu cuộn màng thô: {name}."
    add_item(code, name, grp, uom, desc=desc, is_sales=0, is_purchase=1, spec={
        "packaging_type": pkg, "custom_structure_layers": layer, "custom_thickness_mic": thick,
        "custom_film_width_mm": w, "custom_density_g_cm3": density,
        "custom_design_variant": "Màng mộc nguyên cuộn"
    })

# 6. MÀNG IN NVL
pet_in_items = [
    ("NVL-00028", "PET in 888 - Phấn Thơm", "PET In", 800, 12, "Màng PET đã in ống đồng mẫu 888 - Phấn Thơm (Khổ 800mm)", "m"),
    ("NVL-00029", "PET in 888 - Huyền Bí", "PET In", 800, 12, "Màng PET đã in ống đồng mẫu 888 - Huyền Bí Xanh (Khổ 800mm)", "m"),
    ("NVL-00030", "PET in 888 - Đam Mê", "PET In", 800, 12, "Màng PET đã in ống đồng mẫu 888 - Đam Mê Đỏ (Khổ 800mm)", "m"),
    ("NVL-00031", "PET in NGCS Đỏ - Tím", "PET In", 800, 12, "Màng PET in mẫu NGCS Đỏ - Tím (2 mẫu/trục)", "m"),
    ("NVL-00032", "PET in NGCS Hồng - Xanh", "PET In", 800, 12, "Màng PET in mẫu NGCS Hồng - Xanh Dương (2 mẫu/trục)", "m"),
    ("NVL-00033", "PET in Minh Râu Tím", "PET In", 780, 12, "Màng PET in mẫu Minh Râu Tím (Khổ 780mm)", "m"),
    ("NVL-00034", "PET in TopGia 2L", "PET In", 750, 12, "Màng PET in mẫu TopGia 2L (Khổ 750mm)", "m"),
    ("NVL-00035", "PET in Softy 3L", "PET In", 800, 12, "Màng PET in mẫu Softy 3L Nền Tím (Khổ 800mm)", "m"),
    ("NVL-00036", "PET in FUTA Xanh MT", "PET In", 900, 12, "Màng PET in FUTA Xanh mặt trước (Khổ 900mm)", "m"),
    ("NVL-00037", "PET in FUTA Xanh MS", "PET In", 900, 12, "Màng PET in FUTA Xanh mặt sau (Khổ 900mm)", "m"),
    ("NVL-00038", "PET in FUTA Tím MT", "PET In", 900, 12, "Màng PET in FUTA Tím mặt trước (Khổ 900mm)", "m"),
    ("NVL-00039", "PET in FUTA Tím MS", "PET In", 900, 12, "Màng PET in FUTA Tím mặt sau (Khổ 900mm)", "m"),
]
for code, name, layer, w, thick, desc, uom in pet_in_items:
    add_item(code, name, "Màng In Ống Đồng", uom, desc=desc, is_sales=0, is_purchase=1, spec={
        "packaging_type": "Màng In Ống Đồng", "custom_structure_layers": layer,
        "custom_thickness_mic": thick, "custom_film_width_mm": w, "custom_density_g_cm3": 1.34,
        "custom_print_method": "In Ống Đồng (Rotogravure)", "custom_print_colors": 6,
        "custom_design_variant": name.replace("PET in ", "")
    })

# 7. CUỘN MÀNG GHÉP BTP
btp_items = [
    ("BTP-00001", "Cuộn 888 - Phấn Thơm", "PET//PA/PE sữa", 800, 230, "Cuộn màng ghép hoàn thiện 3 lớp mẫu 888 Phấn Thơm (Input máy cắt túi hoặc bán cuộn)", "m"),
    ("BTP-00002", "Cuộn 888 - Huyền Bí", "PET//PA/PE sữa", 800, 230, "Cuộn màng ghép hoàn thiện 3 lớp mẫu 888 Huyền Bí Xanh", "m"),
    ("BTP-00003", "Cuộn 888 - Đam Mê", "PET//PA/PE sữa", 800, 230, "Cuộn màng ghép hoàn thiện 3 lớp mẫu 888 Đam Mê Đỏ", "m"),
    ("BTP-00004", "Cuộn NGCS Đỏ - Tím", "PET//PA/PE sữa", 800, 230, "Cuộn màng ghép hoàn thiện NGCS Đỏ - Tím", "m"),
    ("BTP-00005", "Cuộn NGCS Hồng - Xanh", "PET//PA/PE sữa", 800, 230, "Cuộn màng ghép hoàn thiện NGCS Hồng - Xanh", "m"),
    ("BTP-00006", "Cuộn Minh Râu Tím", "PET//PA/PE sữa", 780, 230, "Cuộn màng ghép hoàn thiện Minh Râu Tím", "m"),
    ("BTP-00007", "Cuộn TopGia 2L", "PET/PA/PE", 750, 190, "Cuộn màng ghép hoàn thiện TopGia 2L", "m"),
    ("BTP-00008", "Cuộn Softy 3L", "PET/PA/PE sữa", 800, 230, "Cuộn màng ghép hoàn thiện Softy 3L", "m"),
    ("BTP-00009", "Cuộn FUTA Xanh MT", "PET//PA/PE sữa", 900, 230, "Cuộn màng ghép FUTA Xanh mặt trước", "m"),
    ("BTP-00010", "Cuộn FUTA Xanh MS", "PET//PA/PE sữa", 900, 230, "Cuộn màng ghép FUTA Xanh mặt sau", "m"),
    ("BTP-00011", "Cuộn FUTA Tím MT", "PET//PA/PE sữa", 900, 230, "Cuộn màng ghép FUTA Tím mặt trước", "m"),
    ("BTP-00012", "Cuộn FUTA Tím MS", "PET//PA/PE sữa", 900, 230, "Cuộn màng ghép FUTA Tím mặt sau", "m"),
    ("BTP-00013", "Cuộn màng đáy 3.2Kg", "PET/PE sữa", 180, 150, "Cuộn màng ghép chuyên dụng cắt đáy đứng túi 3.2Kg", "m"),
]
for code, name, layer, w, thick, desc, uom in btp_items:
    add_item(code, name, "Cuộn Màng Ghép BTP", uom, desc=desc, spec={
        "packaging_type": "Cuộn Màng Ghép", "custom_structure_layers": layer,
        "custom_thickness_mic": thick, "custom_film_width_mm": w, "custom_density_g_cm3": 1.15,
        "custom_print_method": "In Ống Đồng (Rotogravure)", "custom_print_colors": 6,
        "custom_design_variant": name.replace("Cuộn ", "")
    })

# 8. PHỤ KIỆN BAO BÌ
pk_items = [
    ("NVL-00040", "Vòi 16mm", "Cái", "Vòi 16mm", "Vòi nhựa phi 16mm kèm nắp niêm phong chống tràn cho túi nước giặt (dùng cho cả đặt thẳng hoặc đặt xéo góc)."),
    ("NVL-00041", "Vòi 10mm", "Cái", "Vòi 10mm", "Vòi nhựa phi 10mm kèm nắp cho túi thể tích nhỏ / dung dịch mỹ phẩm."),
    ("NVL-00042", "Vòi 22mm", "Cái", "Vòi 22mm", "Vòi nhựa phi 22mm kèm nắp cho túi dung tích lớn 5L / hóa chất."),
    ("NVL-00043", "Dây Zipper", "m", "Không Vòi", "Cuộn dây khóa zipper dán nhiệt cho túi 3 biên / túi đáy đứng zipper."),
    ("NVL-00044", "Thùng carton đựng túi", "Cái", "Không Vòi", "Thùng carton 3 lớp / 5 lớp đóng gói giao hàng túi nước giặt."),
]
for code, name, uom, spout, desc in pk_items:
    is_spout = "Vòi" in name
    add_item(code, name, "Phụ Kiện Bao Bì", uom, desc=desc, is_sales=0, is_purchase=1, spec={
        "packaging_type": "Phụ Kiện", "custom_structure_layers": "Nhựa PP/PE Nguyên Sinh" if is_spout else "Carton",
        "custom_density_g_cm3": 0.91 if is_spout else 0.5,
        "custom_closure_type": "Vòi Rót" if is_spout else ("Khóa Zipper Thường" if "Zipper" in name else ""),
        "custom_spout_type": spout, "custom_spout_position": "Đa Năng (Thẳng hoặc Xéo)"
    })

# 9. CUSTOMER BRAND MATRIX
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

# Ghi CSV
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
