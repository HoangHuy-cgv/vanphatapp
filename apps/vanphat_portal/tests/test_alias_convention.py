"""Guard chuẩn alias: Title Case, không `-`/`_`, áp cho mọi cột alias.

Chạy: python3 -m unittest discover -s apps/vanphat_portal/tests -p "test_*.py"
"""

import csv
import os
import re
import unittest

ALLOWED_CODE_ALIAS = {"HYGIENE-TKV"}

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
FILES = {
    os.path.join(BASE, "data", "clean-data", "customer_master.csv"): "alias",
    os.path.join(BASE, "data", "templates", "customer_master.csv"): "alias",
    os.path.join(BASE, "data", "clean-data", "supplier_master.csv"): "alias",
    os.path.join(BASE, "data", "templates", "supplier_master.csv"): "alias",
    os.path.join(BASE, "data", "clean-data", "item_master.csv"): "custom_alias",
    os.path.join(BASE, "data", "templates", "item_master.csv"): "custom_alias",
}


def title_case_ok(value):
    # Chuẩn Sếp: mỗi từ viết hoa chữ đầu; từ đã HOA nguyên (VẠN AN, XNK, AZ),
    # đơn vị kỹ thuật (K560, 6mic, PET) và ký tự cấu trúc (& / + , " ( )) giữ nguyên.
    for w in value.split(" "):
        if not w or w in ("&", "/", "-", "–", "+", ",", "(", ")", '"'):
            continue
        w = w.strip('",()')
        if not w or w in ("&", "/", "-", "–", "+", ","):
            continue
        if w.isupper() or w.isdigit():
            continue
        if any(ch.isdigit() for ch in w):
            continue
        if not w[:1].isupper():
            return False
    return True


class TestAliasConvention(unittest.TestCase):
    def test_alias_khong_gach_ngang_gach_duoi(self):
        bad = []
        for path, col in FILES.items():
            with open(path, encoding="utf-8-sig") as f:
                for row in csv.DictReader(f):
                    key = row.get("name") or row.get("item_code") or "?"
                    val = (row.get(col) or "").strip()
                    if val in ALLOWED_CODE_ALIAS:
                        continue
                    if "-" in val or "_" in val:
                        bad.append(f"{os.path.basename(path)}:{key}={val}")
        self.assertEqual(bad, [])

    def test_alias_title_case_moi_tu(self):
        bad = []
        for path, col in FILES.items():
            with open(path, encoding="utf-8-sig") as f:
                for row in csv.DictReader(f):
                    key = row.get("name") or row.get("item_code") or "?"
                    val = (row.get(col) or "").strip()
                    if val and not title_case_ok(val):
                        bad.append(f"{os.path.basename(path)}:{key}={val}")
        self.assertEqual(bad, [])

    def test_alias_customer_active_khong_trung(self):
        # Chuẩn Sếp: customer + supplier active không trùng; TRUC trùng tên
        # thật (khác mã trục) được giữ, phân biệt bằng item_code.
        for base in ("clean-data", "templates"):
            path = os.path.join(BASE, "data", base, "customer_master.csv")
            with open(path, encoding="utf-8-sig") as f:
                seen = {}
                for row in csv.DictReader(f):
                    if (row.get("disabled") or "0").strip() == "1":
                        continue
                    key = (row.get("alias") or "").strip().casefold()
                    if key:
                        seen.setdefault(key, []).append(row.get("name"))
            dups = {k: v for k, v in seen.items() if len(v) > 1}
            self.assertEqual(dups, {}, base)
        for base in ("clean-data", "templates"):
            path = os.path.join(BASE, "data", base, "supplier_master.csv")
            with open(path, encoding="utf-8-sig") as f:
                seen = {}
                for row in csv.DictReader(f):
                    if (row.get("disabled") or "0").strip() == "1":
                        continue
                    key = (row.get("alias") or "").strip().casefold()
                    if key:
                        seen.setdefault(key, []).append(row.get("name"))
            dups = {k: v for k, v in seen.items() if len(v) > 1}
            self.assertEqual(dups, {}, base)

    def test_alias_khong_chua_ma_noi_bo(self):
        pat = re.compile(r"^(KC[-_ ]|COC-|KL[-_ ]|NCC-|PK_)|\bTRUC-", re.I)
        bad = []
        for base in ("clean-data", "templates"):
            for fname, col in (("customer_master.csv", "alias"), ("supplier_master.csv", "alias")):
                path = os.path.join(BASE, "data", base, fname)
                with open(path, encoding="utf-8-sig") as f:
                    for row in csv.DictReader(f):
                        val = (row.get(col) or "").strip()
                        if val and pat.search(val):
                            bad.append(f"{base}/{fname}:{row.get('name')}={val}")
        self.assertEqual(bad, [])


if __name__ == "__main__":
    unittest.main()
