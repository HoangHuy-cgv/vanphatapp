#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script: extract_user_master.py
Mục đích: Trích xuất và chuẩn hóa Danh Mục Người Dùng & Phân Quyền (User & Role)
chuẩn 100% ERPNext Native v16 cho Bao Bì Vạn Phát từ dữ liệu nhân sự đã chốt trong Archive.
"""

import os
import csv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_FILE = os.path.join(BASE_DIR, "data", "clean-data", "user_master.csv")

USERS_DATA = [
    {
        "name": "huyhoang@vanphat.io.vn",
        "email": "huyhoang@vanphat.io.vn",
        "first_name": "Huy",
        "last_name": "Hoàng Viết",
        "full_name": "Hoàng Viết Huy",
        "short_name": "HuyHoang",
        "user_type": "System User",
        "role_profile_name": "Quản Trị Hệ Thống",
        "role": "admin",
        "roles": "System Manager",
        "mobile_no": "0919459799",
        "department": "Ban Giám Đốc",
        "designation": "Quản Trị Hệ Thống (Admin)",
        "alias": "huyhoang|huy|Administrator|Admin",
        "enabled": 1
    },
    {
        "name": "lamdoan@vanphat.io.vn",
        "email": "lamdoan@vanphat.io.vn",
        "first_name": "Lam",
        "last_name": "Doãn Thị Tường",
        "full_name": "Doãn Thị Tường Lam",
        "short_name": "LamDoan",
        "user_type": "System User",
        "role_profile_name": "Ban Giám Đốc",
        "role": "giamdoc",
        "roles": "System Manager,Sales Master Manager,Accounts Manager,Manufacturing Manager,Stock Manager",
        "mobile_no": "0909354141",
        "department": "Ban Giám Đốc",
        "designation": "Giám Đốc Điều Hành",
        "alias": "lamdoan|lam|Doãn Lam|Giám đốc Lam|Sếp Lam|giamdoc",
        "enabled": 1
    },
    {
        "name": "phucpham@vanphat.io.vn",
        "email": "phucpham@vanphat.io.vn",
        "first_name": "Phúc",
        "last_name": "Phạm Nguyễn Minh",
        "full_name": "Phạm Nguyễn Minh Phúc",
        "short_name": "PhucPham",
        "user_type": "System User",
        "role_profile_name": "Nhân Viên Kinh Doanh",
        "role": "sale",
        "roles": "Sales User",
        "mobile_no": "0941054234",
        "department": "Phòng Kinh Doanh",
        "designation": "Nhân Viên Kinh Doanh",
        "alias": "phucpham|phuc|Phúc|Minh Phúc|PhÚC",
        "enabled": 1
    },
    {
        "name": "lainguyen@vanphat.io.vn",
        "email": "lainguyen@vanphat.io.vn",
        "first_name": "Lài",
        "last_name": "Nguyễn Thị Hồng",
        "full_name": "Nguyễn Thị Hồng Lài",
        "short_name": "LaiNguyen",
        "user_type": "System User",
        "role_profile_name": "Nhân Viên Kinh Doanh",
        "role": "sale",
        "roles": "Sales User",
        "mobile_no": "0899941791",
        "department": "Phòng Kinh Doanh",
        "designation": "Nhân Viên Kinh Doanh",
        "alias": "lainguyen|lai|Lài|Hồng Lài|Lài Vinplus|LÀI",
        "enabled": 1
    },
    {
        "name": "nhanpham@vanphat.io.vn",
        "email": "nhanpham@vanphat.io.vn",
        "first_name": "Nhàn",
        "last_name": "Phạm Thị",
        "full_name": "Phạm Thị Nhàn",
        "short_name": "NhanPham",
        "user_type": "System User",
        "role_profile_name": "Nhân Viên Kinh Doanh",
        "role": "sale",
        "roles": "Sales User",
        "mobile_no": "0704753809",
        "department": "Phòng Kinh Doanh",
        "designation": "Nhân Viên Kinh Doanh",
        "alias": "nhanpham|nhan|Nhàn|Chị Nhàn|NhÀN",
        "enabled": 1
    },
    {
        "name": "dieunguyen@vanphat.io.vn",
        "email": "dieunguyen@vanphat.io.vn",
        "first_name": "Diệu",
        "last_name": "Nguyễn Thị",
        "full_name": "Nguyễn Thị Diệu",
        "short_name": "DieuNguyen",
        "user_type": "System User",
        "role_profile_name": "Kế Toán Viên",
        "role": "ketoan",
        "roles": "Accounts User",
        "mobile_no": "0938258948",
        "department": "Phòng Kế Toán",
        "designation": "Kế Toán Trưởng & Công Nợ",
        "alias": "dieunguyen|dieu|Diệu|Kế toán Diệu",
        "enabled": 1
    },
    {
        "name": "ngandoan@vanphat.io.vn",
        "email": "ngandoan@vanphat.io.vn",
        "first_name": "Ngân",
        "last_name": "Doãn Thị Kim",
        "full_name": "Doãn Thị Kim Ngân",
        "short_name": "NganDoan",
        "user_type": "System User",
        "role_profile_name": "Kế Toán Viên",
        "role": "ketoan",
        "roles": "Accounts User",
        "mobile_no": "0944622279",
        "department": "Phòng Kế Toán",
        "designation": "Kế Toán Kho & Thu Chi",
        "alias": "ngandoan|ngan|Ngân|Kế toán Ngân",
        "enabled": 1
    },
    {
        "name": "giangtran@vanphat.io.vn",
        "email": "giangtran@vanphat.io.vn",
        "first_name": "Giang",
        "last_name": "Trần Thị Bé",
        "full_name": "Trần Thị Bé Giang",
        "short_name": "GiangTran",
        "user_type": "System User",
        "role_profile_name": "Kế Toán & Kinh Doanh",
        "role": "ketoan,sale",
        "roles": "Accounts User,Sales User",
        "mobile_no": "0705834809",
        "department": "Phòng Kế Toán",
        "designation": "Kế Toán Kiêm Bán Hàng",
        "alias": "giangtran|giang|Giang|Bé Giang|Kế toán Giang",
        "enabled": 1
    },
    {
        "name": "lehuy@vanphat.io.vn",
        "email": "lehuy@vanphat.io.vn",
        "first_name": "Huy",
        "last_name": "Lê",
        "full_name": "Lê Huy",
        "short_name": "HuyLe",
        "user_type": "System User",
        "role_profile_name": "Quản Đốc Sản Xuất",
        "role": "qlsx",
        "roles": "Manufacturing User",
        "mobile_no": "0934381789",
        "department": "Phân Xưởng Sản Xuất",
        "designation": "Quản Lý Kỹ Thuật Sản Xuất",
        "alias": "lehuy|Huy Le|Huy QLSX|Anh Huy SX",
        "enabled": 1
    },
    {
        "name": "kho@vanphat.io.vn",
        "email": "kho@vanphat.io.vn",
        "first_name": "Kho",
        "last_name": "Bộ Phận",
        "full_name": "Tổ Thủ Kho & Giao Vận Vạn Phát",
        "short_name": "KhoVanPhat",
        "user_type": "System User",
        "role_profile_name": "Thủ Kho",
        "role": "kho",
        "roles": "Stock User",
        "mobile_no": "0909999993",
        "department": "Bộ Phận Kho & Giao Nhận",
        "designation": "Thủ Kho Vật Lý & Giao Vận",
        "alias": "kho|Thủ Kho|Anh Vũ|Doi Kho",
        "enabled": 1
    },
    {
        "name": "maythoi@vanphat.io.vn",
        "email": "maythoi@vanphat.io.vn",
        "first_name": "Máy Thổi",
        "last_name": "Tổ Kỹ Thuật",
        "full_name": "Tổ Vận Hành Máy Thổi PE Liên Doanh",
        "short_name": "MayThoi",
        "user_type": "System User",
        "role_profile_name": "Vận Hành Sản Xuất",
        "role": "qlsx",
        "roles": "Manufacturing User",
        "mobile_no": "0909999992",
        "department": "Phân Xưởng Thổi Màng",
        "designation": "Tổ Trưởng Kỹ Thuật Máy Thổi",
        "alias": "maythoi|Máy Thổi|A Dư|A Chiến|Tuệ Nhi",
        "enabled": 1
    }
]

def main():
    fieldnames = [
        "name", "email", "first_name", "last_name", "full_name", "short_name",
        "user_type", "role_profile_name", "role", "roles", "mobile_no",
        "department", "designation", "alias", "enabled"
    ]
    with open(OUTPUT_FILE, mode="w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for u in USERS_DATA:
            writer.writerow(u)
    print(f"Đã xuất thành công {len(USERS_DATA)} người dùng chuẩn ERPNext Native v16 vào: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
