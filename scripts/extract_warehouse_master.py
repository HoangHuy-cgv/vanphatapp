#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Thiết lập Danh mục Kho Hàng (DocType Warehouse) chuẩn 100% ERPNext Native v16
Tinh giản tối đa theo dòng chảy sản xuất thực tế tại Bao Bì Vạn Phát:
1. Kho Nguyên Vật Liệu (NVL): Màng PET in từ NCC, màng thô PE/PA, keo ghép, dung môi EA, vòi nắp, thùng carton.
2. Kho Bán Thành Phẩm (BTP): Cuộn màng ghép phức hợp sau máy ghép chờ cắt túi.
3. Kho Thành Phẩm (TP): Túi màng ghép đặt riêng, túi zipper, túi phôi NGCS và túi in lụa hoàn thiện đóng thùng.
4. Kho Trục In (TRUC): Bộ trục in ống đồng của khách hàng.
5. Kho Phế Liệu (PHE-LIEU): Phế liệu màng xén biên và màng lỗi thu hồi bán tái chế.

ERPNext Native v16 Attributes:
- name: Mã kho hệ thống ([warehouse_code] - VP)
- warehouse_name: Tên kho chuẩn tiếng Việt
- warehouse_code: Mã viết tắt (NVL, BTP, TP, TRUC, PHE-LIEU)
- warehouse_type: Stores | Work In Progress | Finished Goods | Scrap
- parent_warehouse: All Warehouses
- is_group: 0 (Kho thực tế có quản lý số lượng và giá trị tồn kho)
- account: Tài khoản kế toán tương ứng (152, 154, 155, 153)
- description: Mô tả nghiệp vụ và loại hàng hóa lưu trữ
- disabled: 0
"""

import os
import csv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(BASE_DIR, "data", "clean-data")

WAREHOUSES = [
    {
        "name": "NVL - VP",
        "warehouse_name": "Kho Nguyên Vật Liệu",
        "warehouse_code": "NVL",
        "warehouse_type": "Stores",
        "parent_warehouse": "All Warehouses",
        "is_group": 0,
        "account": "152 - Nguyên liệu, vật liệu",
        "description": "Lưu trữ cuộn màng PET in từ NCC, cuộn màng thô (PE sữa, PA, MPET, OPP), keo ghép polyurethane, dung môi Ethyl Acetate (EA), phụ kiện vòi nắp và thùng carton đóng gói.",
        "disabled": 0
    },
    {
        "name": "BTP - VP",
        "warehouse_name": "Kho Bán Thành Phẩm",
        "warehouse_code": "BTP",
        "warehouse_type": "Work In Progress",
        "parent_warehouse": "All Warehouses",
        "is_group": 0,
        "account": "154 - Chi phí sản xuất kinh doanh dở dang",
        "description": "Lưu trữ cuộn màng ghép phức hợp sau công đoạn ghép màng khô, đang ủ nhiệt lưu hóa keo hoặc chờ chuyển sang máy cắt dán túi.",
        "disabled": 0
    },
    {
        "name": "TP - VP",
        "warehouse_name": "Kho Thành Phẩm",
        "warehouse_code": "TP",
        "warehouse_type": "Finished Goods",
        "parent_warehouse": "All Warehouses",
        "is_group": 0,
        "account": "155 - Thành phẩm",
        "description": "Lưu trữ túi màng ghép đặt riêng hoàn thiện, túi zipper mua ngoài, túi phôi NGCS có sẵn và túi sau khi gia công in lụa hoàn tất đóng thùng chờ xuất giao.",
        "disabled": 0
    },
    {
        "name": "TRUC - VP",
        "warehouse_name": "Kho Trục In",
        "warehouse_code": "TRUC",
        "warehouse_type": "Stores",
        "parent_warehouse": "All Warehouses",
        "is_group": 0,
        "account": "153 - Công cụ dụng cụ",
        "description": "Quản lý danh mục các bộ trục in ống đồng khắc laser của khách hàng, theo dõi thông số chu vi, chiều dài và lịch sử điều chuyển vị trí.",
        "disabled": 0
    },
    {
        "name": "PHE-LIEU - VP",
        "warehouse_name": "Kho Phế Liệu",
        "warehouse_code": "PHE-LIEU",
        "warehouse_type": "Scrap",
        "parent_warehouse": "All Warehouses",
        "is_group": 0,
        "account": "152 - Nguyên liệu, vật liệu",
        "description": "Thu hồi phế liệu màng nhựa PE sữa xén biên và màng ghép phức hợp phế thải trong quá trình canh chỉnh máy để cân ký bán thanh lý tái chế.",
        "disabled": 0
    }
]

def main():
    print("=" * 75)
    print("XUẤT DANH MỤC KHO HÀNG (DocType Warehouse) - CHUẨN ERPNext v16 NATIVE")
    print("=" * 75)

    os.makedirs(OUT_DIR, exist_ok=True)
    out_csv = os.path.join(OUT_DIR, "warehouse_master.csv")

    fieldnames = [
        "name",
        "warehouse_name",
        "warehouse_code",
        "warehouse_type",
        "parent_warehouse",
        "is_group",
        "account",
        "description",
        "disabled"
    ]

    for w in WAREHOUSES:
        print(f"[{w['warehouse_code']:<8}] {w['warehouse_name']:<25} | Loại: {w['warehouse_type']:<18} | TK: {w['account']}")

    with open(out_csv, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(WAREHOUSES)

    print(f"\n[+] ĐÃ XUẤT THÀNH CÔNG: {out_csv} ({len(WAREHOUSES)} Kho chuẩn hóa)")
    print("=" * 75)

if __name__ == "__main__":
    main()
