#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Trích xuất Danh mục Khách Hàng (DocType Customer) trực tiếp 100% từ raw-data gốc:
- data/raw-data/cong no phai thu cua khach.xlsx (sổ nợ 131 của DS COSMETIC và BV VẠN AN)
- data/raw-data/TỔNG HỢP ĐƠN HÀNG ĐÃ CỌC CHƯA GIAO.xlsx (5 sheets: TÚI HD, túi ngcs, ĐÃ GIAO T3, ĐÃ GIAO T4, ĐÃ GIAO T5)
- data/clean-data/item_master.csv (các mặt hàng độc quyền đang gán khách hàng)

Tuân thủ nghiêm ngặt 100% ERPNext Native v16 Wording:
- name: KH-00001 .. KH-#####
- customer_name: Tên pháp nhân đầy đủ theo ĐKKD / Hóa đơn VAT
- alias: Tên gọi tắt thương mại UI Cockpit (cột native ERPNext)
- customer_type: Company | Individual
- customer_group: Khách Hàng Bao Bì Màng Ghép | Khách Hàng Bao Bì In Sẵn (NGCS) | Khách Hàng Túi Màng Đơn | Khách Hàng Thương Mại & Phân Phối
- territory: Phân vùng địa bàn giao hàng (TP. Hồ Chí Minh, Long An, Bình Dương, Hà Nội, v.v.)
- payment_terms: Công nợ gối đầu 30 ngày | Cọc trước 50% - Giao hàng 50%
  (Sếp chốt: phân loại Trả trước/Trả sau SUY RA từ payment_terms, KHÔNG dùng
  credit_limit — Customer native không có field phẳng này)
- default_currency: VND
- tax_id: Mã số thuế
- primary_address: Địa chỉ giao hàng thực tế
- customer_primary_contact: NVKD hoặc người liên hệ đại diện
- disabled: 0
"""

import os
import re
import csv
import unicodedata
from python_calamine import CalamineWorkbook

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw-data")
OUT_DIR = os.path.join(BASE_DIR, "data", "clean-data")

# Bảng chuẩn hóa tên sai lệch / viết tắt về Tên Pháp Nhân Chuẩn
CANONICAL_NAME_MAP = {
    "cty ds888": "CÔNG TY CỔ PHẦN DS COSMETIC",
    "công ty ds888": "CÔNG TY CỔ PHẦN DS COSMETIC",
    "công ty cổ phần bệnh viện vạn an 1": "CÔNG TY CỔ PHẦN BỆNH VIỆN VẠN AN",
    "cty tnhh sx - xnk amyco": "CÔNG TY TNHH SẢN XUẤT - XUẤT NHẬP KHẨU AMYCO",
    "cty cp hoá mỹ phẩm việt nhật": "CÔNG TY CP ĐẦU TƯ LIÊN DOANH SẢN XUẤT HOÁ MỸ PHẨM VIỆT NHẬT",
    "công ty cp đt liên doanh sx hóa mỹ phẩm cao cấp việt nhật": "CÔNG TY CP ĐẦU TƯ LIÊN DOANH SẢN XUẤT HOÁ MỸ PHẨM VIỆT NHẬT",
    "công ty cp đàu tư liên doanh sx hóa mỹ phẩm cao cấp việt nhật": "CÔNG TY CP ĐẦU TƯ LIÊN DOANH SẢN XUẤT HOÁ MỸ PHẨM VIỆT NHẬT",
    "công ty cp đầu tư liên doanh sản xuất hoá mỹ phẩm việt nhật": "CÔNG TY CP ĐẦU TƯ LIÊN DOANH SẢN XUẤT HOÁ MỸ PHẨM VIỆT NHẬT",
    "công ty tnhh sx tm bao bì kovaa": "CÔNG TY TNHH SX THƯƠNG MẠI BAO BÌ KOVAA",
    "cty tnhh zyland": "CÔNG TY TNHH ZYLAND",
    "công ty nguyễn gia": "CÔNG TY TNHH ĐẦU TƯ SẢN XUẤT DỊCH VỤ VÀ THƯƠNG MẠI NGUYỄN GIA",
    "khách hàng ms. barun": "CÔNG TY TNHH NHÀ HÀNG HÀN QUỐC MS BARUN",
    "hộ kinh doanh ms barun": "CÔNG TY TNHH NHÀ HÀNG HÀN QUỐC MS BARUN",
    "khách hàng anh khoa": "PHÒNG KHÁM CHUYÊN KHOA NHI – MẶT TRỜI BÉ CON",
    "anh khoa (mtbc vĩnh long, an hữu, bình phước, củ chi, thủ đức)": "PHÒNG KHÁM CHUYÊN KHOA NHI – MẶT TRỜI BÉ CON",
    "anh khoa": "PHÒNG KHÁM CHUYÊN KHOA NHI – MẶT TRỜI BÉ CON",
    "anh khoa mtbc": "PHÒNG KHÁM CHUYÊN KHOA NHI – MẶT TRỜI BÉ CON",
    "hải sản ốc kiều": "Hải sản tươi sống Ốc Kiều",
    "doanh nghiệp thế kỷ vàng": "HỘ KINH DOANH THẾ KỶ VÀNG",
    "khách hàng sofia": "CÔNG TY CỔ PHẦN EZ COSMETIC VIỆT NAM – CHI NHÁNH LONG AN",
    "khách hàng futa true": "CÔNG TY TNHH MTV TM TRANG UYÊN",
    "công ty tnhhsảnxuất và thươngmạituấn phát": "CÔNG TY TNHH SẢN XUẤT VÀ THƯƠNG MẠI TUẤN PHÁT",
    "công ty tnhhsảnxuất và thươngmại tuấn phát": "CÔNG TY TNHH SẢN XUẤT VÀ THƯƠNG MẠI TUẤN PHÁT",
    "công ty tnhh kinh doanh đầu tư và dịch vụ phan gia bích": "CÔNG TY TNHH KINH DOANH ĐẦU TƯ VÀ DỊCH VỤ PHAN GIA BÍCH"
}

# Bảng định nghĩa Alias ưu tiên chuẩn thương mại
KNOWN_ALIASES = {
    "CÔNG TY CỔ PHẦN DS COSMETIC": "DS COSMETIC",
    "CÔNG TY CỔ PHẦN BỆNH VIỆN VẠN AN": "VẠN AN",
    "CÔNG TY TNHH MTV SX TM XNK ANH PHÁT": "ANH PHÁT",
    "CÔNG TY TNHH CÔNG NGHỆ VẬT LIỆU TIÊN PHONG VIETCOAT": "VIETCOAT",
    "CÔNG TY TNHH THƯƠNG MẠI JNS VIỆT NAM": "JNS VIỆT NAM",
    "CÔNG TY CỔ PHẦN ECO WIPES VIỆT NAM": "ECO WIPES",
    "CÔNG TY TNHH SX THƯƠNG MẠI BAO BÌ KOVAA": "KOVAA",
    "CÔNG TY TNHH SẢN XUẤT - XUẤT NHẬP KHẨU AMYCO": "AMYCO",
    "CÔNG TY CỔ PHẦN EZ COSMETIC VIỆT NAM – CHI NHÁNH LONG AN": "EZ COSMETIC",
    "CÔNG TY TNHH MTV TM TRANG UYÊN": "TRANG UYÊN",
    "CÔNG TY CỔ PHẦN DINH DƯỠNG SKX": "DINH DƯỠNG SKX",
    "CÔNG TY TNHH ENZY FOOD": "ENZY FOOD",
    "CÔNG TY TNHH SẢN XUẤT THƯƠNG MẠI DỊCH VỤ TỔNG HỢP THÁI DƯƠNG": "THÁI DƯƠNG",
    "CÔNG TY TNHH HÓA MỸ PHẨM VIO": "VIO",
    "CÔNG TY TNHH HÓA PHẨM NAM GIA PHÁT": "NAM GIA PHÁT",
    "CÔNG TY TNHH HÓA MỸ PHẨM LINH PHƯƠNG": "LINH PHƯƠNG",
    "CÔNG TY TNHH KINH DOANH ĐẦU TƯ VÀ DỊCH VỤ PHAN GIA BÍCH": "PHAN GIA BÍCH",
    "CÔNG TY TNHH TM-DV THANH TẠO PHÁT": "THANH TẠO PHÁT",
    "CÔNG TY TNHH SẢN XUẤT VÀ THƯƠNG MẠI TUẤN PHÁT": "TUẤN PHÁT",
    "CÔNG TY TNHH SX& ĐẦU TƯ PHÚ THÀNH": "PHÚ THÀNH",
    "CÔNG TY TNHH PHÁT TRIỂN THƯƠNG MẠI NHAN GIA PHÁT": "NHAN GIA PHÁT",
    "CÔNG TY TNHH TM-DV HÓA MỸ PHẨM LÂM GIA": "LÂM GIA",
    "Công ty TNHH sản xuất và thương mại Anh Lâm": "ANH LÂM",
    "CÔNG TY TNHH THƯƠNG MẠI -XNK T&Đ VIỆT NAM": "T&Đ VIỆT NAM",
    "CÔNG TY TNHH ĐẦU TƯ VÀ THƯƠNG MẠI AN SINH LỘC": "AN SINH LỘC",
    "CÔNG TY CP ĐẦU TƯ LIÊN DOANH SẢN XUẤT HOÁ MỸ PHẨM VIỆT NHẬT": "VIỆT NHẬT",
    "CÔNG TY TNHH DƯƠNG PHÁT HT": "DƯƠNG PHÁT",
    "HỘ KINH DOANH HÀO GIA": "HÀO GIA",
    "Hộ Kinh Doanh NT VAN": "NT VAN",
    "Hải sản tươi sống Ốc Kiều": "ỐC KIỀU",
    "CÔNG TY TNHH NHÀ HÀNG HÀN QUỐC MS BARUN": "MS BARUN",
    "CÔNG TY TNHH NHỰA HÀ LINH": "HÀ LINH",
    "HỘ KINH DOANH ĐẶNG DIỀU TÂM": "ĐẶNG DIỀU TÂM",
    "CÔNG TY TNHH SẢN XUẤT NỆM PHONG NGUYÊN": "PHONG NGUYÊN",
    "Phòng khám chuyên khoa Nhi Huỳnh Minh Thư": "HUỲNH MINH THƯ",
    "PHÒNG KHÁM CHUYÊN KHOA NHI – MẶT TRỜI BÉ CON": "MTBC",
    "CÔNG TY TNHH SẢN XUẤT VÀ KINH DOANH NHẬT QUANG VINA": "NHẬT QUANG VINA",
    "CÔNG TY CP QUỐC TẾ VMT GROUP": "VMT GROUP",
    "CÔNG TY CP PHÚC HƯNG PHÚC": "PHÚC HƯNG PHÚC",
    "CÔNG TY TNHH PHÁT TRIỂN THƯƠNG MẠI CHÂU LONG": "CHÂU LONG",
    "CÔNG TY TNHH SẢN XUẤT VÀ THƯƠNG MẠI RIOS VIỆT NAM": "RIOS",
    "HỘ KINH DOANH THẾ KỶ VÀNG": "THẾ KỶ VÀNG",
    "Công ty TNHH chăm sóc sức khỏe Huy Hoàng": "HUY HOÀNG",
    "CÔNG TY TNHH SẢN XUẤT MỸ PHẨM AN NHIÊN": "AN NHIÊN",
    "CÔNG TY TNHH PHONG TÍN": "PHONG TÍN",
    "CÔNG TY CỔ PHẦN CARITAS FRUITS": "CARITAS FRUITS",
    "CÔNG TY TNHH PET UNIVERSE": "PET UNIVERSE",
    "JieJie’s Kitchen Campuchia": "JIEJIE CAMBODIA",
    "CÔNG TY TNHH SAHAKA VIỆT NAM": "SAHAKA",
    "CÔNG TY TNHH SẢN XUẤT THƯƠNG MẠI DỊCH VỤ AHA FRESH": "AHA FRESH",
    "CÔNG TY TNHH TM VÀ DV TRƯỜNG AN": "TRƯỜNG AN",
    "NGUYỄN CHÍ LINH": "NGUYỄN CHÍ LINH",
    "CÔNG TY TNHH TM XNK KIẾN NAM": "KIẾN NAM",
    "CÔNG TY TNHH DẦU KHÍ PHẠM GIA GROUP": "PHẠM GIA GROUP",
    "CÔNG TY TNHH SAM RAN": "SAM RAN",
    "CÔNG TY TNHH MỸ PHẨM AVATAR VIỆT NAM": "AVATAR",
    "ANH TÂN": "ANH TÂN",
    "CÔNG TY TNHH ZYLAND": "ZYLAND",
    "CÔNG TY TNHH THƯƠNG MẠI THỰC PHẨM JMC": "JMC FOOD",
    "CÔNG TY TNHH ĐẦU TƯ SẢN XUẤT DỊCH VỤ VÀ THƯƠNG MẠI NGUYỄN GIA": "NGUYỄN GIA"
}


def clean_text(s):
    if not s or str(s).strip().lower() in ["none", "nan", "null"]:
        return ""
    return unicodedata.normalize("NFC", str(s).strip())


def normalize_company_name(name):
    raw = clean_text(name)
    if not raw or raw in ["Tên khách hàng", "TỔNG CỘNG"] or raw.startswith("2026-") or raw.startswith("Tổng"):
        return ""
    norm = re.sub(r"\s+", " ", raw)
    low = norm.lower()
    return CANONICAL_NAME_MAP.get(low, norm)


def derive_alias(legal_name):
    if legal_name in KNOWN_ALIASES:
        return KNOWN_ALIASES[legal_name][:25]

    # Tự động rút gọn bằng cách loại bỏ các tiền tố pháp nhân
    name = legal_name
    prefixes = [
        r"^công ty trách nhiệm hữu hạn một thành viên\s+",
        r"^công ty trách nhiệm hữu hạn\s+",
        r"^công ty tnhh một thành viên\s+",
        r"^công ty tnhh mtv tm\s+",
        r"^công ty tnhh mtv sx tm xnk\s+",
        r"^công ty tnhh mtv\s+",
        r"^công ty tnhhsảnxuất và thươngmại\s+",
        r"^công ty tnhh\s+",
        r"^công ty cổ phần\s+",
        r"^công ty cp\s+",
        r"^hộ kinh doanh\s+",
        r"^doanh nghiệp tư nhân\s+",
        r"^doanh nghiệp\s+",
        r"^phòng khám chuyên khoa nhi\s*[-–]\s*",
        r"^phòng khám chuyên khoa\s+",
        r"^cơ sở\s+",
        r"^khách hàng\s+"
    ]
    for p in prefixes:
        name = re.sub(p, "", name, flags=re.IGNORECASE)

    name = re.sub(r"^(sản xuất|thương mại|dịch vụ|đầu tư|xuất nhập khẩu|sx|tm|dv|xnk)\s+", "", name, flags=re.IGNORECASE)
    name = re.sub(r"^(và\s+)?(thương mại|dịch vụ|sản xuất)\s+", "", name, flags=re.IGNORECASE)

    name = name.strip()
    words = name.split()
    if len(words) > 4:
        alias = " ".join(words[:3])
    else:
        alias = name
    return alias.upper()[:25]


def detect_customer_type(legal_name):
    low = legal_name.lower()
    # Nếu là công ty hoặc doanh nghiệp
    if any(k in low for k in ["công ty", "cp ", "tnhh", "doanh nghiệp", "kitchen", "group"]):
        return "Company"
    return "Individual"


def is_valid_delivery_address(addr):
    if not addr: return False
    a = addr.lower()
    # Loại bỏ tên mặt hàng bị gõ nhầm vào cột địa chỉ
    if any(a.startswith(bad) for bad in ["túi", "cuộn", "màng", "thùng", "khay", "nắp", "in ", "hàng", "phi "]):
        return False
    if len(addr) < 8:
        return False
    return True


def select_best_address(addresses):
    valid = [a for a in addresses if is_valid_delivery_address(a)]
    if not valid:
        return ""
    # Ưu tiên địa chỉ có từ khóa địa lý rõ ràng
    def addr_score(a):
        score = len(a)
        low = a.lower()
        if any(k in low for k in ["đường", "số", "phường", "quận", "huyện", "tỉnh", "thành phố", "tphcm", "lô", "kcn", "thôn", "ấp", "xã"]):
            score += 100
        return score
    valid.sort(key=addr_score, reverse=True)
    return valid[0]


def detect_territory(addr):
    if not addr:
        return "Việt Nam"
    a = unicodedata.normalize("NFC", addr).lower()
    if any(k in a for k in ["hồ chí minh", "tp.hcm", "tphcm", "sài gòn", "quận", "hóc môn", "bình chánh", "bình tân", "thủ đức", "tân bình", "tân sơn", "phước long", "đa kao", "an lạc"]):
        return "TP. Hồ Chí Minh"
    if "tây ninh" in a: return "Tây Ninh"
    if any(k in a for k in ["bình dương", "thuận an", "dĩ an", "thủ dầu một"]): return "Bình Dương"
    if any(k in a for k in ["đồng nai", "trảng bom", "long khánh", "xuân hòa"]): return "Đồng Nai"
    if any(k in a for k in ["long an", "bến lức", "cần giuộc", "long cang"]): return "Long An"
    if any(k in a for k in ["hà nội", "chương mỹ", "nguyễn trãi", "hòa xá"]): return "Hà Nội"
    if any(k in a for k in ["hưng yên", "yên mỹ", "như quỳnh", "lạc đạo", "ân thi"]): return "Hưng Yên"
    if any(k in a for k in ["hải phòng", "trường tân", "an hải"]): return "Hải Phòng"
    if "hà tĩnh" in a: return "Hà Tĩnh"
    if "sóc trăng" in a: return "Sóc Trăng"
    if "an giang" in a: return "An Giang"
    if any(k in a for k in ["đắk lắk", "buôn hồ"]): return "Đắk Lắk"
    if "gia lai" in a: return "Gia Lai"
    if "phú thọ" in a: return "Phú Thọ"
    if "ninh bình" in a: return "Ninh Bình"
    if any(k in a for k in ["huế", "thừa thiên"]): return "Thừa Thiên Huế"
    if any(k in a for k in ["bắc ninh", "văn môn"]): return "Bắc Ninh"
    if "tuyên quang" in a: return "Tuyên Quang"
    if any(k in a for k in ["camphuchia", "campuchia"]): return "Campuchia"
    return "Việt Nam"


def detect_customer_group(items_set, legal_name):
    text = " ".join(items_set).lower() + " " + legal_name.lower()
    if any(k in text for k in ["ngcs", "kyros", "vio", "kirei", "firola", "superclean", "rich city", "cleans", "saiky", "hygiene", "fressha", "myo", "youri", "mama care", "d shinephat", "mighty"]):
        return "Khách Hàng Bao Bì In Sẵn (NGCS)"
    if any(k in text for k in ["hd ", "pe ", "pp ", "quai thỏ", "hột xoài", "phong nguyên", "đàn", "bọc nệm", "ốc kiều"]):
        return "Khách Hàng Túi Màng Đơn"
    if any(k in text for k in ["túi đựng", "baba", "chloe'ly", "supergeo", "skx", "enzy", "màng ghép", "trục", "không trục"]):
        return "Khách Hàng Bao Bì Màng Ghép"
    return "Khách Hàng Thương Mại & Phân Phối"


def extract_all():
    print("=" * 75)
    print(" BẮT ĐẦU TRÍCH XUẤT DANH MỤC KHÁCH HÀNG TỪ RAW-DATA CHUẨN ERPNEXT v16")
    print("=" * 75)

    customers = {}

    def register(raw_name, source, addr="", sp="", item="", amt=0):
        cname = normalize_company_name(raw_name)
        if not cname:
            return
        if cname not in customers:
            customers[cname] = {
                "customer_name": cname,
                "sources": set(),
                "addresses": set(),
                "salespersons": set(),
                "items": set(),
                "total_orders": 0,
                "total_amount": 0.0
            }
        cust = customers[cname]
        cust["sources"].add(source)
        a = clean_text(addr)
        if a and a.lower() not in ["địa chỉ", "diachi"]:
            cust["addresses"].add(a)
        s = clean_text(sp)
        if s and s.lower() not in ["mã nhân viên bán hàng", "mã nvkd"]:
            cust["salespersons"].add(s.title())
        it = clean_text(item)
        if it and it.lower() not in ["tên hàng", "tenhang"]:
            cust["items"].add(it)
        cust["total_orders"] += 1
        try:
            cust["total_amount"] += float(amt or 0)
        except:
            pass

    # 1. Trích xuất từ cong no phai thu cua khach.xlsx
    f_debt = os.path.join(RAW_DIR, "cong no phai thu cua khach.xlsx")
    if os.path.exists(f_debt):
        wb_debt = CalamineWorkbook.from_path(f_debt)
        # DS888
        for r in wb_debt.get_sheet_by_name("DS888").to_python()[3:]:
            if len(r) > 6 and r[6]:
                register("CÔNG TY CỔ PHẦN DS COSMETIC", "Sổ nợ 131 DS888", "", "Huy", r[2], r[6])
        # VẠN AN
        for r in wb_debt.get_sheet_by_name("VẠN AN").to_python()[3:]:
            if len(r) > 6 and r[6]:
                register("CÔNG TY CỔ PHẦN BỆNH VIỆN VẠN AN", "Sổ nợ 131 VẠN AN", "Số 352 Tuyến Tránh Quốc Lộ 1, Ấp 4, Phường Long An, Tỉnh Tây Ninh", "Huy", r[1], r[6])
        print(" [+] Đã nạp sổ công nợ 131: CÔNG TY CỔ PHẦN DS COSMETIC & CÔNG TY CỔ PHẦN BỆNH VIỆN VẠN AN")

    # 2. Trích xuất từ TỔNG HỢP ĐƠN HÀNG ĐÃ CỌC CHƯA GIAO.xlsx
    f_orders = os.path.join(RAW_DIR, "TỔNG HỢP ĐƠN HÀNG ĐÃ CỌC CHƯA GIAO.xlsx")
    if os.path.exists(f_orders):
        wb_orders = CalamineWorkbook.from_path(f_orders)
        for sname in ["TÚI HD (2)", "túi ngcs"]:
            for r in wb_orders.get_sheet_by_name(sname).to_python()[1:]:
                if len(r) > 9:
                    register(r[2], f"Đơn cọc [{sname}]", r[3], r[4], r[5], r[9])
        for sname in ["ĐÃ GIAO T3", "ĐÃ GIAO T4", "ĐÃ GIAO T5"]:
            for r in wb_orders.get_sheet_by_name(sname).to_python()[1:]:
                if len(r) > 8:
                    register(r[1], f"Đã giao [{sname}]", r[2], r[3], r[4], r[8])
        print(" [+] Đã nạp toàn bộ 5 sheet trong TỔNG HỢP ĐƠN HÀNG ĐÃ CỌC CHƯA GIAO.xlsx")

    # 3. Quét kiểm tra từ item_master.csv để đảm bảo không sót khách hàng nào có sản phẩm độc quyền
    f_items = os.path.join(OUT_DIR, "item_master.csv")
    if os.path.exists(f_items):
        with open(f_items, mode="r", encoding="utf-8-sig") as f:
            for r in csv.DictReader(f):
                c = clean_text(r.get("customer", ""))
                if c:
                    register(c, "Mặt hàng độc quyền", "", "", r.get("item_name", ""))
        print(" [+] Đã đối chiếu toàn bộ khách hàng gắn với Item Master")

    def sort_key(item):
        name, data = item
        is_debt_cust = name in ["CÔNG TY CỔ PHẦN DS COSMETIC", "CÔNG TY CỔ PHẦN BỆNH VIỆN VẠN AN"]
        has_deposit = any("Đơn cọc" in src for src in data["sources"])
        return (not is_debt_cust, not has_deposit, -data["total_amount"], name)

    sorted_customers = sorted(customers.items(), key=sort_key)
    print(f"\n=> TỔNG CỘNG TRÍCH XUẤT ĐƯỢC: {len(sorted_customers)} KHÁCH HÀNG CHÍNH THỨC.")

    # Xuất ra customer_master.csv chuẩn ERPNext Native v16
    # Sếp chốt 2026-09-15: BỎ credit_limit (không phải field Customer native —
    # native là child table Customer Credit Limit theo Company). Phân loại
    # Trả trước/Trả sau SUY RA từ payment_terms (Cọc 50% vs Gối đầu 30 ngày);
    # import_master_data.py gán template + child limit khi có Company.
    out_rows = []
    HEADERS = [
        "name", "customer_name", "alias", "customer_type", "customer_group",
        "territory", "payment_terms", "default_currency",
        "tax_id", "primary_address", "customer_primary_contact", "disabled"
    ]

    for idx, (legal_name, data) in enumerate(sorted_customers, 1):
        cust_id = f"KH-{idx:05d}"
        alias = derive_alias(legal_name)
        cust_type = detect_customer_type(legal_name)

        primary_addr = select_best_address(data["addresses"])
        territory = detect_territory(primary_addr)

        sp_list = list(data["salespersons"])
        sp = sp_list[0] if sp_list else ""

        group = detect_customer_group(data["items"], legal_name)

        if legal_name == "CÔNG TY CỔ PHẦN DS COSMETIC":
            payment_terms = "Công nợ gối đầu 30 ngày"
        elif legal_name == "CÔNG TY CỔ PHẦN BỆNH VIỆN VẠN AN":
            payment_terms = "Công nợ gối đầu 30 ngày"
        else:
            payment_terms = "Cọc trước 50% - Giao hàng 50%"

        out_rows.append({
            "name": cust_id,
            "customer_name": legal_name,
            "alias": alias,
            "customer_type": cust_type,
            "customer_group": group,
            "territory": territory,
            "payment_terms": payment_terms,
            "default_currency": "VND",
            "tax_id": "",
            "primary_address": primary_addr,
            "customer_primary_contact": sp,
            "disabled": 0
        })

    out_file = os.path.join(OUT_DIR, "customer_master.csv")
    with open(out_file, mode="w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=HEADERS, lineterminator="\n")
        w.writeheader()
        w.writerows(out_rows)

    print(f"\n ĐÃ XUẤT THÀNH CÔNG {len(out_rows)} KHÁCH HÀNG VÀO: {out_file}")
    print("=" * 75)
    return out_rows


if __name__ == "__main__":
    extract_all()
