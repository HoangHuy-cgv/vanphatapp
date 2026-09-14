import os, sys, re, csv
from python_calamine import CalamineWorkbook

RAW_DIR = "data/raw-data"
OUT_DIR = "data/clean-data"
os.makedirs(OUT_DIR, exist_ok=True)

item_master_list = []
customer_brand_list = []

MASTER_HEADERS = [
    "item_code", "item_name", "custom_alias",
    "item_group", "stock_uom", "brand",
    "default_material_request_type", "standard_rate", "min_order_qty", "safety_stock",
    "disabled", "is_stock_item", "is_sales_item", "is_purchase_item",
    # Sếp chốt 2026-09-15: customer_ref_code cũ ĐA NGHĨA (TP=mã biến thể KH,
    # TRUC=mã laser NCC) + thiếu prefix custom_ → tách 2 custom field + ADR:
    # custom_customer_variant_code (TP) / custom_cylinder_code đã có (TRUC).
    "customer", "custom_customer_variant_code",
    "custom_structure_layers", "custom_thickness_mic", "custom_film_width_mm",
    "custom_pouch_width_mm", "custom_pouch_length_mm", "custom_gusset_mm", "custom_cut_length_mm",
    "custom_print_tech", "custom_accessory_spec", "custom_cylinder_item",
    "custom_cylinder_code", "custom_cylinder_length_mm", "custom_cylinder_circ_mm",
    "custom_cylinder_qty", "custom_cylinder_location",
    "description"
]

BRAND_HEADERS = [
    "customer_name", "brand_pattern", "color_variant",
    "applied_item_type", "default_item_code", "notes"
]


def normalize_layers(layers):
    if not layers:
        return ""
    # 1. Thống nhất dấu phân cách duy nhất là dấu gạch chéo đơn /
    s = str(layers).replace("//", "/")
    # 2. Cấm dùng PES -> Chuẩn hóa thành PE sữa
    s = re.sub(r'\bPES\b', 'PE sữa', s, flags=re.IGNORECASE)
    # 3. Cấm dùng LLDPE -> Chuẩn hóa thành PE trong
    s = re.sub(r'\bLLDPE\b', 'PE trong', s, flags=re.IGNORECASE)
    # 4. Chuẩn hóa PE đơn thuần thành PE trong (hoặc giữ nguyên nếu đã là PE sữa / PE trong)
    if s.endswith("/PE"):
        s = s[:-3] + "/PE trong"
    return s


def add_item(code, legal_name, alias, group, uom, brand="", desc="", req_type="Manufacture",
             standard_rate=0.0, min_order_qty=0, safety_stock=0, disabled=0,
             is_stock=1, is_sales=1, is_purchase=0, customer="", ref="",
             layers="", thick=0, film_w=0, pw=0, pl=0, gusset=0, cut_l=0,
             print_tech="Không in", accessory="", cyl_item="",
             cyl_code="", cyl_len=0, cyl_circ=0, cyl_qty=0, cyl_loc=""):
    item_master_list.append({
        "item_code": code,
        "item_name": legal_name,
        "custom_alias": alias,
        "item_group": group,
        "stock_uom": uom,
        "brand": brand,
        "default_material_request_type": req_type,
        "standard_rate": standard_rate,
        "min_order_qty": min_order_qty,
        "safety_stock": safety_stock,
        "disabled": disabled,
        "is_stock_item": is_stock,
        "is_sales_item": is_sales,
        "is_purchase_item": is_purchase,
        "customer": customer,
        "custom_customer_variant_code": ref,
        "custom_structure_layers": normalize_layers(layers),
        "custom_thickness_mic": thick,
        "custom_film_width_mm": film_w,
        "custom_pouch_width_mm": pw,
        "custom_pouch_length_mm": pl,
        "custom_gusset_mm": gusset,
        "custom_cut_length_mm": cut_l,
        "custom_print_tech": print_tech,
        "custom_accessory_spec": accessory,
        "custom_cylinder_item": cyl_item,
        "custom_cylinder_code": cyl_code,
        "custom_cylinder_length_mm": cyl_len,
        "custom_cylinder_circ_mm": cyl_circ,
        "custom_cylinder_qty": cyl_qty,
        "custom_cylinder_location": cyl_loc,
        "description": desc
    })


# ==============================================================================
# 1. NHÓM TÚI NƯỚC GIẶT CÓ SẴN (NGCS - MTS)
# Căn cứ: Bảng giá nội bộ chính thức & quy cách sheet 'túi ngcs' (TỔNG HỢP ĐƠN HÀNG ĐÃ CỌC CHƯA GIAO.xlsx)
# ==============================================================================
ngcs_colors = [
    ("Đỏ", "Đam Mê"),
    ("Xanh", "Hoa Hồng"),
    ("Tím", "Nước Hoa"),
    ("Hồng", "Cá Tính"),
    ("Vàng", "Ban Mai"),
]
ngcs_sizes = [
    (1, "Nhỏ", "2L", 220, 600, 220, 280, 40, 6500.0, "PET/MPET/PA/PE sữa"),
    (6, "Trung", "3.2Kg", 230, 700, 280, 340, 45, 7368.0, "PET/PA/PE sữa"),
    (11, "Lớn", "3.8Kg", 250, 800, 300, 380, 50, 9400.0, "PET/MPET/PA/PE sữa"),
]
for start_idx, size_lbl, cap, thick, film_w, pw, pl, gusset, rate, layers in ngcs_sizes:
    for offset, (c, sf) in enumerate(ngcs_colors):
        idx = start_idx + offset
        code = f"NGCS-{idx:05d}"
        legal_name = f"Túi phôi nước giặt in sẵn {size_lbl.lower()} {cap} có vòi ({c})"
        alias = f"NGCS {size_lbl} {c} - {sf}"
        add_item(
            code=code, legal_name=legal_name, alias=alias,
            group="Túi Nước Giặt Có Sẵn (NGCS)", uom="Túi",
            brand="Vạn Phát", req_type="Manufacture",
            standard_rate=rate, min_order_qty=500, safety_stock=2000,
            layers=layers, thick=thick, film_w=film_w, pw=pw, pl=pl, gusset=gusset, cut_l=pl,
            print_tech="In trục ống đồng", accessory="Vòi 16mm"
        )

# ==============================================================================
# 2. NHÓM TÚI MÀNG ĐƠN DÙNG CHUNG (TMD - PTO / MUA NGOÀI NCC)
# Căn cứ: Các đơn đặt hàng docx/pdf trong data/raw-data/đơn đặt hàng/
# ==============================================================================
tmd_items = [
    ("TMD-00001", "Túi nilon HD quai thỏ 17x25cm", "HD quai thỏ 17x25", 170, 250, 45, "HDPE", 0, 65000.0),
    ("TMD-00002", "Túi nilon HD quai thỏ 26x40cm", "HD quai thỏ 26x40", 260, 400, 45, "HDPE", 0, 65000.0),
    ("TMD-00003", "Túi nilon HD quai thỏ 30x50cm", "HD quai thỏ 30x50", 300, 500, 50, "HDPE", 0, 66000.0),
    ("TMD-00004", "Túi nilon HD quai thỏ 26x43cm", "HD quai thỏ 26x43", 260, 430, 50, "HDPE", 0, 66000.0),
    ("TMD-00005", "Túi nilon HD quai thỏ 30x60cm", "HD quai thỏ 30x60", 300, 600, 55, "HDPE", 0, 66000.0),
    ("TMD-00006", "Túi nilon HD quai thỏ đáy vuông 30x20x30cm", "HD quai thỏ 30x20x30", 300, 300, 50, "HDPE", 100, 68000.0),
    ("TMD-00007", "Túi nilon PE hột xoài trắng sữa 20x30cm", "PE hột xoài 20x30", 200, 300, 60, "LDPE", 0, 64815.0),
    ("TMD-00008", "Túi nilon PE hột xoài trắng sữa 17x22cm", "PE hột xoài 17x22", 170, 220, 60, "LDPE", 0, 65000.0),
    ("TMD-00009", "Túi nilon PE hột xoài trắng sữa 30x42cm", "PE hột xoài 30x42", 300, 420, 70, "LDPE", 0, 65000.0),
    ("TMD-00010", "Túi nilon PP trong suốt 32x45cm", "PP 32x45", 320, 450, 70, "PP", 0, 61111.0),
    ("TMD-00011", "Túi nilon PE trơn bọc nệm 50x100cm", "PE 50x100", 500, 1000, 70, "LDPE", 0, 72222.0),
    ("TMD-00012", "Túi nilon PE phôi cây đàn 30x48.5cm", "PE Cây Đàn", 300, 485, 60, "LDPE", 0, 69444.0),
]
for code, legal_name, alias, w, l, thick, layers, gusset, rate in tmd_items:
    add_item(
        code=code, legal_name=legal_name, alias=alias, group="Túi Màng Đơn", uom="Kg", brand="Mua ngoài",
        req_type="Purchase", standard_rate=rate, min_order_qty=25, safety_stock=100, is_purchase=1,
        layers=layers, thick=thick, film_w=w * 2, pw=w, pl=l, gusset=gusset, cut_l=l,
        print_tech="In lụa", accessory=""
    )

# ==============================================================================
# 3. NHÓM TÚI MÀNG GHÉP ĐẶT RIÊNG (TP - MTO HOẶC MUA NGOÀI)
# Căn cứ: Sheet 'TÚI HD (2)' trong TỔNG HỢP ĐƠN HÀNG ĐÃ CỌC CHƯA GIAO.xlsx
#         và sheet 'Sheet1' trong THÔNG TIN TRỤC IN.xlsx
# ==============================================================================
custom_pouches = [
    # code, legal_name, alias, brand, cust, ref, cap, w, l, gusset, thick, film_w, layers, cyl_code, cyl_wh, cyl_l, cyl_c, cyl_q, accessory, print_tech, rate, req_type, desc
    # --- 888 3.2Kg DS Cosmetic (Doypack đáy đứng có vòi) ---
    ("TP-00001", "Túi đựng nước giặt 888 3.2Kg có vòi (Màu Hồng)", "888 3.2Kg Hồng", "888", "CÔNG TY CỔ PHẦN DS COSMETIC", "888-3.2KG-HONG", "3.2Kg", 280, 340, 45, 230, 700, "PET/PA/PE sữa", "G4006940", "Kho Kiến Tâm", 800, 564, 5, "Vòi 16mm", "In trục ống đồng", 5166.0, "Manufacture", ""),
    ("TP-00002", "Túi đựng nước giặt 888 3.2Kg có vòi (Màu Tím)", "888 3.2Kg Tím", "888", "CÔNG TY CỔ PHẦN DS COSMETIC", "888-3.2KG-TIM", "3.2Kg", 280, 340, 45, 230, 700, "PET/PA/PE sữa", "G4006961", "Kho Kiến Tâm", 800, 564, 5, "Vòi 16mm", "In trục ống đồng", 5166.0, "Manufacture", ""),
    ("TP-00003", "Túi đựng nước giặt 888 3.2Kg có vòi (Màu Đỏ)", "888 3.2Kg Đỏ", "888", "CÔNG TY CỔ PHẦN DS COSMETIC", "888-3.2KG-DO", "3.2Kg", 280, 340, 45, 230, 700, "PET/PA/PE sữa", "G4006960", "Kho Vạn Phát", 800, 564, 5, "Vòi 16mm", "In trục ống đồng", 5166.0, "Manufacture", ""),
    # --- 888 2Kg DS Cosmetic (Doypack đáy đứng có vòi) ---
    ("TP-00004", "Túi đựng nước giặt 888 2Kg có vòi (Màu Hồng)", "888 2Kg Hồng", "888", "CÔNG TY CỔ PHẦN DS COSMETIC", "888-2KG-HONG", "2Kg", 240, 300, 45, 210, 600, "PET/PA/PE sữa", "G4006677", "Kho Vạn Phát", 750, 484, 5, "Vòi 16mm", "In trục ống đồng", 4500.0, "Manufacture", ""),
    ("TP-00005", "Túi đựng nước giặt 888 2Kg có vòi (Màu Tím)", "888 2Kg Tím", "888", "CÔNG TY CỔ PHẦN DS COSMETIC", "888-2KG-TIM", "2Kg", 240, 300, 45, 210, 600, "PET/PA/PE sữa", "G4005893", "Kho Vạn Phát", 750, 484, 5, "Vòi 16mm", "In trục ống đồng", 4500.0, "Manufacture", ""),
    ("TP-00006", "Túi đựng nước giặt 888 2Kg có vòi (Màu Đỏ)", "888 2Kg Đỏ", "888", "CÔNG TY CỔ PHẦN DS COSMETIC", "888-2KG-DO", "2Kg", 240, 300, 45, 210, 600, "PET/PA/PE sữa", "G4005897", "Kho Vạn Phát", 750, 484, 5, "Vòi 16mm", "In trục ống đồng", 4500.0, "Manufacture", ""),
    # --- 888 0.6Kg Ngừng kinh doanh (Doypack đáy đứng nhỏ có vòi) ---
    ("TP-00007", "Túi đựng nước giặt 888 0.6Kg có vòi (Màu Hồng)", "888 0.6Kg Hồng", "888", "CÔNG TY CỔ PHẦN DS COSMETIC", "888-0.6KG-HONG", "0.6Kg", 180, 240, 35, 180, 450, "PET/PA/PE trong", "G4006660", "Kho Vạn Phát", 750, 456, 5, "Vòi 16mm", "In trục ống đồng", 2800.0, "Manufacture", "[NGỪNG KINH DOANH THƯƠNG MẠI] Bảo lưu lịch sử kỹ thuật và trục in."),
    ("TP-00008", "Túi đựng nước giặt 888 0.6Kg có vòi (Màu Tím)", "888 0.6Kg Tím", "888", "CÔNG TY CỔ PHẦN DS COSMETIC", "888-0.6KG-TIM", "0.6Kg", 180, 240, 35, 180, 450, "PET/PA/PE trong", "G4006655", "Kho Vạn Phát", 750, 456, 5, "Vòi 16mm", "In trục ống đồng", 2800.0, "Manufacture", "[NGỪNG KINH DOANH THƯƠNG MẠI] Bảo lưu lịch sử kỹ thuật và trục in."),
    ("TP-00009", "Túi đựng nước giặt 888 0.6Kg có vòi (Màu Đỏ)", "888 0.6Kg Đỏ", "888", "CÔNG TY CỔ PHẦN DS COSMETIC", "888-0.6KG-DO", "0.6Kg", 180, 240, 35, 180, 450, "PET/PA/PE trong", "G4005877", "Kho Vạn Phát", 750, 456, 6, "Vòi 16mm", "In trục ống đồng", 2800.0, "Manufacture", "[NGỪNG KINH DOANH THƯƠNG MẠI] Bảo lưu lịch sử kỹ thuật và trục in."),
    ("TP-00010", "Túi đựng nước lau sàn 888 0.6Kg có vòi", "NLS 888 0.6Kg", "888", "CÔNG TY CỔ PHẦN DS COSMETIC", "888-NLS-0.6KG", "0.6Kg", 180, 240, 35, 180, 450, "PET/PE trong", "G4012417", "Kho Vạn Phát", 750, 456, 6, "Vòi 16mm", "In trục ống đồng", 2500.0, "Manufacture", "[NGỪNG KINH DOANH THƯƠNG MẠI] Bảo lưu lịch sử kỹ thuật và trục in."),
    ("TP-00011", "Túi đựng nước rửa chén 888 0.6Kg có vòi", "NRC 888 0.6Kg", "888", "CÔNG TY CỔ PHẦN DS COSMETIC", "888-NRC-0.6KG", "0.6Kg", 180, 240, 35, 180, 450, "PET/PE trong", "G4012418", "Kho Vạn Phát", 750, 456, 5, "Vòi 16mm", "In trục ống đồng", 2500.0, "Manufacture", "[NGỪNG KINH DOANH THƯƠNG MẠI] Bảo lưu lịch sử kỹ thuật và trục in."),
    # --- Minh Râu 3.2Kg DS Cosmetic (Doypack đáy đứng có vòi) ---
    ("TP-00012", "Túi đựng nước giặt Minh Râu 3.2Kg có vòi (Màu Tím)", "Minh Râu 3.2Kg Tím", "Minh Râu", "CÔNG TY CỔ PHẦN DS COSMETIC", "MINHRAU-3.2KG-TIM", "3.2Kg", 280, 340, 45, 230, 700, "PET/PA/PE sữa", "G4005887", "Kho Kiến Tâm", 780, 564, 6, "Vòi 16mm", "In trục ống đồng", 5166.0, "Manufacture", ""),
    ("TP-00013", "Túi đựng nước giặt Minh Râu 3.2Kg có vòi (Màu Hồng)", "Minh Râu 3.2Kg Hồng", "Minh Râu", "CÔNG TY CỔ PHẦN DS COSMETIC", "MINHRAU-3.2KG-HONG", "3.2Kg", 280, 340, 45, 230, 700, "PET/PA/PE sữa", "G4005883", "Kho Kiến Tâm", 780, 564, 6, "Vòi 16mm", "In trục ống đồng", 5166.0, "Manufacture", ""),
    # --- Lamy 2Kg Eco Wipes (Doypack đáy đứng có vòi) ---
    ("TP-00014", "Túi đựng nước giặt xả Lamy 2Kg có vòi (Màu Vàng)", "Lamy 2Kg Vàng", "Lamy", "CÔNG TY CỔ PHẦN ECO WIPES VIỆT NAM", "LAMY-2KG-VANG", "2Kg", 240, 320, 40, 200, 600, "PET/MPET/PA/PE trong", "", "", "", "", "", "Vòi 16mm", "In trục ống đồng", 5056.0, "Manufacture", ""),
    ("TP-00015", "Túi đựng nước giặt xả Lamy 2Kg có vòi (Màu Xanh)", "Lamy 2Kg Xanh", "Lamy", "CÔNG TY CỔ PHẦN ECO WIPES VIỆT NAM", "LAMY-2KG-XANH", "2Kg", 240, 320, 40, 200, 600, "PET/MPET/PA/PE trong", "", "", "", "", "", "Vòi 16mm", "In trục ống đồng", 5056.0, "Manufacture", ""),
    # --- BABA 3.6Kg Anh Phát (Doypack đáy đứng lớn có vòi) ---
    ("TP-00016", "Túi đựng nước giặt BABA 3.6Kg có vòi", "BABA 3.6Kg", "BABA", "CÔNG TY TNHH MTV SX TM XNK ANH PHÁT", "BABA-3.6KG", "3.6Kg", 280, 380, 50, 230, 800, "PET/MPET/PA/PE sữa", "TRUC-BABA", "Kho Vạn Phát", 800, 564, 8, "Vòi 16mm", "In trục ống đồng", 6759.0, "Manufacture", ""),
    # --- Supergeo 5L Vietcoat (Doypack đáy đứng dung tích lớn có vòi) ---
    ("TP-00017", "Túi đựng keo dán gạch SUPERGEO 5L có vòi", "Supergeo 5L", "Supergeo", "CÔNG TY TNHH CÔNG NGHỆ VẬT LIỆU TIÊN PHONG VIETCOAT", "SUPERGEO-5L", "5L", 320, 340, 50, 240, 800, "PET/PA/PA/PE sữa", "TRUC-SUPERGEO", "Kho Vạn Phát", 800, 564, 6, "Vòi 16mm", "In trục ống đồng", 9685.0, "Manufacture", ""),
    # --- Xốt Phô Mai KOVAA 200g (Túi xếp đáy 4cm có vòi nhỏ 10mm) ---
    ("TP-00018", "Túi đựng xốt phô mai KOVAA 200g có vòi", "Xốt Pho Mai 200g", "KOVAA", "CÔNG TY TNHH SX THƯƠNG MẠI BAO BÌ KOVAA", "KOVAA-200G", "200g", 150, 220, 40, 150, 400, "PET/PA/PE sữa", "", "", "", "", "", "Vòi 10mm", "In trục ống đồng", 1944.0, "Manufacture", "Chịu nhiệt độ rót xốt nóng 70 - 80°C."),
    # --- TopGia MBTP (Túi phẳng màng bọc thực phẩm - KHÔNG ĐÁY) ---
    ("TP-00019", "Túi màng bọc thực phẩm TopGia", "TopGia MBTP", "TopGia", "CÔNG TY TNHH PHONG TÍN", "TOPGIA-MBTP", "Tiêu chuẩn", 200, 300, 0, 80, 420, "PET/PE trong", "", "", "", "", "", "", "In trục ống đồng", 1780.0, "Purchase", ""),
    # --- TopGia 1L Phong Tín (Doypack đáy đứng có vòi) ---
    ("TP-00020", "Túi đựng nước giặt TopGia 1L có vòi (Hoa Nắng)", "TopGia 1L Hoa Nắng", "TopGia", "CÔNG TY TNHH PHONG TÍN", "TOPGIA-1L-HN", "1L", 180, 250, 35, 190, 450, "PET/PA/PE trong", "G4011425", "Kho Kiến Tâm", 750, 404, 6, "Vòi 16mm", "In trục ống đồng", 2852.0, "Manufacture", ""),
    ("TP-00021", "Túi đựng nước giặt TopGia 1L có vòi (Đắm Say)", "TopGia 1L Đắm Say", "TopGia", "CÔNG TY TNHH PHONG TÍN", "TOPGIA-1L-DS", "1L", 180, 250, 35, 190, 450, "PET/PA/PE trong", "G4011427", "Kho Kiến Tâm", 750, 404, 6, "Vòi 16mm", "In trục ống đồng", 2852.0, "Manufacture", ""),
    # --- Softy 3L Amyco (Doypack đáy đứng có vòi) ---
    ("TP-00022", "Túi đựng nước giặt Softy 3L có vòi (Nền Tím)", "Softy 3L Tím", "Softy", "CÔNG TY TNHH SẢN XUẤT - XUẤT NHẬP KHẨU AMYCO", "SOFTY-3L-TIM", "3L", 280, 340, 45, 230, 700, "PET/PA/PE sữa", "", "", "", "", "", "Vòi 16mm", "In trục ống đồng", 6500.0, "Manufacture", ""),
    # --- Sachpoong (Doypack đáy đứng có vòi) ---
    ("TP-00023", "Túi đựng nước giặt Sachpoong 3.2Kg có vòi", "Sachpoong 3.2Kg", "Sachpoong", "Khách hàng Sachpoong", "SACHPOONG-3.2KG", "3.2Kg", 280, 340, 45, 230, 700, "PET/PA/PE sữa", "G4010806", "Kho Vạn Phát", 800, 564, 5, "Vòi 16mm", "In trục ống đồng", 6500.0, "Manufacture", ""),
    ("TP-00024", "Túi đựng nước giặt Sachpoong 0.6Kg có vòi", "Sachpoong 0.6Kg", "Sachpoong", "Khách hàng Sachpoong", "SACHPOONG-0.6KG", "0.6Kg", 180, 240, 35, 180, 450, "PET/PA/PE trong", "G4010805", "Kho Vạn Phát", 750, 456, 5, "Vòi 16mm", "In trục ống đồng", 2800.0, "Manufacture", ""),
    # --- Raptor Clean (Doypack đáy đứng nhỏ có vòi) ---
    ("TP-00025", "Túi đựng nước giặt Raptor Clean 0.6Kg có vòi", "Raptor Clean 0.6Kg", "Raptor Clean", "Khách hàng Raptor Clean", "RAPTOR-0.6KG", "0.6Kg", 180, 240, 35, 180, 450, "PET/PA/PE trong", "G4010947", "Kho Vạn Phát", 750, 456, 7, "Vòi 16mm", "In trục ống đồng", 2800.0, "Manufacture", ""),
    # --- Trần Quân 2Kg (Doypack đáy đứng có vòi) ---
    ("TP-00026", "Túi đựng nước giặt Trần Quân 2Kg có vòi", "Trần Quân 2Kg", "Trần Quân", "Khách hàng Trần Quân", "TRANQUAN-2KG", "2Kg", 240, 300, 45, 210, 600, "PET/PA/PE sữa", "G4011409", "Kho Vạn Phát", 750, 484, 4, "Vòi 16mm", "In trục ống đồng", 4500.0, "Manufacture", ""),
    # --- DPClean 0.6Kg (Doypack đáy đứng nhỏ có vòi) ---
    ("TP-00027", "Túi đựng nước giặt DPClean 0.6Kg có vòi", "DPClean 0.6Kg", "DPClean", "Khách hàng DPClean", "DPCLEAN-0.6KG", "0.6Kg", 180, 240, 35, 180, 450, "PET/PA/PE trong", "G4011542", "Kho Vạn Phát", 750, 456, 5, "Vòi 16mm", "In trục ống đồng", 2800.0, "Manufacture", ""),
    # --- Bluum 3Kg (Doypack đáy đứng có vòi) ---
    ("TP-00028", "Túi đựng nước giặt Bluum 3Kg có vòi (Màu Đen)", "Bluum 3Kg Đen", "Bluum", "Khách hàng Bluum", "BLUUM-3KG-DEN", "3Kg", 280, 340, 45, 230, 700, "PET/PA/PE sữa", "G4012179", "Kho Vạn Phát", 800, 564, 5, "Vòi 16mm", "In trục ống đồng", 6500.0, "Manufacture", ""),
    ("TP-00029", "Túi đựng nước giặt Bluum 3Kg có vòi (Màu Xanh)", "Bluum 3Kg Xanh", "Bluum", "Khách hàng Bluum", "BLUUM-3KG-XANH", "3Kg", 280, 340, 45, 230, 700, "PET/PA/PE sữa", "G4012178", "Kho Vạn Phát", 800, 564, 6, "Vòi 16mm", "In trục ống đồng", 6500.0, "Manufacture", ""),
    # --- Premium 3.2Kg (Doypack đáy đứng có vòi) ---
    ("TP-00030", "Túi đựng nước giặt Premium 3.2Kg có vòi (Màu Tím)", "Premium 3.2Kg Tím", "Premium", "Khách hàng Premium", "PREMIUM-3.2KG-TIM", "3.2Kg", 280, 340, 45, 230, 700, "PET/PA/PE sữa", "G4006905", "Kho Kiến Tâm", 800, 564, 5, "Vòi 16mm", "In trục ống đồng", 6500.0, "Manufacture", ""),
    ("TP-00031", "Túi đựng nước giặt Premium 3.2Kg có vòi (Màu Đỏ)", "Premium 3.2Kg Đỏ", "Premium", "Khách hàng Premium", "PREMIUM-3.2KG-DO", "3.2Kg", 280, 340, 45, 230, 700, "PET/PA/PE sữa", "G4006924", "Kho Vạn Phát", 800, 564, 5, "Vòi 16mm", "In trục ống đồng", 6500.0, "Manufacture", ""),
    # --- Yumi Care, Sofia, Clean 3.6L (Doypack đáy đứng lớn có vòi) ---
    ("TP-00032", "Túi đựng nước giặt Yumi Care 3.6L có vòi", "Yumi Care 3.6L", "Yumi Care", "Khách hàng Yumi Care", "YUMICARE-3.6L", "3.6L", 280, 350, 45, 230, 700, "PET/PA/PE sữa", "G631383", "Kho Vạn Phát", 900, 568, 5, "Vòi 16mm", "In trục ống đồng", 7200.0, "Manufacture", ""),
    ("TP-00033", "Túi đựng nước giặt Sofia 3Kg có vòi (Hương LyLy)", "Sofia 3Kg Xanh", "Sofia", "CÔNG TY CỔ PHẦN EZ COSMETIC VIỆT NAM – CHI NHÁNH LONG AN", "SOFIA-3KG-XANH", "3Kg", 280, 340, 45, 230, 700, "PET/PA/PE sữa", "G4002697", "Kho Vạn Phát", 850, 526, 5, "Vòi 16mm", "In trục ống đồng", 6500.0, "Manufacture", ""),
    ("TP-00034", "Túi đựng nước giặt Clean 3.6L có vòi", "Clean 3.6L", "Clean", "Khách hàng Clean", "CLEAN-3.6L", "3.6L", 280, 350, 45, 230, 700, "PET/PA/PE sữa", "Z418556", "Kho Vạn Phát", 900, 568, 8, "Vòi 16mm", "In trục ống đồng", 7200.0, "Manufacture", ""),
    ("TP-00035", "Túi đựng nước giặt Clean 2L có vòi", "Clean 2L", "Clean", "Khách hàng Clean", "CLEAN-2L", "2L", 240, 300, 45, 210, 600, "PET/PA/PE sữa", "G630657", "Kho Vạn Phát", 800, 466, 8, "Vòi 16mm", "In trục ống đồng", 4500.0, "Manufacture", ""),
    ("TP-00036", "Túi đựng nước giặt Futa True 3Kg có vòi", "Futa True 3Kg", "Futa True", "CÔNG TY TNHH MTV TM TRANG UYÊN", "FUTA-3KG", "3Kg", 280, 340, 45, 230, 700, "PET/PA/PE sữa", "G4013050", "Kho Trang Tín", 900, 544, 6, "Vòi 16mm", "In trục ống đồng", 6500.0, "Manufacture", ""),
    ("TP-00037", "Túi đựng nước giặt Chakari Louis 3.2Kg có vòi", "Chakari Louis 3.2Kg", "Chakari", "Khách hàng Chakari", "CHAKARI-3.2KG", "3.2Kg", 280, 340, 45, 230, 700, "PET/PA/PE sữa", "G4014585", "Kho Trang Tín", 850, 846, 7, "Vòi 16mm", "In trục ống đồng", 6500.0, "Manufacture", ""),
    # --- Chloe'ly 2L (Doypack đáy đứng có vòi) ---
    ("TP-00038", "Túi đựng nước giặt CHLOE'LY 2L có vòi", "Chloe'ly 2L", "Chloe'ly", "CÔNG TY TNHH SẢN XUẤT - XUẤT NHẬP KHẨU AMYCO", "CHLOELY-2L", "2L", 240, 300, 45, 210, 600, "PET/MPET/PA/PE sữa", "", "", "", "", "", "Vòi 16mm", "In trục ống đồng", 5074.0, "Manufacture", ""),
    # --- SKX Đậu Nành (Túi phẳng 3 biên OPPMalt/PE trong - KHÔNG ĐÁY) ---
    ("TP-00039", "Túi đựng hạt đậu dinh dưỡng SKX 16x23.5cm", "SKX Đậu Nành", "SKX", "CÔNG TY CỔ PHẦN DINH DƯỠNG SKX", "SKX-DAUNANH", "500g", 160, 235, 0, 160, 340, "OPPMalt/PE trong", "G652829", "Kho Vạn Phát", 650, 470, 4, "", "In trục ống đồng", 1290.0, "Manufacture", ""),
    # --- ENZY FOOD (Túi 3 biên PET/AL/PE trong có khóa zipper - KHÔNG ĐÁY) ---
    ("TP-00040", "Túi đựng hạt nêm Enzy 900g có zipper", "Enzy Hạt Nêm 900g", "Enzy", "CÔNG TY TNHH ENZY FOOD", "ENZY-900G", "900g", 250, 300, 0, 150, 520, "PET/AL/PE trong", "G4012180", "Kho Vạn Phát", 750, 500, 6, "Khóa Zipper", "In trục ống đồng", 3963.0, "Manufacture", ""),
    ("TP-00041", "Túi đựng hạt nêm Enzy 450g có zipper", "Enzy Hạt Nêm 450g", "Enzy", "CÔNG TY TNHH ENZY FOOD", "ENZY-450G", "450g", 200, 260, 0, 140, 420, "PET/AL/PE trong", "", "", "", "", "", "Khóa Zipper", "In trục ống đồng", 3037.0, "Manufacture", ""),
    ("TP-00042", "Túi đựng hạt nêm Enzy 220g có zipper", "Enzy Hạt Nêm 220g", "Enzy", "CÔNG TY TNHH ENZY FOOD", "ENZY-220G", "220g", 170, 220, 0, 120, 360, "PET/AL/PE trong", "", "", "", "", "", "Khóa Zipper", "In trục ống đồng", 2111.0, "Manufacture", ""),
    ("TP-00043", "Túi đựng gia vị rắc cơm vị hải sản Enzy 11x17cm", "Enzy Rắc Cơm 11x17", "Enzy", "CÔNG TY TNHH ENZY FOOD", "ENZY-RACCOM", "100g", 110, 170, 0, 100, 240, "PET/AL/PE trong", "", "", "", "", "", "Khóa Zipper", "In trục ống đồng", 1315.0, "Manufacture", ""),
    # --- Trang Uyên 2L & Sofia 2L ---
    ("TP-00044", "Túi đựng nước giặt Trang Uyên 2L có vòi", "Trang Uyên 2L", "Trang Uyên", "CÔNG TY TNHH MTV TM TRANG UYÊN", "TRANGUYEN-2L", "2L", 240, 300, 40, 200, 600, "PET/PA/PE sữa", "", "", "", "", "", "Vòi 16mm", "In offset (Không trục)", 6880.0, "Manufacture", "Công nghệ in offset không trục."),
    ("TP-00045", "Túi đựng nước giặt xả Sofia 2L có vòi (Hương Ngọc Lan)", "Sofia 2L Ngọc Lan", "Sofia", "CÔNG TY CỔ PHẦN EZ COSMETIC VIỆT NAM – CHI NHÁNH LONG AN", "SOFIA-2L-NL", "2L", 240, 300, 45, 210, 600, "PET/PA/PE sữa", "TRUC-SOFIA2L", "Kho Vạn Phát", 750, 484, 5, "Vòi 16mm", "In trục ống đồng", 5537.0, "Manufacture", ""),
]

discontinued_codes = {"TP-00007", "TP-00008", "TP-00009", "TP-00010", "TP-00011"}
for item in custom_pouches:
    (code, legal_name, alias, brand, cust, ref, cap, w, l, gusset, thick, film_w, layers,
     cyl_code, cyl_wh, cyl_l, cyl_c, cyl_q, accessory, print_tech, rate, req_type, note) = item
    cyl_item = f"TRUC-{cyl_code}" if cyl_code and cyl_code not in ["TRUC-BABA", "TRUC-SUPERGEO", "TRUC-SOFIA2L"] else (cyl_code if cyl_code else "")
    dis = code in discontinued_codes
    add_item(
        code=code, legal_name=legal_name, alias=alias, group="Túi Màng Ghép Đặt Riêng", uom="Túi", brand=brand,
        desc=note, req_type=req_type, standard_rate=rate, min_order_qty=5000, safety_stock=0,
        disabled=1 if dis else 0, is_sales=0 if dis else 1, is_purchase=1 if req_type == "Purchase" else 0,
        customer=cust, ref=ref,
        layers=layers, thick=thick, film_w=film_w, pw=w, pl=l, gusset=gusset, cut_l=l,
        print_tech=print_tech, accessory=accessory, cyl_item=cyl_item
    )

# ==============================================================================
# 4. NHÓM TRỤC IN ỐNG ĐỒNG (TRUC - CÔNG CỤ TRỤC IN)
# Căn cứ: File raw-data/THÔNG TIN TRỤC IN.xlsx (Sheet1)
# ==============================================================================
def clean_cylinder_title(raw_sp, ma_truc):
    text = raw_sp.strip()
    text = re.sub(r'\s+', ' ', text)

    # Trim packaging type prefixes while preserving product subcategory
    pats = [
        r'^TÚI NƯỚC GIẶT XẢ\s+',
        r'^TÚI NƯỚC GIẶT\s+',
        r'^TÚI NƯỚC LAU SÀN\s+',
        r'^TÚI NƯỚC RỬA CHÉN\s+',
        r'^TÚI ĐỰNG\s+',
        r'^CUỘN MÀNG\s+',
        r'^TÚI MÀNG\s+',
        r'^TÚI\s+',
        r'^MÀNG\s+',
    ]
    is_lau_san = 'LAU SÀN' in text.upper()
    is_rua_chen = 'RỬA CHÉN' in text.upper()

    for p in pats:
        if re.search(p, text, flags=re.IGNORECASE):
            text = re.sub(p, '', text, flags=re.IGNORECASE)
            break

    if is_lau_san and not text.upper().startswith('LAU SÀN'):
        text = 'Lau Sàn ' + text
    elif is_rua_chen and not text.upper().startswith('RỬA CHÉN'):
        text = 'Rửa Chén ' + text

    # Remove internal technical bracketed notes
    text = re.sub(r'\s*\([^)]*(KT|MÀU|MẪU|ZIPPER|PHỦ MỜ|TRỤC CŨ|ĐÁY ĐỨNG|TIỆT TRÙNG|4 LỚP|24\*30|22\*28)[^)]*\)', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\s*-\s*IN\s+\d+\s+MÀU.*', '', text, flags=re.IGNORECASE)
    text = text.strip(' -+')

    def title_word(w):
        wu = w.upper()
        if re.match(r'^\d+(\.\d+)?(KG|G|L|ML)$', wu):
            num = re.search(r'^\d+(\.\d+)?', wu).group(0)
            unit = wu[len(num):]
            unit_str = 'Kg' if unit == 'KG' else ('g' if unit == 'G' else ('L' if unit == 'L' else 'ml'))
            return f'{num}{unit_str}'
        if wu in ['SKX', 'EZ', 'BABA', 'BOPP', 'OPP', 'PET', 'PA', 'PE', 'MBTP']:
            return wu
        if '(' in w or ')' in w or '+' in w:
            return w.title()
        return w.capitalize()

    words = [w for w in text.split(' ') if w]
    clean_words = [title_word(w) for w in words]
    title = ' '.join(clean_words)
    title = re.sub(r'\s*-\s*', ' ', title).strip()

    legal_name = f"Bộ trục in ống đồng {title}"
    alias = f"Trục {title}"
    return legal_name, alias

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
    legal_name, alias = clean_cylinder_title(sp, ma_truc)
    # TRUC: mã laser NCC chỉ nằm ở custom_cylinder_code (chính chủ);
    # custom_customer_variant_code để trống (dành cho TP = mã biến thể KH).
    add_item(
        code=item_code, legal_name=legal_name, alias=alias, group="Trục In Ống Đồng", uom="Cây", brand="Trục in",
        desc=note, req_type="Purchase", standard_rate=3000000.0, is_purchase=1, ref="",
        layers="Thép mạ đồng crom", print_tech="In trục ống đồng",
        cyl_code=ma_truc,
        cyl_len=cd if isinstance(cd, (int, float)) else 0,
        cyl_circ=cv if isinstance(cv, (int, float)) else 0,
        cyl_qty=sl if isinstance(sl, int) else (int(sl) if str(sl).isdigit() else 0),
        cyl_loc=f"Kho {kho}" if kho else "Kho Vạn Phát"
    )

# Thêm 3 bộ trục mới từ đơn cọc
additional_cylinders = [
    ("TRUC-SUPERGEO", "Bộ trục in ống đồng Supergeo 5L", "Trục Supergeo 5L", "TRUC-SUPERGEO", 6, 800, 564, "Kho Vạn Phát", 3800000.0),
    ("TRUC-BABA", "Bộ trục in ống đồng BABA 3.6Kg", "Trục BABA 3.6Kg", "TRUC-BABA", 8, 800, 564, "Kho Vạn Phát", 3148148.0),
    ("TRUC-SOFIA2L", "Bộ trục in ống đồng sửa mẫu Sofia 2L", "Trục Sửa Sofia 2L", "TRUC-SOFIA2L", 2, 750, 484, "Kho Vạn Phát", 2700000.0),
]
for c_code, c_legal, c_alias, c_laser, c_qty, c_len, c_circ, c_loc, c_rate in additional_cylinders:
    add_item(
        code=c_code, legal_name=c_legal, alias=c_alias, group="Trục In Ống Đồng", uom="Cây", brand="Trục in",
        desc="", req_type="Purchase", standard_rate=c_rate, is_purchase=1, ref="",
        layers="Thép mạ đồng crom", print_tech="In trục ống đồng",
        cyl_code=c_laser, cyl_len=c_len, cyl_circ=c_circ, cyl_qty=c_qty, cyl_loc=c_loc
    )

# ==============================================================================
# 5. NHÓM MÀNG THÔ NVL & HÓA CHẤT KEO GHÉP
# Căn cứ: Sheet 'MÃ NVL' trong Nhap xuat ton NVL-T9.xlsx và MÀNG.xlsx
# ==============================================================================
nvl_items = [
    ("NVL-00001", "Cuộn màng PE sữa khổ 700mm dày 160mic", "PE sữa K700 160mic", "PE sữa", 160, 700, "Kg", 58000.0),
    ("NVL-00002", "Cuộn màng PE sữa khổ 700mm dày 190mic", "PE sữa K700 190mic", "PE sữa", 190, 700, "Kg", 58000.0),
    ("NVL-00003", "Cuộn màng PE sữa khổ 740mm dày 190mic", "PE sữa K740 190mic", "PE sữa", 190, 740, "Kg", 58000.0),
    ("NVL-00004", "Cuộn màng PE sữa khổ 750mm dày 190mic", "PE sữa K750 190mic", "PE sữa", 190, 750, "Kg", 58000.0),
    ("NVL-00005", "Cuộn màng PE sữa khổ 740mm dày 50mic", "PE sữa K740 50mic", "PE sữa", 50, 740, "Kg", 62000.0),
    ("NVL-00006", "Cuộn màng PA khổ 700mm dày 15mic", "PA K700 15mic", "PA", 15, 700, "Kg", 78000.0),
    ("NVL-00007", "Cuộn màng PA khổ 740mm dày 15mic", "PA K740 15mic", "PA", 15, 740, "Kg", 78000.0),
    ("NVL-00008", "Cuộn màng PA khổ 760mm dày 15mic", "PA K760 15mic", "PA", 15, 760, "Kg", 78000.0),
    ("NVL-00009", "Cuộn màng PA khổ 800mm dày 15mic", "PA K800 15mic", "PA", 15, 800, "Kg", 78000.0),
    ("NVL-00010", "Cuộn màng PA khổ 380mm dày 15mic", "PA K380 15mic", "PA", 15, 380, "Kg", 78000.0),
    ("NVL-00011", "Cuộn màng PET khổ 560mm dày 12mic", "PET K560 12mic", "PET", 12, 560, "Kg", 48000.0),
    ("NVL-00012", "Cuộn màng PET khổ 610mm dày 12mic", "PET K610 12mic", "PET", 12, 610, "Kg", 48000.0),
    ("NVL-00013", "Cuộn màng PET khổ 700mm dày 12mic", "PET K700 12mic", "PET", 12, 700, "Kg", 48000.0),
    ("NVL-00014", "Cuộn màng PET khổ 740mm dày 12mic", "PET K740 12mic", "PET", 12, 740, "Kg", 48000.0),
    ("NVL-00015", "Cuộn màng PET khổ 800mm dày 12mic", "PET K800 12mic", "PET", 12, 800, "Kg", 48000.0),
    ("NVL-00016", "Cuộn màng PET khổ 790mm dày 190mic", "PET K790 190mic", "PET", 190, 790, "Kg", 52000.0),
    ("NVL-00017", "Cuộn màng MPET khổ 540mm dày 12mic", "MPET K540 12mic", "MPET", 12, 540, "Kg", 55000.0),
    ("NVL-00018", "Cuộn màng MPET khổ 800mm dày 12mic", "MPET K800 12mic", "MPET", 12, 800, "Kg", 55000.0),
    ("NVL-00019", "Cuộn màng nhôm AL khổ 560mm dày 6mic", "AL K560 6mic", "AL", 6, 560, "Kg", 120000.0),
    ("NVL-00020", "Cuộn màng PE trong khổ 720mm dày 70mic", "PE trong K720 70mic", "PE trong", 70, 720, "Kg", 56000.0),
    ("NVL-00021", "Cuộn màng PE trong khổ 660mm dày 75mic", "PE trong K660 75mic", "PE trong", 75, 660, "Kg", 56000.0),
    ("NVL-00022", "Cuộn màng PE trong khổ 700mm dày 150mic", "PE trong K700 150mic", "PE trong", 150, 700, "Kg", 56000.0),
    ("NVL-00023", "Cuộn màng OPP khổ 375mm dày 30mic", "OPP K375 30mic", "OPP", 30, 375, "Kg", 52000.0),
    ("NVL-00024", "Cuộn màng ngọc BOPP khổ 800mm dày 40mic", "Màng Ngọc K800 40mic", "Pearlescent BOPP", 40, 800, "Kg", 58000.0),
    ("NVL-00025", "Keo ghép màng Polyurethane D-9700", "Keo D-9700", "Keo D-9700", 0, 0, "Kg", 85000.0),
    ("NVL-00026", "Chất đóng rắn keo ghép CL-3192K", "Chất Đóng Rắn CL-3192K", "CL-3192K", 0, 0, "Kg", 110000.0),
    ("NVL-00027", "Dung môi công nghiệp Ethyl Acetate (EA)", "Dung Môi EA", "Ethyl Acetate", 0, 0, "Kg", 32000.0),
]
for code, legal_name, alias, layer, thick, w, uom, rate in nvl_items:
    is_chem = code in ["NVL-00025", "NVL-00026", "NVL-00027"]
    grp = "Hóa Chất & Keo Ghép" if is_chem else "Màng Thô NVL"
    add_item(
        code=code, legal_name=legal_name, alias=alias, group=grp, uom=uom, brand="NVL",
        req_type="Purchase", standard_rate=rate, is_sales=0, is_purchase=1,
        layers=layer, thick=thick, film_w=w
    )

# ==============================================================================
# 6. NHÓM MÀNG IN NVL (MUA TỪ NCC IN VỀ GHÉP)
# Căn cứ: Sheet 'MÃ NVL' (A01 - A16) trong Nhap xuat ton NVL-T9.xlsx
# ==============================================================================
pet_in_items = [
    ("NVL-00028", "Cuộn màng PET in ống đồng mẫu 888 Phấn Thơm khổ 800mm", "PET in 888 Phấn Thơm", "PET in", 800, 12, "m", 4200.0),
    ("NVL-00029", "Cuộn màng PET in ống đồng mẫu 888 Huyền Bí Xanh khổ 800mm", "PET in 888 Huyền Bí", "PET in", 800, 12, "m", 4200.0),
    ("NVL-00030", "Cuộn màng PET in ống đồng mẫu 888 Đam Mê Đỏ khổ 800mm", "PET in 888 Đam Mê", "PET in", 800, 12, "m", 4200.0),
    ("NVL-00031", "Cuộn màng PET in ống đồng mẫu NGCS Đỏ - Tím khổ 800mm", "PET in NGCS Đỏ-Tím", "PET in", 800, 12, "m", 4000.0),
    ("NVL-00032", "Cuộn màng PET in ống đồng mẫu NGCS Hồng - Xanh khổ 800mm", "PET in NGCS Hồng-Xanh", "PET in", 800, 12, "m", 4000.0),
    ("NVL-00033", "Cuộn màng PET in ống đồng mẫu Minh Râu Tím khổ 780mm", "PET in Minh Râu Tím", "PET in", 780, 12, "m", 4200.0),
    ("NVL-00034", "Cuộn màng PET in ống đồng mẫu TopGia 2L khổ 750mm", "PET in TopGia 2L", "PET in", 750, 12, "m", 4000.0),
    ("NVL-00035", "Cuộn màng PET in ống đồng mẫu Softy 3L Nền Tím khổ 800mm", "PET in Softy 3L", "PET in", 800, 12, "m", 4200.0),
    ("NVL-00036", "Cuộn màng PET in ống đồng FUTA Xanh mặt trước khổ 900mm", "PET in FUTA Xanh MT", "PET in", 900, 12, "m", 4500.0),
    ("NVL-00037", "Cuộn màng PET in ống đồng FUTA Xanh mặt sau khổ 900mm", "PET in FUTA Xanh MS", "PET in", 900, 12, "m", 4500.0),
    ("NVL-00038", "Cuộn màng PET in ống đồng FUTA Tím mặt trước khổ 900mm", "PET in FUTA Tím MT", "PET in", 900, 12, "m", 4500.0),
    ("NVL-00039", "Cuộn màng PET in ống đồng FUTA Tím mặt sau khổ 900mm", "PET in FUTA Tím MS", "PET in", 900, 12, "m", 4500.0),
    ("NVL-00045", "Cuộn màng PET in ống đồng mẫu BABA 3.6Kg khổ 800mm", "PET in BABA", "PET in", 800, 12, "m", 4500.0),
    ("NVL-00046", "Cuộn màng PET in ống đồng mẫu thực phẩm Năm Tàu khổ 800mm", "PET in Năm Tàu", "PET in", 800, 12, "m", 4200.0),
    ("NVL-00047", "Cuộn màng PET in ống đồng mẫu TopGia 1L Đắm Say khổ 750mm", "PET in TopGia 1L Đắm Say", "PET in", 750, 12, "m", 4000.0),
]
for code, legal_name, alias, layer, w, thick, uom, rate in pet_in_items:
    add_item(
        code=code, legal_name=legal_name, alias=alias, group="Màng In Ống Đồng", uom=uom, brand="Màng in",
        req_type="Purchase", standard_rate=rate, is_sales=0, is_purchase=1,
        layers=layer, thick=thick, film_w=w, print_tech="In trục ống đồng"
    )

# ==============================================================================
# 7. NHÓM CUỘN MÀNG GHÉP BTP (XƯỞNG GHÉP XONG -> BÁN CUỘN HOẶC CẮT TÚI)
# Căn cứ: TIẾN ĐỘ SẢN XUẤT.xlsx (sheet THEO DÕI TỔNG)
# ==============================================================================
btp_items = [
    ("BTP-00001", "Cuộn màng ghép PET/PA/PE 3 lớp 888 Phấn Thơm khổ 800mm", "Cuộn 888 Phấn Thơm", "PET/PA/PE sữa", 800, 230, "m", 12500.0),
    ("BTP-00002", "Cuộn màng ghép PET/PA/PE 3 lớp 888 Huyền Bí Xanh khổ 800mm", "Cuộn 888 Huyền Bí", "PET/PA/PE sữa", 800, 230, "m", 12500.0),
    ("BTP-00003", "Cuộn màng ghép PET/PA/PE 3 lớp 888 Đam Mê Đỏ khổ 800mm", "Cuộn 888 Đam Mê", "PET/PA/PE sữa", 800, 230, "m", 12500.0),
    ("BTP-00004", "Cuộn màng ghép PET/PA/PE 3 lớp NGCS Đỏ - Tím khổ 800mm", "Cuộn NGCS Đỏ-Tím", "PET/PA/PE sữa", 800, 230, "m", 12000.0),
    ("BTP-00005", "Cuộn màng ghép PET/PA/PE 3 lớp NGCS Hồng - Xanh khổ 800mm", "Cuộn NGCS Hồng-Xanh", "PET/PA/PE sữa", 800, 230, "m", 12000.0),
    ("BTP-00006", "Cuộn màng ghép PET/PA/PE 3 lớp Minh Râu Tím khổ 780mm", "Cuộn Minh Râu Tím", "PET/PA/PE sữa", 780, 230, "m", 12500.0),
    ("BTP-00007", "Cuộn màng ghép PET/PA/PE 3 lớp TopGia 2L khổ 750mm", "Cuộn TopGia 2L", "PET/PA/PE trong", 750, 190, "m", 11000.0),
    ("BTP-00008", "Cuộn màng ghép PET/PA/PE 3 lớp Softy 3L khổ 800mm", "Cuộn Softy 3L", "PET/PA/PE sữa", 800, 230, "m", 12500.0),
    ("BTP-00009", "Cuộn màng ghép PET/PA/PE 3 lớp FUTA Xanh mặt trước khổ 900mm", "Cuộn FUTA Xanh MT", "PET/PA/PE sữa", 900, 230, "m", 13500.0),
    ("BTP-00010", "Cuộn màng ghép PET/PA/PE 3 lớp FUTA Xanh mặt sau khổ 900mm", "Cuộn FUTA Xanh MS", "PET/PA/PE sữa", 900, 230, "m", 13500.0),
    ("BTP-00011", "Cuộn màng ghép PET/PA/PE 3 lớp FUTA Tím mặt trước khổ 900mm", "Cuộn FUTA Tím MT", "PET/PA/PE sữa", 900, 230, "m", 13500.0),
    ("BTP-00012", "Cuộn màng ghép PET/PA/PE 3 lớp FUTA Tím mặt sau khổ 900mm", "Cuộn FUTA Tím MS", "PET/PA/PE sữa", 900, 230, "m", 13500.0),
    ("BTP-00013", "Cuộn màng ghép cắt đáy đứng túi 3.2Kg khổ 180mm", "Cuộn màng đáy 3.2Kg", "PET/PE sữa", 180, 150, "m", 5500.0),
    ("BTP-00014", "Cuộn màng ghép 4 lớp BABA 3.6Kg khổ 800mm", "Cuộn BABA 3.6Kg", "PET/MPET/PA/PE sữa", 800, 230, "m", 13000.0),
    ("BTP-00015", "Cuộn màng ghép thực phẩm Năm Tàu khổ 800mm", "Cuộn Năm Tàu", "PET/PA/PE trong", 800, 200, "m", 12000.0),
    ("BTP-00016", "Cuộn màng ghép TopGia 1L Đắm Say khổ 750mm", "Cuộn TopGia 1L Đắm Say", "PET/PA/PE trong", 750, 190, "m", 11000.0),
]
for code, legal_name, alias, layer, w, thick, uom, rate in btp_items:
    add_item(
        code=code, legal_name=legal_name, alias=alias, group="Cuộn Màng Ghép BTP", uom=uom, brand="Cuộn ghép",
        req_type="Manufacture", standard_rate=rate, is_sales=1, is_purchase=0,
        layers=layer, thick=thick, film_w=w, print_tech="In trục ống đồng"
    )

# ==============================================================================
# 8. NHÓM PHỤ KIỆN BAO BÌ (VẬT TƯ TRONG BOM)
# Căn cứ: Đơn cọc T8 và Nhap xuat ton NVL-T9.xlsx
# ==============================================================================
pk_items = [
    ("NVL-00040", "Vòi nhựa đóng gói phi 16mm kèm nắp chống tràn", "Vòi 16mm", "Cái", 600.0),
    ("NVL-00041", "Vòi nhựa đóng gói phi 10mm kèm nắp", "Vòi 10mm", "Cái", 500.0),
    ("NVL-00043", "Cuộn dây khóa zipper dán nhiệt miệng túi", "Dây Zipper", "m", 450.0),
    ("NVL-00044", "Thùng carton 5 lớp đóng gói giao hàng túi", "Thùng carton", "Cái", 18000.0),
]
for code, legal_name, alias, uom, rate in pk_items:
    add_item(
        code=code, legal_name=legal_name, alias=alias, group="Phụ Kiện Bao Bì", uom=uom, brand="Phụ kiện",
        req_type="Purchase", standard_rate=rate, is_sales=0, is_purchase=1,
        layers="Nhựa PP/PE hoặc Carton"
    )

# ==============================================================================
# 9. NHÓM PHẾ LIỆU THU HỒI
# Căn cứ: Mã P01, P02 trong Nhap xuat ton NVL-T9.xlsx
# ==============================================================================
scrap_items = [
    ("NVL-P01", "Phế liệu màng nhựa PE sữa thu hồi từ xén biên", "Phế liệu PE sữa", "Kg", 15000.0),
    ("NVL-P02", "Phế liệu màng ghép phức hợp thu hồi", "Phế liệu màng ghép", "Kg", 8000.0),
]
for code, legal_name, alias, uom, rate in scrap_items:
    add_item(
        code=code, legal_name=legal_name, alias=alias, group="Phế Liệu Thu Hồi", uom=uom, brand="Phế liệu",
        req_type="Manufacture", standard_rate=rate, is_sales=1, is_purchase=0
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

# XUẤT DUY NHẤT 1 FILE item_master.csv
write_csv("item_master.csv", item_master_list, MASTER_HEADERS)

# XÓA BỎ HOÀN TOÀN CÁC FILE THỪA LẠC HẬU
for old_f in ["item_spec.csv", "customer_brand_matrix.csv"]:
    old_p = os.path.join(OUT_DIR, old_f)
    if os.path.exists(old_p):
        os.remove(old_p)
        print(f" ĐÃ XÓA BỎ FILE THỪA: {old_p}")
