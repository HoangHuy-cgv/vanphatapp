#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Thiết lập Danh mục Công Đoạn (DocType Operation) và Trạm Máy (DocType Workstation)
chuẩn 100% ERPNext Native v16 theo đúng thực tế xưởng Bao Bì Vạn Phát:
1. Ghép Màng Khô (WS-GHEP-01 - Máy Ghép Màng Khô)
2. Cắt Dán Túi (WS-CAT-01 - Máy Cắt Dán Túi Đáy Đứng / 3 Biên)
3. Đóng Vòi Hàn Nhiệt (WS-VOI-01 - Máy Đóng Vòi Tự Động)
4. Thổi Màng PE (WS-THOI-01 - Máy Thổi Màng PE liên doanh Vạn Phát - Tuệ Nhi)

Lưu ý nghiêm ngặt: Chi phí giờ máy hour_rate = 0.0 (Không bịa đặt số liệu).
"""

import os
import csv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(BASE_DIR, "data", "clean-data")

WORKSTATIONS = [
    {
        "name": "WS-GHEP-01",
        "workstation_name": "Máy Ghép Màng Khô",
        "production_capacity": 1,
        "hour_rate": 0.0,
        "description": "Máy ghép màng phức hợp khô (Dry Lamination), sử dụng keo polyurethane và dung môi Ethyl Acetate ghép màng PET in với màng PE sữa hoặc PA."
    },
    {
        "name": "WS-CAT-01",
        "workstation_name": "Máy Cắt Dán Túi Đáy Đứng / 3 Biên",
        "production_capacity": 1,
        "hour_rate": 0.0,
        "description": "Máy cắt dán làm túi màng ghép, dập nhiệt biên hông, gấp đáy đứng (doypack) hoặc túi 3 biên từ cuộn màng ghép BTP."
    },
    {
        "name": "WS-VOI-01",
        "workstation_name": "Máy Đóng Vòi Tự Động",
        "production_capacity": 1,
        "hour_rate": 0.0,
        "description": "Máy hàn nhiệt vòi nhựa tự động, hàn vòi 16mm hoặc 10mm kèm nắp chống tràn lên góc hoặc giữa miệng túi nước giặt xả."
    },
    {
        "name": "WS-THOI-01",
        "workstation_name": "Máy Thổi Màng PE",
        "production_capacity": 1,
        "hour_rate": 0.0,
        "description": "Máy thổi màng nhựa PE sữa khổ rộng 700 - 750mm thuộc cụm máy thổi liên doanh Vạn Phát - Tuệ Nhi."
    }
]

OPERATIONS = [
    {
        "name": "GHEP-MANG",
        "operation_name": "Ghép Màng Khô",
        "workstation": "WS-GHEP-01",
        "description": "Công đoạn ghép cuộn màng PET in với cuộn màng PE sữa/PA bằng keo PU và dung môi EA tạo cuộn màng ghép BTP."
    },
    {
        "name": "CAT-TUI",
        "operation_name": "Cắt Dán Túi",
        "workstation": "WS-CAT-01",
        "description": "Công đoạn cắt và dán nhiệt cuộn màng ghép phức hợp thành túi thành phẩm (túi đáy đứng doypack, túi 3 biên)."
    },
    {
        "name": "DONG-VOI",
        "operation_name": "Đóng Vòi Hàn Nhiệt",
        "workstation": "WS-VOI-01",
        "description": "Công đoạn hàn nhiệt vòi nhựa phi 16mm/10mm lên túi thành phẩm chứa chất lỏng."
    },
    {
        "name": "THOI-MANG",
        "operation_name": "Thổi Màng PE",
        "workstation": "WS-THOI-01",
        "description": "Công đoạn đùn thổi hạt nhựa PE thành cuộn màng PE sữa nguyên liệu (thuộc liên doanh máy thổi)."
    }
]

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    ws_csv = os.path.join(OUT_DIR, "workstation_master.csv")
    op_csv = os.path.join(OUT_DIR, "operation_master.csv")

    with open(ws_csv, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "workstation_name", "production_capacity", "hour_rate", "description"], lineterminator="\n")
        writer.writeheader()
        writer.writerows(WORKSTATIONS)
    print(f"Xuất thành công {ws_csv} ({len(WORKSTATIONS)} Trạm máy)")

    with open(op_csv, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "operation_name", "workstation", "description"], lineterminator="\n")
        writer.writeheader()
        writer.writerows(OPERATIONS)
    print(f"Xuất thành công {op_csv} ({len(OPERATIONS)} Công đoạn)")

if __name__ == "__main__":
    main()
