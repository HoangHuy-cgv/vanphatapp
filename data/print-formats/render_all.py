#!/usr/bin/env python3
"""Script render đồng loạt toàn bộ các Print Format chuẩn Native của Vạn Phát ra file PDF.
Sử dụng Playwright (Chromium headless) và Jinja2 để kết xuất chính xác 100% như ERPNext.
Tự động dọn dẹp file HTML tạm sau khi xuất xong.
"""
import os
import base64
from jinja2 import Environment, BaseLoader
from playwright.sync_api import sync_playwright

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class Doc:
    def __init__(self, d):
        self._d = d
    def __getattr__(self, name):
        val = self._d.get(name)
        if isinstance(val, list):
            return [Doc(x) if isinstance(x, dict) else x for x in val]
        return val
    def get(self, name, default=None):
        val = self._d.get(name, default)
        if isinstance(val, list):
            return [Doc(x) if isinstance(x, dict) else x for x in val]
        return val

class FrappeUtils:
    @staticmethod
    def formatdate(date_str, fmt="dd/MM/yyyy"):
        if not date_str:
            return ""
        parts = str(date_str).split("-")
        if len(parts) == 3:
            return f"{parts[2]}/{parts[1]}/{parts[0]}"
        return str(date_str)

class FrappeHelper:
    def __init__(self):
        self.utils = FrappeUtils()

def get_base64_uri(path, mime="image/png"):
    if not os.path.exists(path):
        return ""
    with open(path, "rb") as f:
        return f"data:{mime};base64,{base64.b64encode(f.read()).decode('utf-8')}"

def render_template_to_pdf(page, template_filename, doc_dict, output_pdf_name, header_html, logo_uri, pdf_format="A4", landscape=False):
    tpl_path = os.path.join(BASE_DIR, template_filename)
    with open(tpl_path, "r", encoding="utf-8") as f:
        tpl_raw = f.read()

    env = Environment(loader=BaseLoader())
    jinja_template = env.from_string(tpl_raw)
    body = jinja_template.render(doc=Doc(doc_dict), frappe=FrappeHelper(), watermark_uri=logo_uri)

    full_html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <title>{doc_dict.get('name')}</title>
</head>
<body style="padding: 6px 12px;">
  <!-- LETTER HEAD HEADER -->
  {header_html}

  <!-- BODY CONTENT -->
  {body}
</body>
</html>
"""
    tmp_html = os.path.join(BASE_DIR, f"tmp-{output_pdf_name}.html")
    with open(tmp_html, "w", encoding="utf-8") as f:
        f.write(full_html)

    page.goto(f"file://{tmp_html}", wait_until="networkidle")

    footer_tpl = '<div style="width: 100%; border-top: 1px solid #e1e4e8; padding-top: 3px; margin: 0 10mm; text-align: right; font-size: 8.5px; color: #888888; font-family: sans-serif;">Trang <span class="pageNumber"></span> / <span class="totalPages"></span></div>'
    out_pdf = os.path.join(BASE_DIR, output_pdf_name)
    page.pdf(
        path=out_pdf,
        format=pdf_format,
        landscape=landscape,
        print_background=True,
        display_header_footer=True,
        header_template="<div></div>",
        footer_template=footer_tpl,
        margin={"top": "8mm", "bottom": "12mm", "left": "10mm", "right": "10mm"}
    )
    if os.path.exists(tmp_html):
        os.remove(tmp_html)
    print(f"-> Xuất thành công: {out_pdf}")

def main():
    logo_path = os.path.join(BASE_DIR, "assets", "logo-vp.png")
    sample_design = os.path.join(BASE_DIR, "assets", "sample-design.jpg")
    logo_uri = get_base64_uri(logo_path, "image/png")
    design_uri = get_base64_uri(sample_design, "image/jpeg")
    tui_img_path = os.path.join(BASE_DIR, "..", "raw-data", "images_clean", "SOFTY-3KG-DOC.png")
    tui_design_uri = get_base64_uri(tui_img_path, "image/png") if os.path.exists(tui_img_path) else design_uri
    thanhtung_img_path = os.path.join(BASE_DIR, "..", "raw-data", "images_clean", "HD-QT-OC-KIEU-30X50.webp")
    thanhtung_design_uri = get_base64_uri(thanhtung_img_path, "image/webp") if os.path.exists(thanhtung_img_path) else design_uri

    # Load Letter Head
    with open(os.path.join(BASE_DIR, "letter-head.html"), "r", encoding="utf-8") as f:
        letter_head_raw = f.read()

    footer_marker = "<!-- ===== FOOTER HTML"
    part_h = letter_head_raw.split(footer_marker)[0]
    header_start = part_h.find('<div class="letter-head-header"')
    header_raw = part_h[header_start:].strip()
    env = Environment(loader=BaseLoader())
    lh_tpl = env.from_string(header_raw)
    header_html = lh_tpl.render(logo_uri=logo_uri)
    header_html = header_html.replace('/files/logo-vp.png', logo_uri)

    # =========================================================================
    # DỮ LIỆU THỰC TẾ: ĐƠN ĐẶT HÀNG (SALES ORDERS)
    # =========================================================================
    # 1.1. Đơn Đặt Hàng AMYCO (Nước giặt xả SOFTY 3L + Trục in 8 màu)
    so_amyco_data = {
        "name": "DH-2608-AMYCO",
        "transaction_date": "2026-08-18",
        "delivery_date": "2026-09-08",
        "customer_name": "CÔNG TY TNHH SX - XNK AMYCO",
        "tax_id": "0315487660",
        "contact_mobile": "0989.123.456",
        "shipping_address": "Lô B2-15, KCN Tây Bắc Củ Chi, Xã Tân An Hội, H. Củ Chi, TP. Hồ Chí Minh",
        "items": [
            {
                "item_name": "Túi đựng nước giặt xả cao cấp SOFTY 3 LÍT (Có gắn vòi TQ16)",
                "description": "Quy cách: 26 x 34 x Đáy 10 cm | Độ dày: 180 mic | Cấu trúc: PET12 / PA15 / LLDPE180 | In ống đồng 8 màu (Mẫu Tím - Hương Chuẩn Châu Âu).",
                "uom": "Túi",
                "qty": 30000,
                "rate": 6652.8,
                "amount": 199584000
            },
            {
                "item_name": "Trục in ống đồng kỹ thuật cao SOFTY 3L (Bộ 8 màu)",
                "description": "Khắc điện tử cao cấp, bảo hành 1,000,000 mét màng in. Bàn giao lưu kho kỹ thuật Vạn Phát.",
                "uom": "Trục",
                "qty": 8,
                "rate": 3240000,
                "amount": 25920000
            }
        ],
        "net_total": 225504000,
        "total_taxes_and_charges": 18040320,
        "grand_total": 243544320,
        "advance_paid": 20000000,
        "in_words": "Hai trăm bốn mươi ba triệu năm trăm bốn mươi bốn nghìn ba trăm hai mươi đồng.",
        "design_image": design_uri
    }

    # 1.2. Đơn Đặt Hàng DS888 (DS Cosmetic: Túi 888 Hồng, Túi 888 Tím, Túi Minh Râu Tím)
    so_ds888_data = {
        "name": "DH-2608-DS888",
        "transaction_date": "2026-08-20",
        "delivery_date": "2026-09-10",
        "customer_name": "CÔNG TY CỔ PHẦN DS COSMETIC",
        "tax_id": "0316789123",
        "contact_mobile": "0903.888.999",
        "shipping_address": "Số 45 Đường số 8, KDC Cityland Park Hills, P. 10, Q. Gò Vấp, TP. Hồ Chí Minh",
        "items": [
            {
                "item_name": "Túi 888 3.2KG Hồng - Dịu Nhẹ Cho Gia Đình",
                "description": "Quy cách: 28 x 36 x 12 cm | Dày: 190 mic | Cấu trúc: PET / MPET / LLDPE | Đóng gói 40 túi/thùng.",
                "uom": "Túi",
                "qty": 28000,
                "rate": 5166.67,
                "amount": 144666760
            },
            {
                "item_name": "Túi 888 3.2KG Tím - Hương Nước Hoa Huyền Bí",
                "description": "Quy cách: 28 x 36 x 12 cm | Dày: 190 mic | Cấu trúc: PET / MPET / LLDPE | Đóng gói 40 túi/thùng.",
                "uom": "Túi",
                "qty": 12000,
                "rate": 5166.67,
                "amount": 62000040
            },
            {
                "item_name": "Túi minh râu tím 3.2Kg",
                "description": "Quy cách: 28 x 36 x 12 cm | Dày: 190 mic | Cấu trúc: PET / MPET / LLDPE | Đóng gói 40 túi/thùng.",
                "uom": "Túi",
                "qty": 9600,
                "rate": 5166.67,
                "amount": 49600032
            }
        ],
        "net_total": 256266832,
        "total_taxes_and_charges": 20501347,
        "grand_total": 276768179,
        "in_words": "Hai trăm bảy mươi sáu triệu bảy trăm sáu mươi tám nghìn một trăm bảy mươi chín đồng.",
        "design_image": design_uri
    }

    # =========================================================================
    # DỮ LIỆU THỰC TẾ: 4 MẪU ĐƠN MUA HÀNG (PURCHASE ORDERS)
    # =========================================================================
    # 2.1. Đơn Đặt Sản Xuất Túi Thành Phẩm (Trang Tín - KÈM HÌNH TRANG 2)
    po_tui_data = {
        "name": "PO-TMG-2608-TRANGTIN",
        "transaction_date": "2026-08-20",
        "posting_date": "2026-08-20",
        "schedule_date": "2026-08-31",
        "supplier_name": "CÔNG TY CỔ PHẦN SẢN XUẤT BAO BÌ TRANG TÍN",
        "tax_id": "0314899123",
        "contact_mobile": "0938.999.888",
        "supplier_address": "Lô C4, KCN Đức Hòa 1, H. Đức Hòa, Tỉnh Long An",
        "representative": "ĐỖ MINH TRANG",
        "items": [
            {
                "item_name": "Túi nước giặt SOFTY 3L (chờ đóng vòi)",
                "description": "Cấu trúc màng PET12 / PA15 / LLDPE180. Túi ép 3 biên, chừa miệng theo dưỡng kỹ thuật để Vạn Phát về tự ép vòi TQ16.",
                "item_group": "TUI-GHEP",
                "custom_dimensions": "26 x 34 x Đáy 10 cm",
                "custom_thickness_mic": "180 mic",
                "uom": "Túi",
                "qty": 20000,
                "rate": 3200,
                "amount": 64000000
            },
            {
                "item_name": "Túi nước giặt BABA 3.6Kg (không vòi)",
                "description": "Cấu trúc PET / MPET / PA / PE trong. Túi xếp hông đáy đứng, ép kín 100% (không vòi).",
                "item_group": "TUI-GHEP",
                "custom_dimensions": "28 x 38 x Đáy 14 cm",
                "custom_thickness_mic": "210 mic",
                "uom": "Túi",
                "qty": 15000,
                "rate": 3800,
                "amount": 57000000
            }
        ],
        "net_total": 121000000,
        "total_taxes_and_charges": 9680000,
        "grand_total": 130680000,
        "in_words": "Một trăm ba mươi triệu sáu trăm tám mươi nghìn đồng chẵn.",
        "design_image": tui_design_uri
    }

    # 2.1b. Đơn Đặt In Lụa Gia Công Túi (Cơ sở Thanh Tùng - KÈM HÌNH MAQUETTE TRANG 2)
    po_tui_thanhtung_data = {
        "name": "PO-INLUA-2608-THANHTUNG",
        "transaction_date": "2026-08-19",
        "posting_date": "2026-08-19",
        "supplier_name": "CƠ SỞ IN ẤN BAO BÌ THANH TÙNG",
        "tax_id": "0314587660",
        "contact_mobile": "0903.874.782",
        "supplier_address": "39A Ấp 2, Long Sơn, Cần Đước, Long An",
        "representative": "NGUYỄN THANH TÙNG",
        "items": [
            {
                "item_name": "HD sữa quai thỏ: in 1 màu 1 mặt (Hải sản tươi sống Ốc Kiều)",
                "description": "Có chỉnh địa chỉ CN 1: Số 8 Trần Phú, xã Ngãi Giao, Tp Hồ Chí Minh. Mực in xanh đậm chuẩn mẫu.",
                "custom_dimensions": "30 x 50 cm",
                "uom": "Kg",
                "qty": 200,
                "rate": 55000,
                "amount": 11000000
            }
        ],
        "net_total": 11000000,
        "total_taxes_and_charges": 0,
        "grand_total": 11000000,
        "in_words": "Mười một triệu đồng chẵn.",
        "design_image": thanhtung_design_uri
    }

    # 2.1c. Đơn Đặt Mua Túi Màng Đơn (NCC Tạ Minh - 1 TRANG KHÔNG HÌNH, ĐVT: KG)
    po_taminh_data = {
        "name": "PO-TMD-2608-TAMINH",
        "transaction_date": "2026-08-28",
        "posting_date": "2026-08-28",
        "supplier_name": "CÔNG TY TNHH MỘT THÀNH VIÊN SẢN XUẤT THƯƠNG MẠI TẠ MINH",
        "tax_id": "0313617295",
        "contact_mobile": "0908.666.777",
        "supplier_address": "Lô C2, Đường số 3, KCN Vĩnh Lộc, Huyện Bình Chánh, TP.HCM",
        "representative": "TẠ THÀNH MINH",
        "items": [
            {
                "item_name": "Túi HD sữa Vạn An (đục quai hột xoài)",
                "description": "Phôi túi màng đơn HD trắng đục, xử lý corona đạt chuẩn in lụa.",
                "custom_dimensions": "20 x 30 cm",
                "uom": "Kg",
                "qty": 316.5,
                "rate": 50000,
                "amount": 15825000
            },
            {
                "item_name": "Túi HD sữa Vạn An (đục quai hột xoài)",
                "description": "Phôi túi màng đơn HD trắng đục, xử lý corona đạt chuẩn in lụa.",
                "custom_dimensions": "17 x 25 cm",
                "uom": "Kg",
                "qty": 300.0,
                "rate": 50000,
                "amount": 15000000
            },
            {
                "item_name": "Túi HD sữa Vạn An (đục quai hột xoài)",
                "description": "Phôi túi màng đơn HD trắng đục, xử lý corona đạt chuẩn in lụa.",
                "custom_dimensions": "26 x 40 cm",
                "uom": "Kg",
                "qty": 139.5,
                "rate": 50000,
                "amount": 6975000
            }
        ],
        "net_total": 37800000,
        "total_taxes_and_charges": 3024000,
        "grand_total": 40824000,
        "in_words": "Bốn mươi triệu tám trăm hai mươi bốn nghìn đồng chẵn."
    }

    # 2.2. Đơn Đặt In Gia Công Màng Ống Đồng - IGC (Tuệ Nhi - KÈM HÌNH TRANG 2)
    po_igc_data = {
        "name": "PO-IGC-2608-TUENHI",
        "transaction_date": "2026-08-22",
        "schedule_date": "2026-08-28",
        "supplier_name": "CÔNG TY TNHH SẢN XUẤT BAO BÌ NHỰA TUỆ NHI",
        "tax_id": "0302694611",
        "contact_mobile": "0938.258.948",
        "items": [
            {
                "item_name": "Cuộn màng PET 12 in 8 màu — Nước Giặt NGCS Đen Đam Mê",
                "description": "In theo bộ 8 trục Vạn Phát giao sang. Quấn mặt in vào trong, đúng bước mắt đọc sensor.",
                "item_group": "MANG-PET-IN",
                "custom_print_width_cm": "78",
                "custom_film_width_cm": "80",
                "custom_linear_meters": 12000,
                "custom_m2": 9600,
                "uom": "M2",
                "qty": 9600,
                "rate": 2800,
                "amount": 26880000
            },
            {
                "item_name": "Cuộn màng OPP in 3 màu — Chả Lụa Năm Tàu",
                "description": "Khổ in thành phẩm 35cm, khổ màng chạy 37cm. Canh chuẩn màu theo mẫu duyệt.",
                "item_group": "MANG-PET-IN",
                "custom_print_width_cm": "35",
                "custom_film_width_cm": "37",
                "custom_linear_meters": 8000,
                "custom_m2": 2960,
                "uom": "M2",
                "qty": 2960,
                "rate": 2600,
                "amount": 7696000
            }
        ],
        "net_total": 34576000,
        "total_taxes_and_charges": 2766080,
        "grand_total": 37342080,
        "in_words": "Ba mươi bảy triệu ba trăm bốn mươi hai nghìn không trăm tám mươi đồng.",
        "design_image": design_uri
    }

    # 2.3. Đơn Mua Màng Nguyên Liệu Mộc (Nam Sơn - 1 TRANG KHÔNG HÌNH)
    po_mang_data = {
        "name": "PO-MANG-2608-NAMSON",
        "transaction_date": "2026-08-21",
        "schedule_date": "2026-08-26",
        "supplier_name": "CÔNG TY TNHH THƯƠNG MẠI VÀ XNK NAM SƠN",
        "tax_id": "0302694611",
        "contact_mobile": "0908.123.456",
        "items": [
            {
                "item_name": "Màng PET",
                "description": "Xử lý Corona 1 mặt ≥ 42 dynes, độ phẳng cao, không tĩnh điện.",
                "item_group": "MANG-NVL",
                "custom_thickness_mic": 12,
                "custom_film_width_mm": 700,
                "custom_linear_meters": 12000,
                "uom": "Kg",
                "qty": 135.1,
                "rate": 47000,
                "amount": 6349700,
                "custom_note": "1 mặt corona"
            },
            {
                "item_name": "Màng MPET",
                "description": "Độ bám dính lớp mạ nhôm cao, cách ẩm và chắn ánh sáng tuyệt đối.",
                "item_group": "MANG-NVL",
                "custom_thickness_mic": 12,
                "custom_film_width_mm": 800,
                "custom_linear_meters": 12000,
                "uom": "Kg",
                "qty": 161.3,
                "rate": 57000,
                "amount": 9194100,
                "custom_note": "Mạ nhôm"
            },
            {
                "item_name": "Màng PA 2 mặt",
                "description": "Chuyên dùng ghép túi hút chân không thực phẩm đông lạnh.",
                "item_group": "MANG-NVL",
                "custom_thickness_mic": 15,
                "custom_film_width_mm": 800,
                "custom_linear_meters": 12000,
                "uom": "Kg",
                "qty": 164.2,
                "rate": 80000,
                "amount": 13136000,
                "custom_note": "Hút chân không"
            }
        ],
        "net_total": 28679800,
        "total_taxes_and_charges": 2294384,
        "grand_total": 30974184,
        "in_words": "Ba mươi triệu chín trăm bảy mươi tư nghìn một trăm tám mươi tư đồng."
    }

    # 2.4. Đơn Đặt Khắc Trục In Ống Đồng (Dong Yun - BẢNG 7 CỘT, TRANG 2 MAQUETTE KỸ THUẬT)
    po_truc_data = {
        "name": "PO-TRUC-2608-DONGYUN",
        "transaction_date": "2026-08-04",
        "posting_date": "2026-08-04",
        "schedule_date": "2026-08-09",
        "supplier_name": "CÔNG TY TNHH VIỆT NAM DONG YUN PLATE MAKING MIỀN NAM",
        "tax_id": "1100785988",
        "contact_mobile": "0272.377.9888",
        "supplier_address": "Lô B2-6, KCN Đức Hòa 1 - Hạnh Phúc, Xã Đức Hòa Đông, Huyện Đức Hòa, Tỉnh Long An",
        "representative": "DONG YUN",
        "items": [
            {
                "item_name": "Bộ trục in ống đồng — Túi nước giặt SOFTY 3L (Bộ 8 trục)",
                "description": "Khắc điện tử cao cấp theo file thiết kế duyệt tại Trang 2. Mạ crom cứng bảo vệ bề mặt chống ma sát.",
                "item_group": "NVL-TRUC-IN",
                "custom_dimensions": "Dài 850 mm x Chu vi 450 mm",
                "uom": "Trục",
                "qty": 8,
                "rate": 3300000,
                "amount": 26400000
            }
        ],
        "net_total": 26400000,
        "total_taxes_and_charges": 2112000,
        "grand_total": 28512000,
        "in_words": "Hai mươi tám triệu năm trăm mười hai nghìn đồng chẵn.",
        "design_image": tui_design_uri
    }

    # 2.5. Đơn Mua Hóa Chất & Hạt Nhựa (Sungdo Vina - 1 TRANG KHÔNG HÌNH)
    po_hoachat_data = {
        "name": "PO-HOACHAT-2608-SUNGDO",
        "transaction_date": "2026-08-24",
        "schedule_date": "2026-08-29",
        "supplier_name": "CÔNG TY TNHH MTV SUNGDO VINA",
        "tax_id": "3602456789",
        "contact_mobile": "0908.345.233",
        "subtitle": "ĐẶT MUA HÓA CHẤT & HẠT NHỰA",
        "supplier_address": "Lô 05F, Đường số 05, KCN Giang Điền, Xã Trảng Bom, Tỉnh Đồng Nai",
        "items": [
            {
                "item_name": "Keo ghép màng PU hai thành phần D-9822K",
                "description": "Chuyên dùng ghép màng bao bì khô (Dry lamination), bám dính cực tốt.",
                "item_group": "NVL-HOA-CHAT",
                "custom_dimensions": "Phuy sắt 200 kg",
                "uom": "Kg",
                "qty": 900,
                "rate": 78000,
                "amount": 70200000
            },
            {
                "item_name": "Chất đóng rắn keo ghép CL-3196K",
                "description": "Chất đóng rắn tương thích hoàn hảo với keo D-9822K, đạt chuẩn an toàn.",
                "item_group": "NVL-HOA-CHAT",
                "custom_dimensions": "Can thiếc 18 kg",
                "uom": "Kg",
                "qty": 180,
                "rate": 115000,
                "amount": 20700000
            },
            {
                "item_name": "Hạt nhựa nguyên sinh LLDPE Sabic 218WJ",
                "description": "Chỉ số MI 2.0, dùng cho máy thổi màng LLDPE trong xưởng Bình Chánh.",
                "item_group": "NVL-HAT",
                "custom_dimensions": "Bao 25 kg (Sabic)",
                "uom": "Kg",
                "qty": 2000,
                "rate": 32000,
                "amount": 64000000
            }
        ],
        "net_total": 154900000,
        "total_taxes_and_charges": 12392000,
        "grand_total": 167292000,
        "in_words": "Một trăm sáu mươi bảy triệu hai trăm chín mươi hai nghìn đồng chẵn."
    }

    # 2.6. Đơn Mua Vật Tư Phụ Liệu & Phụ Kiện Đóng Gói (Unlimited Access / Tiến Phát - 1 TRANG KHÔNG HÌNH)
    po_vattu_data = {
        "name": "PO-VATTU-2608-UNLIMITED",
        "transaction_date": "2026-08-25",
        "posting_date": "2026-08-25",
        "schedule_date": "2026-08-30",
        "subtitle": "ĐẶT MUA VẬT TƯ & PHỤ KIỆN ĐÓNG GÓI",
        "supplier_name": "CÔNG TY CỔ PHẦN QUỐC TẾ UNLIMITED ACCESS VIỆT NAM",
        "tax_id": "0316096435",
        "contact_mobile": "0912.888.777",
        "supplier_address": "Lô G3, Đường số 10, KCN Hải Sơn, Huyện Đức Hòa, Tỉnh Long An",
        "representative": "LÊ HOÀNG NAM",
        "items": [
            {
                "item_name": "Bộ vòi & nắp ren TQ16 (nhựa nguyên sinh)",
                "description": "Đầu vòi kèm nắp vặn ren kín, ép nhiệt vào mép túi nước giặt 3L.",
                "item_group": "NVL-BAO-BI",
                "custom_dimensions": "Đường kính Ø16 mm",
                "uom": "Bộ",
                "qty": 30000,
                "rate": 450,
                "amount": 13500000
            },
            {
                "item_name": "Thùng carton 5 lớp sóng BC (đựng túi nước giặt 3L)",
                "description": "Chịu lực xếp chồng 5 lớp, in flexo nhận diện thương hiệu Vạn Phát.",
                "item_group": "NVL-BAO-BI",
                "custom_dimensions": "58 x 38 x 28 cm",
                "uom": "Thùng",
                "qty": 1000,
                "rate": 16500,
                "amount": 16500000
            },
            {
                "item_name": "Băng keo trong dán thùng 5cm x 100 yard",
                "description": "Độ dính màng 50 mic, chuyên dùng đóng niêm phong thùng carton.",
                "item_group": "NVL-BAO-BI",
                "custom_dimensions": "Khổ 5 cm (50 mic)",
                "uom": "Cuộn",
                "qty": 120,
                "rate": 18000,
                "amount": 2160000
            }
        ],
        "net_total": 32160000,
        "total_taxes_and_charges": 2572800,
        "grand_total": 34732800,
        "in_words": "Ba mươi tư triệu bảy trăm ba mươi hai nghìn tám trăm đồng chẵn."
    }

    # =========================================================================
    # DỮ LIỆU THỰC TẾ: 1 MẪU PHIẾU XUẤT KHO (DELIVERY NOTE - A5 LANDSCAPE)
    # =========================================================================
    dn_ds888_data = {
        "name": "PXK-2608-00454",
        "posting_date": "2026-08-24",
        "against_sales_order": "DH-2608-DS888",
        "customer_name": "CÔNG TY CỔ PHẦN DS COSMETIC",
        "shipping_address": "Kho DS Cosmetic, 45 Đường số 8, KDC Cityland Park Hills, P. 10, Q. Gò Vấp, TP.HCM",
        "contact_mobile": "0903.888.999",
        "items": [
            {
                "item_name": "Túi 888 3.2KG Hồng - Dịu Nhẹ Cho Gia Đình",
                "description": "Quy cách: 28 x 36 x 12 cm | Dày 190 mic | Đóng thùng 40 túi/thùng (Tổng cộng 630 thùng)",
                "uom": "Túi",
                "qty": 25200,
                "remarks": "Đủ 630 thùng"
            },
            {
                "item_name": "Túi minh râu tím 3.2Kg",
                "description": "Quy cách: 28 x 36 x 12 cm | Dày 190 mic | Đóng thùng 40 túi/thùng (Tổng cộng 197 thùng)",
                "uom": "Túi",
                "qty": 7880,
                "remarks": "Đủ 197 thùng"
            }
        ]
    }

    # =========================================================================
    # CÁC BIỂU MẪU BỔ TRỢ KHÁC (BÁO GIÁ, HỢP ĐỒNG, ĐỐI SOÁT)
    # =========================================================================
    quotation_data = {
        "name": "BG-2608-AMYCO",
        "transaction_date": "2026-08-15",
        "customer_name": "CÔNG TY TNHH SX - XNK AMYCO",
        "tax_id": "0315487660",
        "contact_mobile": "0989.123.456",
        "shipping_address": "Lô B2-15, KCN Tây Bắc Củ Chi, Xã Tân An Hội, H. Củ Chi, TP. Hồ Chí Minh",
        "items": so_amyco_data["items"],
        "net_total": so_amyco_data["net_total"],
        "total_taxes_and_charges": so_amyco_data["total_taxes_and_charges"],
        "grand_total": so_amyco_data["grand_total"],
        "in_words": so_amyco_data["in_words"],
        "design_image": design_uri
    }

    contract_data = {
        "name": "2608-AMYCO/HĐMB-VP",
        "transaction_date": "2026-08-18",
        "customer_name": "CÔNG TY TNHH SX - XNK AMYCO",
        "tax_id": "0315487660",
        "contact_mobile": "0989.123.456",
        "shipping_address": "Lô B2-15, KCN Tây Bắc Củ Chi, Xã Tân An Hội, H. Củ Chi, TP. Hồ Chí Minh",
        "items": so_amyco_data["items"],
        "net_total": so_amyco_data["net_total"],
        "total_taxes_and_charges": so_amyco_data["total_taxes_and_charges"],
        "grand_total": so_amyco_data["grand_total"],
        "in_words": so_amyco_data["in_words"]
    }

    statement_data = {
        "name": "ĐSCN-2608-DS888",
        "posting_date": "2026-08-31",
        "from_date": "2026-08-01",
        "to_date": "2026-08-31",
        "customer_name": "CÔNG TY CỔ PHẦN DS COSMETIC",
        "tax_id": "0316789123",
        "contact_mobile": "0903.888.999",
        "shipping_address": "Số 45 Đường số 8, KDC Cityland Park Hills, P. 10, Q. Gò Vấp, TP. Hồ Chí Minh",
        "opening_balance": 0,
        "entries": [
            {
                "posting_date": "2026-08-20",
                "voucher_no": "PXK-2608-00446",
                "remarks": "Giao 22,000 túi 888 Hồng & 9,600 túi Minh Râu Hồng",
                "debit": 176328011,
                "credit": 0,
                "balance": 176328011
            },
            {
                "posting_date": "2026-08-21",
                "voucher_no": "PXK-2608-00452",
                "remarks": "Giao 10,400 túi 888 Hồng & 12,000 túi Minh Râu Tím",
                "debit": 124992008,
                "credit": 0,
                "balance": 301320019
            },
            {
                "posting_date": "2026-08-24",
                "voucher_no": "PXK-2608-00454",
                "remarks": "Giao 25,200 túi 888 Hồng & 7,880 túi Minh Râu Tím",
                "debit": 184586412,
                "credit": 0,
                "balance": 485906431
            },
            {
                "posting_date": "2026-08-27",
                "voucher_no": "PXK-2608-00459",
                "remarks": "Giao 13,600 túi 888 Hồng & 12,000 túi 888 Tím",
                "debit": 142840009,
                "credit": 0,
                "balance": 628746440
            },
            {
                "posting_date": "2026-08-31",
                "voucher_no": "PXK-2608-00465",
                "remarks": "Giao đợt cuối: 28,000 túi 888 Hồng & 8,730 túi 888 Tím",
                "debit": 204961413,
                "credit": 0,
                "balance": 833707853
            }
        ],
        "total_debit": 833707853,
        "total_credit": 0,
        "closing_balance": 833707853,
        "in_words": "Tám trăm ba mươi ba triệu bảy trăm lẻ bảy nghìn tám trăm năm mươi ba đồng."
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--no-sandbox", "--disable-setuid-sandbox"])
        page = browser.new_page()

        # ---------------------------------------------------------------------
        # 1. ĐƠN ĐẶT HÀNG (SALES ORDERS) - 2 KHÁCH HÀNG THỰC TẾ
        # ---------------------------------------------------------------------
        # 1.1. Khách hàng AMYCO (Túi SOFTY 3L có vòi + Trục in 8 màu)
        render_template_to_pdf(page, "don-dat-hang-template.html", so_amyco_data, "don-dat-hang-amyco-mau.pdf", header_html, logo_uri)
        # 1.2. Khách hàng DS COSMETIC (Túi 888 Hồng, Túi 888 Tím, Túi Minh Râu Tím)
        render_template_to_pdf(page, "don-dat-hang-template.html", so_ds888_data, "don-dat-hang-ds888-mau.pdf", header_html, logo_uri)

        # ---------------------------------------------------------------------
        # 2. 4 MẪU ĐƠN MUA HÀNG THỰC TẾ (PURCHASE ORDERS)
        # ---------------------------------------------------------------------
        # 2.1. Đặt Mua Túi Màng Ghép Trang Tín (Mẫu Túi Màng Ghép - 7 cột, kèm hình Trang 2)
        render_template_to_pdf(page, "don-mua-hang-tui-mang-ghep-template.html", po_tui_data, "don-mua-hang-tui-trangtin-mau.pdf", header_html, logo_uri)
        render_template_to_pdf(page, "don-mua-hang-tui-mang-ghep-template.html", po_tui_data, "don-mua-hang-tui-mang-ghep-mau.pdf", header_html, logo_uri)
        # 2.1b. Đặt In Lụa Gia Công Túi Thanh Tùng (Mẫu 3 - 7 cột, kèm hình Trang 2)
        render_template_to_pdf(page, "don-mua-hang-tui-template.html", po_tui_thanhtung_data, "don-mua-hang-tui-thanhtung-mau.pdf", header_html, logo_uri)
        # 2.1c. Đặt Mua Túi Màng Đơn Tạ Minh (Mẫu Túi Màng Đơn - 7 cột, 1 trang KHÔNG HÌNH, ĐVT: Kg)
        render_template_to_pdf(page, "don-mua-hang-tui-mang-don-template.html", po_taminh_data, "don-mua-hang-taminh-mau.pdf", header_html, logo_uri)
        # 2.2. Đặt In Gia Công Màng Ống Đồng Tuệ Nhi (8 cột chuẩn raw-docx, kèm hình Trang 2)
        render_template_to_pdf(page, "don-mua-hang-in-ong-dong-template.html", po_igc_data, "don-mua-hang-in-ong-dong-mau.pdf", header_html, logo_uri)
        render_template_to_pdf(page, "don-mua-hang-in-ong-dong-template.html", po_igc_data, "don-mua-hang-igc-tuenhi-mau.pdf", header_html, logo_uri)
        # 2.3. Đặt Mua Màng Nguyên Liệu Mộc Nam Sơn (10 cột chuẩn raw-excel, 1 trang duy nhất)
        render_template_to_pdf(page, "don-mua-hang-mang-nvl-template.html", po_mang_data, "don-mua-hang-mang-namson-mau.pdf", header_html, logo_uri)
        render_template_to_pdf(page, "don-mua-hang-mang-nvl-template.html", po_mang_data, "don-mua-hang-mang-mau.pdf", header_html, logo_uri)
        # 2.4. Đặt Hóa Chất, Keo Ghép & Hạt Nhựa Sungdo Vina (Mẫu Baseline 7 Cột, 1 Trang Không Hình)
        render_template_to_pdf(page, "don-mua-hang-baseline-template.html", po_hoachat_data, "don-mua-hang-hoachat-sungdo-mau.pdf", header_html, logo_uri)
        render_template_to_pdf(page, "don-mua-hang-baseline-template.html", po_hoachat_data, "don-mua-hang-baseline-hoachat-mau.pdf", header_html, logo_uri)
        # 2.4b. Đặt Vật Tư Phụ Liệu & Phụ Kiện Đóng Gói Unlimited (Mẫu Baseline 7 Cột, 1 Trang Không Hình)
        render_template_to_pdf(page, "don-mua-hang-baseline-template.html", po_vattu_data, "don-mua-hang-vattu-unlimited-mau.pdf", header_html, logo_uri)
        render_template_to_pdf(page, "don-mua-hang-baseline-template.html", po_vattu_data, "don-mua-hang-baseline-vattu-mau.pdf", header_html, logo_uri)
        # 2.5. Đặt Khắc Trục In Ống Đồng Dong Yun (7 cột, Trang 2 Maquette duyệt)
        render_template_to_pdf(page, "don-mua-hang-truc-in-template.html", po_truc_data, "don-mua-hang-truc-dongyun-mau.pdf", header_html, logo_uri)
        render_template_to_pdf(page, "don-mua-hang-truc-in-template.html", po_truc_data, "don-mua-hang-truc-in-mau.pdf", header_html, logo_uri)

        # ---------------------------------------------------------------------
        # 3. 1 MẪU PHIẾU XUẤT KHO THỰC TẾ (DELIVERY NOTE)
        # ---------------------------------------------------------------------
        # Khách hàng DS Cosmetic (25.200 túi 888 Hồng + 7.880 túi Minh Râu Tím - A5 Landscape)
        render_template_to_pdf(page, "phieu-xuat-kho-template.html", dn_ds888_data, "phieu-xuat-kho-ds888-mau.pdf", header_html, logo_uri, pdf_format="A5", landscape=True)

        # ---------------------------------------------------------------------
        # 4. CÁC FILE KHÁC (BÁO GIÁ, HỢP ĐỒNG, ĐỐI SOÁT CÔNG NỢ)
        # ---------------------------------------------------------------------
        render_template_to_pdf(page, "bao-gia-template.html", quotation_data, "bao-gia-van-phat-mau.pdf", header_html, logo_uri)
        render_template_to_pdf(page, "hop-dong-mua-ban-template.html", contract_data, "hop-dong-mua-ban-van-phat-mau.pdf", header_html, logo_uri)
        render_template_to_pdf(page, "bien-ban-doi-soat-cong-no-template.html", statement_data, "bien-ban-doi-soat-cong-no-van-phat-mau.pdf", header_html, logo_uri, pdf_format="A4", landscape=True)

        browser.close()

    print("\n>>> ĐÃ XUẤT THÀNH CÔNG TOÀN BỘ CÁC BIỂU MẪU TỪ DỮ LIỆU THỰC TẾ! <<<")

if __name__ == "__main__":
    main()
