#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script: generate_packaging_boms.py
Sinh định mức sản xuất 2 cấp (BOM - Bill of Materials) chuẩn ERPNext v16 Native
Dựa trên tam giác kiểm chứng (Triangulation):
1. Raw-data thực tế từ xưởng: TIẾN ĐỘ SẢN XUẤT.xlsx & Nhap xuat ton NVL-T9.xlsx
2. Đặc tả kỹ thuật nội bộ: docs/specs/packaging-calculation-spec.md
3. Chuẩn ngành bao bì màng ghép: ASTM D792, Dry Bond Lamination, 2-up Totani Pouch Making
4. Quy cách đóng thùng carton rỗng chuẩn xác của Sếp:
   - Túi lớn (3.2Kg - 3.8Kg): 2.5 thùng / 1.000 túi (400 túi/thùng)
   - Túi nhỏ & trung (0.6Kg - 2L): 2.0 thùng / 1.000 túi (500 túi/thùng)
"""

import os
import csv
import math

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEAN_DIR = os.path.join(BASE_DIR, "data", "clean-data")

def load_clean_items():
    path = os.path.join(CLEAN_DIR, "item_master.csv")
    with open(path, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))

def main():
    print("=" * 75)
    print("KHỞI TẠO ĐỊNH MỨC SẢN XUẤT BOM 2 CẤP (CHUẨN ERPNext v16 NATIVE)")
    print("=" * 75)

    items = load_clean_items()
    item_map = {it["item_code"]: it for it in items}

    bom_masters = []
    bom_items = []

    # =========================================================================
    # CẤP 1: BOM CUỘN MÀNG GHÉP PHỨC HỢP BTP (Đơn vị tính: 1.000 mét dài - m)
    # =========================================================================
    # Bản đồ cấu hình kỹ thuật từng cuộn BTP
    # btp_code: {pet_in, pe_layer, pa_layer, mpet_layer, is_4_layers}
    BTP_CONFIGS = {
        "BTP-00001": {"pet": "NVL-00028", "pe": "NVL-00004", "pa": "NVL-00009", "layers": 3, "width_mm": 800, "pe_mic": 190, "pa_mic": 15}, # 888 Phấn Thơm
        "BTP-00002": {"pet": "NVL-00029", "pe": "NVL-00004", "pa": "NVL-00009", "layers": 3, "width_mm": 800, "pe_mic": 190, "pa_mic": 15}, # 888 Huyền Bí
        "BTP-00003": {"pet": "NVL-00030", "pe": "NVL-00004", "pa": "NVL-00009", "layers": 3, "width_mm": 800, "pe_mic": 190, "pa_mic": 15}, # 888 Đam Mê
        "BTP-00004": {"pet": "NVL-00031", "pe": "NVL-00004", "pa": "NVL-00009", "layers": 3, "width_mm": 800, "pe_mic": 190, "pa_mic": 15}, # NGCS Đỏ - Tím
        "BTP-00005": {"pet": "NVL-00032", "pe": "NVL-00004", "pa": "NVL-00009", "layers": 3, "width_mm": 800, "pe_mic": 190, "pa_mic": 15}, # NGCS Hồng - Xanh
        "BTP-00006": {"pet": "NVL-00033", "pe": "NVL-00003", "pa": "NVL-00008", "layers": 3, "width_mm": 780, "pe_mic": 190, "pa_mic": 15}, # Minh Râu Tím
        "BTP-00007": {"pet": "NVL-00034", "pe": "NVL-00004", "pa": "NVL-00009", "layers": 3, "width_mm": 750, "pe_mic": 190, "pa_mic": 15}, # TopGia 2L
        "BTP-00008": {"pet": "NVL-00035", "pe": "NVL-00004", "pa": "NVL-00009", "layers": 3, "width_mm": 800, "pe_mic": 190, "pa_mic": 15}, # Softy 3L
        "BTP-00009": {"pet": "NVL-00036", "pe": "NVL-00004", "pa": "NVL-00009", "layers": 3, "width_mm": 900, "pe_mic": 190, "pa_mic": 15}, # FUTA Xanh MT
        "BTP-00010": {"pet": "NVL-00037", "pe": "NVL-00004", "pa": "NVL-00009", "layers": 3, "width_mm": 900, "pe_mic": 190, "pa_mic": 15}, # FUTA Xanh MS
        "BTP-00011": {"pet": "NVL-00038", "pe": "NVL-00004", "pa": "NVL-00009", "layers": 3, "width_mm": 900, "pe_mic": 190, "pa_mic": 15}, # FUTA Tím MT
        "BTP-00012": {"pet": "NVL-00039", "pe": "NVL-00004", "pa": "NVL-00009", "layers": 3, "width_mm": 900, "pe_mic": 190, "pa_mic": 15}, # FUTA Tím MS
        "BTP-00013": {"pet": "NVL-00028", "pe": "NVL-00001", "pa": "",          "layers": 2, "width_mm": 180, "pe_mic": 160, "pa_mic": 0},  # Đáy đứng 3.2Kg
        "BTP-00014": {"pet": "NVL-00045", "pe": "NVL-00004", "pa": "NVL-00009", "mpet": "NVL-00018", "layers": 4, "width_mm": 800, "pe_mic": 190, "pa_mic": 15}, # BABA 3.6Kg 4 lớp
        "BTP-00015": {"pet": "NVL-00046", "pe": "NVL-00004", "pa": "NVL-00009", "layers": 3, "width_mm": 800, "pe_mic": 190, "pa_mic": 15}, # Năm Tàu
        "BTP-00016": {"pet": "NVL-00047", "pe": "NVL-00004", "pa": "NVL-00009", "layers": 3, "width_mm": 750, "pe_mic": 190, "pa_mic": 15}  # TopGia 1L Đắm Say
    }

    print("\n1. Tạo BOM Cấp 1 (16 Cuộn Màng Ghép BTP):")
    for btp_code, cfg in BTP_CONFIGS.items():
        if btp_code not in item_map:
            continue
        btp_item = item_map[btp_code]
        bom_no = f"BOM-{btp_code}-001"
        w_m = cfg["width_mm"] / 1000.0

        # Khối lượng màng thô cho 1000m (tỷ trọng ASTM: PE=0.93, PA=1.15, MPET=1.40, hao hụt ghép 2%)
        kg_pe = round(1000.0 * w_m * cfg["pe_mic"] * 0.93 / 1000.0 * 1.02, 1)
        kg_pa = round(1000.0 * w_m * cfg["pa_mic"] * 1.15 / 1000.0 * 1.02, 1) if cfg.get("pa") else 0

        # Keo, Đóng rắn, Dung môi theo cấu trúc lớp
        is_4 = cfg["layers"] == 4
        kg_keo = 2.0 if is_4 else 1.2
        kg_dong_ran = 2.0 if is_4 else 1.2
        kg_ea = 8.0 if is_4 else 4.8

        bom_masters.append({
            "bom_no": bom_no,
            "item": btp_code,
            "item_name": btp_item["item_name"],
            "quantity": 1000.0,
            "uom": "m",
            "is_active": 1,
            "is_default": 1,
            "process_loss_percentage": 2.0,
            "operations": "Ghép Màng Khô (WS-GHEP-01)",
            "description": f"Định mức ghép 1.000m cuộn {btp_item['custom_alias']} (Khổ {cfg['width_mm']}mm, {cfg['layers']} lớp, hao hụt ghép 2.0%)."
        })

        # 1. Màng in PET
        pet_item = item_map.get(cfg["pet"], {})
        bom_items.append({
            "bom_no": bom_no,
            "item_code": cfg["pet"],
            "item_name": pet_item.get("item_name", "Cuộn màng PET in"),
            "qty": 1020.0,
            "uom": "m",
            "scrap_pct": 2.0,
            "note": "Màng PET in ống đồng từ NCC (1000m + 2% hao hụt canh máy)"
        })

        # 2. Màng PE sữa (mua từ máy thổi)
        pe_item = item_map.get(cfg["pe"], {})
        bom_items.append({
            "bom_no": bom_no,
            "item_code": cfg["pe"],
            "item_name": pe_item.get("item_name", "Cuộn màng PE sữa"),
            "qty": kg_pe,
            "uom": "Kg",
            "scrap_pct": 2.0,
            "note": f"Màng PE sữa hàn dán dày {cfg['pe_mic']}mic mua từ máy thổi ({kg_pe} Kg)"
        })

        # 3. Màng PA (nếu có)
        if cfg.get("pa") and kg_pa > 0:
            pa_item = item_map.get(cfg["pa"], {})
            bom_items.append({
                "bom_no": bom_no,
                "item_code": cfg["pa"],
                "item_name": pa_item.get("item_name", "Cuộn màng PA"),
                "qty": kg_pa,
                "uom": "Kg",
                "scrap_pct": 2.0,
                "note": f"Màng PA rào cản chống bục thủng 15mic ({kg_pa} Kg)"
            })

        # 4. Màng MPET (nếu có mạ nhôm 4 lớp)
        if cfg.get("mpet"):
            kg_mpet = round(1000.0 * w_m * 12 * 1.40 / 1000.0 * 1.02, 1)
            mpet_item = item_map.get(cfg["mpet"], {})
            bom_items.append({
                "bom_no": bom_no,
                "item_code": cfg["mpet"],
                "item_name": mpet_item.get("item_name", "Cuộn màng MPET 12mic"),
                "qty": kg_mpet,
                "uom": "Kg",
                "scrap_pct": 2.0,
                "note": f"Lớp màng MPET mạ nhôm cản sáng 12mic ({kg_mpet} Kg)"
            })

        # 5. Keo ghép PU
        bom_items.append({
            "bom_no": bom_no,
            "item_code": "NVL-00025",
            "item_name": "Keo ghép màng Polyurethane D-9700",
            "qty": kg_keo,
            "uom": "Kg",
            "scrap_pct": 0.0,
            "note": f"Keo polyurethane ghép màng khô ({kg_keo} Kg)"
        })

        # 6. Chất đóng rắn
        bom_items.append({
            "bom_no": bom_no,
            "item_code": "NVL-00026",
            "item_name": "Chất đóng rắn keo ghép CL-3192K",
            "qty": kg_dong_ran,
            "uom": "Kg",
            "scrap_pct": 0.0,
            "note": f"Chất đóng rắn Isocyanate ({kg_dong_ran} Kg)"
        })

        # 7. Dung môi EA
        bom_items.append({
            "bom_no": bom_no,
            "item_code": "NVL-00027",
            "item_name": "Dung môi công nghiệp Ethyl Acetate (EA)",
            "qty": kg_ea,
            "uom": "Kg",
            "scrap_pct": 0.0,
            "note": f"Dung môi pha keo bay hơi buồng sấy ({kg_ea} Kg)"
        })

        print(f"   [+] {bom_no} cho {btp_item['custom_alias']:<20} (PE: {kg_pe}kg, PA: {kg_pa}kg, Keo: {kg_keo}kg)")

    # =========================================================================
    # CẤP 2: BOM TÚI THÀNH PHẨM (Đơn vị tính: 1.000 Túi)
    # =========================================================================
    # Ánh xạ mã TP/NGCS sang cuộn BTP nguồn
    # (Túi lớn >= 3.2Kg: cut_step ~ 560mm, hộp 2.5 thùng; Túi trung 2L: ~ 480mm, hộp 2.0 thùng; Túi nhỏ: ~ 340mm, hộp 2.0 thùng)
    TP_BTP_MAP = {
        # Dòng 888 3.2Kg (TP-00001 .. 00003) -> BTP-00001, BTP-00002, BTP-00003
        "TP-00001": {"btp": "BTP-00001", "cut_mm": 560.0, "size": "large"},
        "TP-00002": {"btp": "BTP-00002", "cut_mm": 560.0, "size": "large"},
        "TP-00003": {"btp": "BTP-00003", "cut_mm": 560.0, "size": "large"},
        # Dòng 888 2Kg (TP-00004 .. 00006)
        "TP-00004": {"btp": "BTP-00001", "cut_mm": 480.0, "size": "medium"},
        "TP-00005": {"btp": "BTP-00002", "cut_mm": 480.0, "size": "medium"},
        "TP-00006": {"btp": "BTP-00003", "cut_mm": 480.0, "size": "medium"},
        # Dòng 888 0.6Kg (TP-00007 .. 00011)
        "TP-00007": {"btp": "BTP-00001", "cut_mm": 340.0, "size": "small"},
        "TP-00008": {"btp": "BTP-00002", "cut_mm": 340.0, "size": "small"},
        "TP-00009": {"btp": "BTP-00003", "cut_mm": 340.0, "size": "small"},
        "TP-00010": {"btp": "BTP-00001", "cut_mm": 340.0, "size": "small"},
        "TP-00011": {"btp": "BTP-00001", "cut_mm": 340.0, "size": "small"},
        # Dòng Minh Râu (TP-00012, TP-00013) -> BTP-00006
        "TP-00012": {"btp": "BTP-00006", "cut_mm": 564.0, "size": "large"},
        "TP-00013": {"btp": "BTP-00006", "cut_mm": 564.0, "size": "large"},
        # Dòng Lamy 2Kg (TP-00014, TP-00015)
        "TP-00014": {"btp": "BTP-00007", "cut_mm": 480.0, "size": "medium"},
        "TP-00015": {"btp": "BTP-00007", "cut_mm": 480.0, "size": "medium"},
        # BABA 3.6Kg (TP-00016) -> BTP-00014
        "TP-00016": {"btp": "BTP-00014", "cut_mm": 580.0, "size": "large"},
        # Vietcoat 5L (TP-00017) -> BTP-00008
        "TP-00017": {"btp": "BTP-00008", "cut_mm": 600.0, "size": "large"},
        # TopGia (TP-00019, 00020, 00021) -> BTP-00007, BTP-00016
        "TP-00019": {"btp": "BTP-00007", "cut_mm": 480.0, "size": "medium"},
        "TP-00020": {"btp": "BTP-00016", "cut_mm": 420.0, "size": "small"},
        "TP-00021": {"btp": "BTP-00016", "cut_mm": 420.0, "size": "small"},
        # Softy 3L (TP-00022) -> BTP-00008
        "TP-00022": {"btp": "BTP-00008", "cut_mm": 560.0, "size": "large"},
        # Sachpoong & Raptor Clean (TP-00023 .. 00025)
        "TP-00023": {"btp": "BTP-00001", "cut_mm": 560.0, "size": "large"},
        "TP-00024": {"btp": "BTP-00001", "cut_mm": 340.0, "size": "small"},
        "TP-00025": {"btp": "BTP-00001", "cut_mm": 340.0, "size": "small"},
        # Trần Quân 2Kg & DPClean (TP-00026, 00027)
        "TP-00026": {"btp": "BTP-00001", "cut_mm": 480.0, "size": "medium"},
        "TP-00027": {"btp": "BTP-00001", "cut_mm": 340.0, "size": "small"},
        # Bluum & Premium 3.2Kg (TP-00028 .. 00031)
        "TP-00028": {"btp": "BTP-00001", "cut_mm": 560.0, "size": "large"},
        "TP-00029": {"btp": "BTP-00001", "cut_mm": 560.0, "size": "large"},
        "TP-00030": {"btp": "BTP-00001", "cut_mm": 560.0, "size": "large"},
        "TP-00031": {"btp": "BTP-00003", "cut_mm": 560.0, "size": "large"},
        # Yumi, Sofia, Clean, Futa (TP-00032 .. 00037)
        "TP-00032": {"btp": "BTP-00001", "cut_mm": 560.0, "size": "large"},
        "TP-00033": {"btp": "BTP-00001", "cut_mm": 560.0, "size": "large"},
        "TP-00034": {"btp": "BTP-00001", "cut_mm": 560.0, "size": "large"},
        "TP-00035": {"btp": "BTP-00001", "cut_mm": 480.0, "size": "medium"},
        "TP-00036": {"btp": "BTP-00009", "cut_mm": 560.0, "size": "large"},
        "TP-00037": {"btp": "BTP-00001", "cut_mm": 560.0, "size": "large"},
        # Thực phẩm Năm Tàu (TP-00045) -> BTP-00015
        "TP-00045": {"btp": "BTP-00015", "cut_mm": 480.0, "size": "medium"},

        # 15 Túi phôi nước giặt có sẵn (NGCS-00001 .. 00015)
        # Nhỏ 2L (00001 .. 00005) -> cut 480mm, medium
        "NGCS-00001": {"btp": "BTP-00004", "cut_mm": 480.0, "size": "medium"},
        "NGCS-00002": {"btp": "BTP-00005", "cut_mm": 480.0, "size": "medium"},
        "NGCS-00003": {"btp": "BTP-00004", "cut_mm": 480.0, "size": "medium"},
        "NGCS-00004": {"btp": "BTP-00005", "cut_mm": 480.0, "size": "medium"},
        "NGCS-00005": {"btp": "BTP-00004", "cut_mm": 480.0, "size": "medium"},
        # Trung 3.2Kg (00006 .. 00010) -> cut 560mm, large
        "NGCS-00006": {"btp": "BTP-00004", "cut_mm": 560.0, "size": "large"},
        "NGCS-00007": {"btp": "BTP-00005", "cut_mm": 560.0, "size": "large"},
        "NGCS-00008": {"btp": "BTP-00004", "cut_mm": 560.0, "size": "large"},
        "NGCS-00009": {"btp": "BTP-00005", "cut_mm": 560.0, "size": "large"},
        "NGCS-00010": {"btp": "BTP-00004", "cut_mm": 560.0, "size": "large"},
        # Lớn 3.8Kg (00011 .. 00015) -> cut 580mm, large
        "NGCS-00011": {"btp": "BTP-00004", "cut_mm": 580.0, "size": "large"},
        "NGCS-00012": {"btp": "BTP-00005", "cut_mm": 580.0, "size": "large"},
        "NGCS-00013": {"btp": "BTP-00004", "cut_mm": 580.0, "size": "large"},
        "NGCS-00014": {"btp": "BTP-00005", "cut_mm": 580.0, "size": "large"},
        "NGCS-00015": {"btp": "BTP-00004", "cut_mm": 580.0, "size": "large"}
    }

    print("\n2. Tạo BOM Cấp 2 (Túi Thành Phẩm Đặt Riêng & NGCS):")
    for tp_code, cfg in TP_BTP_MAP.items():
        if tp_code not in item_map:
            continue
        tp_item = item_map[tp_code]
        bom_no = f"BOM-{tp_code}-001"

        # Mét màng BTP cần cho 1.000 túi (chạy 2 lane, hao hụt cắt 2.5%)
        # m_btp = (1000 / 2) * (cut_mm / 1000) * 1.025
        m_btp = round(500.0 * (cfg["cut_mm"] / 1000.0) * 1.025, 1)

        # Định mức thùng carton chuẩn xác của Sếp:
        # Túi lớn: 2.5 thùng / 1000 túi (400 túi/thùng)
        # Túi trung & nhỏ: 2.0 thùng / 1000 túi (500 túi/thùng)
        carton_qty = 2.5 if cfg["size"] == "large" else 2.0
        carton_note = "Đóng gói tiêu chuẩn 400 túi lớn xẹp/thùng 60x40x40" if cfg["size"] == "large" else "Đóng gói tiêu chuẩn 500 túi xẹp/thùng 60x40x40"

        # Kiểm tra vòi
        acc = tp_item.get("custom_accessory_spec", "")
        has_spout_16 = "16mm" in acc
        has_spout_10 = "10mm" in acc

        ops_desc = "Cắt Dán Túi (WS-CAT-01)"
        if has_spout_16 or has_spout_10:
            ops_desc += " -> Đóng Vòi Hàn Nhiệt (WS-VOI-01)"

        bom_masters.append({
            "bom_no": bom_no,
            "item": tp_code,
            "item_name": tp_item["item_name"],
            "quantity": 1000.0,
            "uom": "Túi",
            "is_active": 1,
            "is_default": 1,
            "process_loss_percentage": 2.5,
            "operations": ops_desc,
            "description": f"Định mức sản xuất 1.000 túi {tp_item['custom_alias']} (Bước cắt {cfg['cut_mm']}mm, 2 lane, hao hụt 2.5%)."
        })

        # 1. Cuộn màng BTP
        btp_item = item_map.get(cfg["btp"], {})
        bom_items.append({
            "bom_no": bom_no,
            "item_code": cfg["btp"],
            "item_name": btp_item.get("item_name", "Cuộn màng ghép BTP"),
            "qty": m_btp,
            "uom": "m",
            "scrap_pct": 2.5,
            "note": f"Cuộn màng ghép BTP chạy 2 lane (Bước cắt {cfg['cut_mm']}mm x 1.000 túi + 2.5% hao hụt)"
        })

        # 2. Phụ kiện vòi (nếu có)
        if has_spout_16:
            bom_items.append({
                "bom_no": bom_no,
                "item_code": "NVL-00040",
                "item_name": "Vòi nhựa đóng gói phi 16mm kèm nắp chống tràn",
                "qty": 1010.0,
                "uom": "Cái",
                "scrap_pct": 1.0,
                "note": "1 vòi 16mm/túi + 1% hao hụt máy hàn nhiệt"
            })
        elif has_spout_10:
            bom_items.append({
                "bom_no": bom_no,
                "item_code": "NVL-00041",
                "item_name": "Vòi nhựa đóng gói phi 10mm kèm nắp",
                "qty": 1010.0,
                "uom": "Cái",
                "scrap_pct": 1.0,
                "note": "1 vòi 10mm/túi + 1% hao hụt máy hàn nhiệt"
            })

        # 3. Thùng carton đóng gói xuất xưởng
        bom_items.append({
            "bom_no": bom_no,
            "item_code": "NVL-00044",
            "item_name": "Thùng carton 5 lớp đóng gói giao hàng túi",
            "qty": carton_qty,
            "uom": "Cái",
            "scrap_pct": 0.0,
            "note": carton_note
        })

        print(f"   [+] {bom_no} cho {tp_item['custom_alias']:<22} (Màng BTP: {m_btp:>5}m, Thùng: {carton_qty} cái)")

    # Ghi file sạch
    out_master_csv = os.path.join(CLEAN_DIR, "bom_master.csv")
    out_items_csv = os.path.join(CLEAN_DIR, "bom_items.csv")

    # Siết chặt quy tắc UI/UX: Đảm bảo mọi dòng vật tư đều có custom_alias ngắn gọn
    for bi in bom_items:
        code = bi.get("item_code")
        matched = item_map.get(code, {})
        bi["custom_alias"] = matched.get("custom_alias") or bi.get("item_name") or code

    with open(out_master_csv, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "bom_no", "item", "item_name", "quantity", "uom", "is_active", "is_default",
            "process_loss_percentage", "operations", "description"
        ])
        writer.writeheader()
        writer.writerows(bom_masters)
    print(f"\n[+] Xuất thành công: {out_master_csv} ({len(bom_masters)} BOM Master)")

    with open(out_items_csv, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "bom_no", "item_code", "item_name", "custom_alias", "qty", "uom", "scrap_pct", "note"
        ])
        writer.writeheader()
        writer.writerows(bom_items)
    print(f"[+] Xuất thành công: {out_items_csv} ({len(bom_items)} Dòng chi tiết vật tư BOM Items có custom_alias)")
    print("=" * 75)

if __name__ == "__main__":
    main()
