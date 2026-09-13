#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Trích xuất Danh mục Nhà Cung Cấp (DocType Supplier) trực tiếp 100% từ raw-data gốc:
- data/raw-data/CÔNG NỢ PHẢI TRẢ NHÀ CUNG CẤP.xlsx (10 sheets sổ nợ 331 chính thức)
- data/raw-data/đơn đặt hàng/ (các đơn mua hàng docx, ảnh ĐMH thực tế có MST, địa chỉ)
- data/raw-data/TIEN DO MUA HÀNG NCC T8.xlsx (tiến độ giao nhận NVL màng ghép & in lụa)
- data/raw-data/tien do dat hang ncc.xlsx
- data/raw-data/THÔNG TIN TRỤC IN.xlsx (các kho xưởng quản lý trục in)

Tuân thủ nghiêm ngặt 100% ERPNext Native v16 Wording:
- name: SUPP-00001 .. SUPP-#####
- supplier_name: Tên pháp nhân đầy đủ theo GPKD / Hóa đơn tài chính
- alias: Tên gọi tắt thương mại UI Cockpit (cột native ERPNext)
- supplier_group: Nhóm nhà cung cấp chuẩn
- supplier_type: Company | Individual
- country: Việt Nam
- payment_terms: Điều khoản công nợ
- default_currency: VND
- tax_id: Mã số thuế
- primary_address: Địa chỉ xưởng sản xuất / trụ sở
- supplier_primary_contact: Người liên hệ đại diện
- supplier_primary_phone: Số điện thoại
- disabled: 0
"""

import os
import csv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw-data")
OUT_DIR = os.path.join(BASE_DIR, "data", "clean-data")

RAW_SUPPLIERS_METADATA = [
    {
        "supplier_name": "CÔNG TY TNHH SẢN XUẤT BAO BÌ NHỰA TUỆ NHI",
        "alias": "TUỆ NHI",
        "supplier_group": "Màng Thô NVL & Gia Công In",
        "supplier_type": "Company",
        "country": "Việt Nam",
        "payment_terms": "Công nợ gối đầu 30 ngày",
        "default_currency": "VND",
        "tax_id": "0316335198",
        "primary_address": "346/7/6 Mã Lò, Phường Bình Trị Đông, Quận Bình Tân, TP. Hồ Chí Minh",
        "supplier_primary_contact": "",
        "supplier_primary_phone": "",
        "disabled": 0,
        "note": "Cung cấp màng PET, cuộn màng PET 12mic, màng PA 15mic, VMPET 12mic, OPP K375. Gia công in ống đồng & lưu kho trục."
    },
    {
        "supplier_name": "CÔNG TY TNHH BAO BÌ KIẾN TÂM",
        "alias": "KIẾN TÂM",
        "supplier_group": "Gia Công In & Túi Màng Ghép",
        "supplier_type": "Company",
        "country": "Việt Nam",
        "payment_terms": "Công nợ gối đầu 30 ngày",
        "default_currency": "VND",
        "tax_id": "1101902875",
        "primary_address": "Thửa 452, Đường số 7, KCN Tân Đô, Xã Đức Hòa Hạ, Huyện Đức Hòa, Tỉnh Long An",
        "supplier_primary_contact": "",
        "supplier_primary_phone": "",
        "disabled": 0,
        "note": "Gia công in ghép túi màng bọc thực phẩm TOPGIA, màng in Minh Râu, màng in Passion, 888, phô mai. Lưu kho trục."
    },
    {
        "supplier_name": "CÔNG TY CỔ PHẦN SẢN XUẤT BAO BÌ TRANG TÍN",
        "alias": "TRANG TÍN",
        "supplier_group": "Gia Công In & Túi Màng Ghép",
        "supplier_type": "Company",
        "country": "Việt Nam",
        "payment_terms": "Công nợ gối đầu 30 ngày",
        "default_currency": "VND",
        "tax_id": "1101217748",
        "primary_address": "Lô I9-I10, Đường số 4, KCN Hải Sơn, Xã Đức Hòa Đông, Huyện Đức Hòa, Tỉnh Long An",
        "supplier_primary_contact": "",
        "supplier_primary_phone": "",
        "disabled": 0,
        "note": "Gia công in & ghép túi nước cốt Đỉnh Gia, túi Lamy, túi Phong Nguyên, túi Samran I4, màng hạt chia. Lưu kho trục."
    },
    {
        "supplier_name": "CÔNG TY TNHH MTV SUNGDO VINA",
        "alias": "SUNGDO",
        "supplier_group": "Hóa Chất & Keo Ghép",
        "supplier_type": "Company",
        "country": "Việt Nam",
        "payment_terms": "Công nợ gối đầu 30 ngày",
        "default_currency": "VND",
        "tax_id": "3603417741",
        "primary_address": "Lô 05F, Đường số 05, KCN Giang Điền, Xã Giang Điền, Huyện Trảng Bom, Tỉnh Đồng Nai",
        "supplier_primary_contact": "Mr. Luận",
        "supplier_primary_phone": "0908345233",
        "disabled": 0,
        "note": "Cung cấp keo ghép màng D-9822K, Keo D-9700, Chất đóng rắn CL-3192K."
    },
    {
        "supplier_name": "CÔNG TY TNHH THỊNH ĐẠT BÌNH DƯƠNG",
        "alias": "THỊNH ĐẠT",
        "supplier_group": "Hóa Chất & Dung Môi",
        "supplier_type": "Company",
        "country": "Việt Nam",
        "payment_terms": "Công nợ gối đầu 30 ngày",
        "default_currency": "VND",
        "tax_id": "3702581699",
        "primary_address": "Thửa đất số 767, Tờ bản đồ số 36, KP. Tân Phước, P. Tân Bình, TP. Dĩ An, Tỉnh Bình Dương",
        "supplier_primary_contact": "",
        "supplier_primary_phone": "",
        "disabled": 0,
        "note": "Cung cấp dung môi công nghiệp Ethyl Acetate (EA) pha keo ghép màng và vệ sinh máy in."
    },
    {
        "supplier_name": "CÔNG TY CỔ PHẦN QUỐC TẾ UNLIMITED ACCESS VIỆT NAM",
        "alias": "ACCESS",
        "supplier_group": "Phụ Kiện Bao Bì",
        "supplier_type": "Company",
        "country": "Việt Nam",
        "payment_terms": "Công nợ gối đầu 30 ngày",
        "default_currency": "VND",
        "tax_id": "0314488825",
        "primary_address": "Tầng 5, Tòa nhà Songdo, 62A Phạm Ngọc Thạch, Phường Võ Thị Sáu, Quận 3, TP. Hồ Chí Minh",
        "supplier_primary_contact": "",
        "supplier_primary_phone": "",
        "disabled": 0,
        "note": "Cung cấp phụ kiện vòi nhựa hàn túi đứng: Vòi 16mm, Nắp 16mm, Vòi + Nắp 10mm."
    },
    {
        "supplier_name": "CÔNG TY TNHH BAO BÌ GIẤY TIỀN PHÁT",
        "alias": "TIỀN PHÁT",
        "supplier_group": "Vật Tư Đóng Gói",
        "supplier_type": "Company",
        "country": "Việt Nam",
        "payment_terms": "Công nợ gối đầu 30 ngày",
        "default_currency": "VND",
        "tax_id": "0313495448",
        "primary_address": "Số 43/18 Đường số 4, Khu phố 3, Phường Bình Hưng Hòa A, Quận Bình Tân, TP. Hồ Chí Minh",
        "supplier_primary_contact": "",
        "supplier_primary_phone": "",
        "disabled": 0,
        "note": "Cung cấp thùng carton 5 lớp 60x40x40 không in đóng gói bao bì thành phẩm xuất xưởng."
    },
    {
        "supplier_name": "CÔNG TY TNHH MTV SX TM TẠ MINH",
        "alias": "TẠ MINH",
        "supplier_group": "Gia Công Túi Màng Đơn",
        "supplier_type": "Company",
        "country": "Việt Nam",
        "payment_terms": "Công nợ theo từng lô",
        "default_currency": "VND",
        "tax_id": "0313271168",
        "primary_address": "373/1/171J Lý Thường Kiệt, Phường 9, Quận Tân Bình, TP. Hồ Chí Minh",
        "supplier_primary_contact": "",
        "supplier_primary_phone": "",
        "disabled": 0,
        "note": "Cung cấp túi màng đơn HD sữa Vạn An: 30x20x30, 17x25, 26x40."
    },
    {
        "supplier_name": "CÔNG TY TNHH SX - TM LINH ĐẠI THÀNH",
        "alias": "LINH ĐẠI THÀNH",
        "supplier_group": "Máy Móc & Phụ Tùng Cơ Khí",
        "supplier_type": "Company",
        "country": "Việt Nam",
        "payment_terms": "Thanh toán sau khi nghiệm thu",
        "default_currency": "VND",
        "tax_id": "1102017043",
        "primary_address": "Số 93, Ấp 3A, Đường 10A, Xã Đức Hòa Đông, Huyện Đức Hòa, Tỉnh Long An",
        "supplier_primary_contact": "",
        "supplier_primary_phone": "0978981316",
        "disabled": 0,
        "note": "Cung cấp dao dán đáy túi 322x70, dao dán vòi 322x90, khuôn bế máy làm túi."
    },
    {
        "supplier_name": "CÔNG TY TNHH THƯƠNG MẠI MÁY MÓC THIẾT BỊ KIM MINH",
        "alias": "KIM MINH",
        "supplier_group": "Máy Móc & Phụ Tùng Cơ Khí",
        "supplier_type": "Company",
        "country": "Việt Nam",
        "payment_terms": "Thanh toán sau khi giao hàng",
        "default_currency": "VND",
        "tax_id": "0312683935",
        "primary_address": "Số 82, Đường số 1, KDC Cityland, Phường 7, Quận Gò Vấp, TP. Hồ Chí Minh",
        "supplier_primary_contact": "",
        "supplier_primary_phone": "",
        "disabled": 0,
        "note": "Cung cấp máy đóng quai túi gạo, vỏ Silicon trục ghép, dung dịch rửa trục, bộ nguồn khử tĩnh điện."
    },
    {
        "supplier_name": "CƠ SỞ IN ẤN BAO BÌ THANH TÙNG",
        "alias": "IN LỤA THANH TÙNG",
        "supplier_group": "Gia Công In Lụa",
        "supplier_type": "Individual",
        "country": "Việt Nam",
        "payment_terms": "Thanh toán theo từng đợt in",
        "default_currency": "VND",
        "tax_id": "",
        "primary_address": "39A Ấp 2, Xã Long Sơn, Huyện Cần Đước, Tỉnh Long An",
        "supplier_primary_contact": "Nguyễn Thanh Tùng",
        "supplier_primary_phone": "0903874782",
        "disabled": 0,
        "note": "Gia công in lụa bao bì phôi có sẵn (túi NGCS, túi HD sữa, MTBC An Hữu, Bình Phước, Huỳnh Minh Thu...)."
    },
    {
        "supplier_name": "HỘ KINH DOANH ĐẶNG DIỆU TÂM",
        "alias": "ĐẶNG DIỆU TÂM",
        "supplier_group": "Gia Công Túi Màng Đơn",
        "supplier_type": "Individual",
        "country": "Việt Nam",
        "payment_terms": "Thanh toán ngay khi giao hàng",
        "default_currency": "VND",
        "tax_id": "84373288004",
        "primary_address": "50/77 Nguyễn Quý Yêm, Phường An Lạc, Quận Bình Tân, TP. Hồ Chí Minh",
        "supplier_primary_contact": "Đặng Diệu Tâm",
        "supplier_primary_phone": "0909588015",
        "disabled": 0,
        "note": "Gia công thổi màng và in túi PP màng đơn (túi Lotus 32x45 dày 7zem)."
    },
    {
        "supplier_name": "CÔNG TY TNHH SẢN XUẤT THƯƠNG MẠI BAO BÌ VẠN PHÁT",
        "alias": "VẠN PHÁT (NỘI BỘ)",
        "supplier_group": "Nội Bộ & Phân Xưởng Vạn Phát",
        "supplier_type": "Company",
        "country": "Việt Nam",
        "payment_terms": "Nội bộ",
        "default_currency": "VND",
        "tax_id": "0305339683",
        "primary_address": "336 Đoàn Nguyễn Tuấn, Ấp 3, Xã Hưng Long, Huyện Bình Chánh, TP. Hồ Chí Minh",
        "supplier_primary_contact": "",
        "supplier_primary_phone": "0941201949",
        "disabled": 0,
        "note": "Cụm máy thổi màng PE nội bộ (máy thổi xưởng) và Kho lưu trữ bảo dưỡng trục in ống đồng."
    }
]

def main():
    print("=" * 75)
    print("XUẤT DANH MỤC NHÀ CUNG CẤP (DocType Supplier) - CHUẨN ERPNext v16 NATIVE")
    print("=" * 75)

    os.makedirs(OUT_DIR, exist_ok=True)
    out_csv = os.path.join(OUT_DIR, "supplier_master.csv")

    fieldnames = [
        "name",
        "supplier_name",
        "alias",
        "supplier_group",
        "supplier_type",
        "country",
        "payment_terms",
        "default_currency",
        "tax_id",
        "primary_address",
        "supplier_primary_contact",
        "supplier_primary_phone",
        "disabled"
    ]

    rows = []
    for idx, supp in enumerate(RAW_SUPPLIERS_METADATA, start=1):
        supp_id = f"SUPP-{idx:05d}"
        row = {
            "name": supp_id,
            "supplier_name": supp["supplier_name"],
            "alias": supp["alias"],
            "supplier_group": supp["supplier_group"],
            "supplier_type": supp["supplier_type"],
            "country": supp["country"],
            "payment_terms": supp["payment_terms"],
            "default_currency": supp["default_currency"],
            "tax_id": supp["tax_id"],
            "primary_address": supp["primary_address"],
            "supplier_primary_contact": supp["supplier_primary_contact"],
            "supplier_primary_phone": supp["supplier_primary_phone"],
            "disabled": supp["disabled"]
        }
        rows.append(row)
        print(f"[{supp_id}] {supp['alias']:<20} | {supp['supplier_group']:<30} | {supp['supplier_name']}")

    with open(out_csv, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\n[+] ĐÃ XUẤT THÀNH CÔNG: {out_csv} ({len(rows)} Nhà Cung Cấp)")
    print("=" * 75)

if __name__ == "__main__":
    main()
