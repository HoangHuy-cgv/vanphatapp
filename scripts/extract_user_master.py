#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script: extract_user_master.py
Mục đích: Trích xuất và chuẩn hóa Danh Mục Người Dùng & Phân Quyền (User & Role)
chuẩn 100% ERPNext Native v16 cho Bao Bì Vạn Phát từ dữ liệu nhân sự thực tế.
"""

import os
import csv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_FILE = os.path.join(BASE_DIR, "data", "clean-data", "user_master.csv")

USERS_DATA = [
    {
        "name": "huy@vanphat.com",
        "email": "huy@vanphat.com",
        "first_name": "Huy",
        "last_name": "Võ Quang",
        "full_name": "Võ Quang Huy",
        "user_type": "System User",
        "role_profile_name": "Ban Giám Đốc",
        "roles": "System Manager,Sales Master Manager,Accounts Manager,Manufacturing Manager,Stock Manager",
        "mobile_no": "0908888888",
        "department": "Ban Giám Đốc",
        "designation": "Giám Đốc Điều Hành",
        "enabled": 1
    },
    {
        "name": "lai@vanphat.com",
        "email": "lai@vanphat.com",
        "first_name": "Lài",
        "last_name": "Nguyễn Thị",
        "full_name": "Nguyễn Thị Lài",
        "user_type": "System User",
        "role_profile_name": "Nhân Viên Kinh Doanh",
        "roles": "Sales User",
        "mobile_no": "0901111111",
        "department": "Phòng Kinh Doanh",
        "designation": "Nhân Viên Kinh Doanh",
        "enabled": 1
    },
    {
        "name": "lam@vanphat.com",
        "email": "lam@vanphat.com",
        "first_name": "Lam",
        "last_name": "Trần Thị",
        "full_name": "Trần Thị Lam",
        "user_type": "System User",
        "role_profile_name": "Nhân Viên Kinh Doanh",
        "roles": "Sales User",
        "mobile_no": "0902222222",
        "department": "Phòng Kinh Doanh",
        "designation": "Nhân Viên Kinh Doanh",
        "enabled": 1
    },
    {
        "name": "nhan@vanphat.com",
        "email": "nhan@vanphat.com",
        "first_name": "Nhàn",
        "last_name": "Lê Thị",
        "full_name": "Lê Thị Nhàn",
        "user_type": "System User",
        "role_profile_name": "Nhân Viên Kinh Doanh",
        "roles": "Sales User",
        "mobile_no": "0903333333",
        "department": "Phòng Kinh Doanh",
        "designation": "Nhân Viên Kinh Doanh",
        "enabled": 1
    },
    {
        "name": "giang@vanphat.com",
        "email": "giang@vanphat.com",
        "first_name": "Giang",
        "last_name": "Phạm Hương",
        "full_name": "Phạm Hương Giang",
        "user_type": "System User",
        "role_profile_name": "Nhân Viên Kinh Doanh",
        "roles": "Sales User",
        "mobile_no": "0904444444",
        "department": "Phòng Kinh Doanh",
        "designation": "Nhân Viên Kinh Doanh",
        "enabled": 1
    },
    {
        "name": "phuc@vanphat.com",
        "email": "phuc@vanphat.com",
        "first_name": "Phúc",
        "last_name": "Nguyễn Hoàng",
        "full_name": "Nguyễn Hoàng Phúc",
        "user_type": "System User",
        "role_profile_name": "Nhân Viên Kinh Doanh",
        "roles": "Sales User",
        "mobile_no": "0905555555",
        "department": "Phòng Kinh Doanh",
        "designation": "Nhân Viên Kinh Doanh",
        "enabled": 1
    },
    {
        "name": "duyen@vanphat.com",
        "email": "duyen@vanphat.com",
        "first_name": "Duyên",
        "last_name": "Trần Mỹ",
        "full_name": "Trần Mỹ Duyên",
        "user_type": "System User",
        "role_profile_name": "Nhân Viên Kinh Doanh",
        "roles": "Sales User",
        "mobile_no": "0906666666",
        "department": "Phòng Kinh Doanh",
        "designation": "Nhân Viên Kinh Doanh",
        "enabled": 1
    },
    {
        "name": "quynhanh@vanphat.com",
        "email": "quynhanh@vanphat.com",
        "first_name": "Quỳnh Anh",
        "last_name": "Đặng",
        "full_name": "Đặng Quỳnh Anh",
        "user_type": "System User",
        "role_profile_name": "Kế Toán Viên",
        "roles": "Accounts User",
        "mobile_no": "0907777777",
        "department": "Phòng Kế Toán",
        "designation": "Kế Toán Công Nợ & Thu Chi",
        "enabled": 1
    },
    {
        "name": "ben@vanphat.com",
        "email": "ben@vanphat.com",
        "first_name": "Ben",
        "last_name": "Trần Văn",
        "full_name": "Trần Văn Ben",
        "user_type": "System User",
        "role_profile_name": "Quản Đốc Sản Xuất",
        "roles": "Manufacturing User",
        "mobile_no": "0909999991",
        "department": "Phân Xưởng Bao Bì",
        "designation": "Quản Đốc Phân Xưởng Ghép - Cắt",
        "enabled": 1
    },
    {
        "name": "maythoi@vanphat.com",
        "email": "maythoi@vanphat.com",
        "first_name": "Dư & Chiến",
        "last_name": "Tổ Máy Thổi",
        "full_name": "Tổ Vận Hành Máy Thổi PE",
        "user_type": "System User",
        "role_profile_name": "Vận Hành Sản Xuất",
        "roles": "Manufacturing User",
        "mobile_no": "0909999992",
        "department": "Phân Xưởng Thổi Màng",
        "designation": "Tổ Trưởng Kỹ Thuật Máy Thổi",
        "enabled": 1
    },
    {
        "name": "kho@vanphat.com",
        "email": "kho@vanphat.com",
        "first_name": "Vũ",
        "last_name": "Đội Kho & Xe",
        "full_name": "Tổ Thủ Kho & Giao Nhận Vạn Phát",
        "user_type": "System User",
        "role_profile_name": "Thủ Kho",
        "roles": "Stock User",
        "mobile_no": "0909999993",
        "department": "Bộ Phận Kho & Giao Nhận",
        "designation": "Thủ Kho Vật Lý & Giao Vận",
        "enabled": 1
    }
]

def main():
    fieldnames = [
        "name", "email", "first_name", "last_name", "full_name",
        "user_type", "role_profile_name", "roles", "mobile_no",
        "department", "designation", "enabled"
    ]
    with open(OUTPUT_FILE, mode="w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for u in USERS_DATA:
            writer.writerow(u)
    print(f"Đã xuất thành công {len(USERS_DATA)} người dùng chuẩn ERPNext Native v16 vào: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
