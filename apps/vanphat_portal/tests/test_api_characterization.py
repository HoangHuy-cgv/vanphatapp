"""Test đặc tả (characterization) cho wrapper `vanphat_portal.api.*`.

Chạy KHÔNG cần bench/site:
    python3 -m unittest discover -s apps/vanphat_portal/tests -p "test_*.py"

Bộ này khoá hành vi của các endpoint đọc/ghi một-doc (preview giá, chi tiết đơn,
ghi nhận cọc, submit, tạo đơn, chi tiết mặt hàng). Endpoint dùng `frappe.qb`
(list_orders, item.get_list, list_quotations) phải verify trên site thật.

Thay đổi đã được Sếp duyệt (2026-02-17):
- `qty` chỉ cộng dòng túi/cuộn (bỏ dòng trục) ở cả list + drawer.
- `cylinder_total` = tiền trục CHƯA VAT (giá NCC thuần) ở mọi màn.
- `product_total` = net_total native − cylinder_total (tiền hàng chưa VAT).
- Thiếu Default Company → báo lỗi rõ ràng, không hardcode tên công ty.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from frappe_stub import FrappeThrow, install  # noqa: E402

install()

from vanphat_portal.api import bao_gia, item, order  # noqa: E402


def base_state():
	"""Dựng dữ liệu giả nền tảng: Company/VP, VAT 8%, KH COSMETIC cọc 50%, Item TP-001."""
	_, state = install()
	state.defaults = {"Company": "VP"}
	state.tax_templates = {"VAT 8%": 0.08}
	state.add(
		"Sales Taxes and Charges Template",
		{"name": "VAT 8%", "company": "VP", "is_default": 1},
	)
	state.add("Sales Taxes and Charges", {"parent": "VAT 8%", "rate": 8.0})
	state.add(
		"Customer",
		{
			"name": "CUST-1",
			"customer_name": "Công ty TNHH Cosmetic",
			"alias": "COSMETIC",
			"payment_terms": "Cọc 50-50",
			"disabled": 0,
		},
	)
	state.add("Payment Terms Template Detail", {"parent": "Cọc 50-50", "invoice_portion": 50.0})
	state.add("Customer Credit Limit", {"parent": "CUST-1", "credit_limit": 0.0})
	state.add(
		"Item",
		{
			"name": "TP-001",
			"item_code": "TP-001",
			"item_name": "Túi đựng nước giặt BABA 500g",
			"custom_alias": "BABA 500g",
			"brand": "",
			"custom_structure_layers": "PET/PA/PE",
			"description": "280 x 340 mm",
			"disabled": 0,
			"is_sales_item": 1,
			"customer_code": "BABA",
		},
	)
	return state


def sales_order(**overrides):
	"""Sales Order chuẩn: net 2.000.000 (túi 1.000.000 + trục 1.000.000), VAT 8%, tổng 2.160.000."""
	doc = {
		"doctype": "Sales Order",
		"name": "SO-1",
		"customer": "CUST-1",
		"customer_name": "Công ty TNHH Cosmetic",
		"company": "VP",
		"transaction_date": "2026-01-01",
		"docstatus": 1,
		"status": "Submitted",
		"net_total": 2000000.0,
		"total_taxes_and_charges": 160000.0,
		"grand_total": 2160000.0,
		"advance_paid": 1500000.0,
		"items": [
			{
				"item_code": "TP-001",
				"item_name": "Túi đựng nước giặt BABA 500g",
				"qty": 100,
				"rate": 10000.0,
				"amount": 1000000.0,
				"uom": "Túi",
			},
			{
				"item_code": "TRUC-IN",
				"item_name": "Trục in (2 cây, NCC Kiến Tâm)",
				"qty": 2,
				"rate": 500000.0,
				"amount": 1000000.0,
				"uom": "Cây",
			},
		],
	}
	doc.update(overrides)
	return doc


class TestOrderPricePreview(unittest.TestCase):
	def test_preview_doc_driven_va_pass_through_truc(self):
		base_state()
		res = order.get_price_preview(
			items=[{"qty": 100, "rate": 1000}],
			customer="CUST-1",
			has_new_cylinders=True,
			cylinder_count=2,
			cylinder_spec={"qty": 2, "unit_price": 500000, "supplier": "Kiến Tâm"},
			company="VP",
		)
		self.assertEqual(res["net_total"], 1100000.0)
		self.assertEqual(res["vat_rate"], 8.0)
		self.assertEqual(res["vat_amount"], 88000.0)
		self.assertEqual(res["tax_template"], "VAT 8%")
		self.assertEqual(res["cylinder_count"], 2)
		self.assertEqual(res["cylinder_rate"], 500000.0)
		self.assertEqual(res["cylinder_total"], 1000000.0)
		self.assertFalse(res["cylinder_pending"])
		self.assertEqual(res["cylinder_supplier"], "Kiến Tâm")
		self.assertEqual(res["grand_total"], 1188000.0)
		self.assertEqual(res["grand_total_final"], 1188000.0)
		self.assertEqual(res["payment_type"], "Trả trước")
		self.assertEqual(res["credit_limit"], 0.0)
		self.assertEqual(res["deposit_pct"], 50.0)
		# 50% tiền hàng (đã VAT theo doc native) + 100% tiền trục
		self.assertEqual(res["required_deposit"], 1188000 * 0.5 + 1000000)

	def test_preview_thieu_gia_ncc_thi_pending_truthful(self):
		base_state()
		res = order.get_price_preview(
			items=[{"qty": 100, "rate": 10000}],
			customer="COSMETIC",
			has_new_cylinders=True,
			cylinder_count=2,
			company="VP",
		)
		self.assertTrue(res["cylinder_pending"])
		self.assertEqual(res["cylinder_total"], 0.0)
		self.assertIsNone(res["grand_total_final"])
		self.assertIsNone(res["required_deposit_final"])
		self.assertEqual(res["cylinder_count"], 2)

	def test_preview_khach_tra_sau_coc_bang_khong(self):
		state = base_state()
		state.rows["Customer Credit Limit"] = [{"parent": "CUST-1", "credit_limit": 50000000.0}]
		res = order.get_price_preview(
			items=[{"qty": 100, "rate": 10000}], customer="CUST-1", company="VP"
		)
		self.assertEqual(res["payment_type"], "Trả sau")
		self.assertEqual(res["credit_limit"], 50000000.0)
		self.assertEqual(res["required_deposit"], 0.0)

	def test_preview_thieu_khach_thi_bao_loi(self):
		base_state()
		with self.assertRaises(FrappeThrow):
			order.get_price_preview(items=[{"qty": 1, "rate": 1}], customer="KHONG-CO", company="VP")


class TestOrderDetails(unittest.TestCase):
	def test_chi_tiet_tach_tien_hang_va_tien_truc_native(self):
		state = base_state()
		state.add("Sales Order", sales_order())
		res = order.get_order_details("SO-1")

		# Tiền: net/tax/grand đọc native, KHÔNG nhân VAT tay
		self.assertEqual(res["net_total"], 2000000.0)
		self.assertEqual(res["vat_amount"], 160000.0)
		self.assertEqual(res["vat_rate"], 8.0)
		self.assertEqual(res["grand_total"], 2160000.0)
		# Tiền trục = giá NCC chưa VAT; tiền hàng = net native − tiền trục
		self.assertEqual(res["cylinder_total"], 1000000.0)
		self.assertEqual(res["product_total"], 1000000.0)
		self.assertEqual(res["required_deposit"], 1000000.0 * 0.5 + 1000000.0)
		self.assertEqual(res["advance_paid"], 1500000.0)
		self.assertEqual(res["outstanding_amount"], 660000.0)
		self.assertEqual(res["deposit_pct"], 69.4)
		# Số lượng chỉ tính dòng túi/cuộn
		self.assertEqual(res["qty"], 100)

		# Phân loại + trình bày giữ nguyên
		self.assertEqual(res["customer_alias"], "COSMETIC")
		self.assertEqual(res["product_group"], "Túi màng ghép")
		self.assertEqual(res["order_tab"], "xuong_sx")
		self.assertEqual(res["uom"], "Túi")
		self.assertEqual(res["materials"], ["PET", "PA", "PE"])
		self.assertEqual(res["dimensions_text"], "280 x 340 mm")
		self.assertEqual(res["brand"], "VẠN PHÁT")
		self.assertEqual([row["is_cylinder"] for row in res["items"]], [False, True])
		self.assertIs(res["can_submit"], False)
		self.assertEqual(res["order_state"], "Chính thức (Đã cọc >=50%)")
		# Chống N+1: brand + lớp cấu trúc + mô tả lấy trong ĐÚNG 1 query (trước là 3)
		item_gets = [call for call in state.calls if call[0] == "get_value" and call[1] == "Item"]
		self.assertEqual(len(item_gets), 1)

	def test_chi_tiet_don_nhap_thieu_coc_thi_hold(self):
		state = base_state()
		state.add("Sales Order", sales_order(docstatus=0, status="Draft", advance_paid=500000.0))
		res = order.get_order_details("SO-1")
		self.assertTrue(res["is_hold"])
		self.assertFalse(res["can_submit"])
		self.assertEqual(res["order_state"], "HOLD (Thiếu cọc)")
		self.assertEqual(res["outstanding_amount"], 1660000.0)

	def test_chi_tiet_khong_ton_tai_thi_bao_loi(self):
		base_state()
		with self.assertRaises(FrappeThrow):
			order.get_order_details("SO-KHONG-CO")


class TestOrderMutations(unittest.TestCase):
	def test_ghi_nhan_coc_du_thi_tu_dong_submit(self):
		state = base_state()
		state.add("Sales Order", sales_order(docstatus=0, status="Draft", advance_paid=0.0))
		res = order.record_order_deposit("SO-1", amount=1500000, note="Cọc lần 1")
		self.assertTrue(res["success"])
		self.assertTrue(res["auto_submitted"])
		self.assertEqual(res["order_state"], "Chính thức (Đã cọc >=50%)")

	def test_ghi_nhan_coc_thieu_thi_giu_hold(self):
		state = base_state()
		state.add("Sales Order", sales_order(docstatus=0, status="Draft", advance_paid=0.0))
		res = order.record_order_deposit("SO-1", amount=1000000)
		self.assertTrue(res["success"])
		self.assertNotIn("auto_submitted", res)
		self.assertEqual(res["order_state"], "HOLD (Thiếu cọc)")
		self.assertTrue(res["is_hold"])

	def test_ghi_nhan_coc_am_thi_bao_loi(self):
		state = base_state()
		state.add("Sales Order", sales_order(docstatus=0, status="Draft"))
		with self.assertRaises(FrappeThrow):
			order.record_order_deposit("SO-1", amount=0)

	def test_submit_don_du_coc(self):
		state = base_state()
		state.add("Sales Order", sales_order(docstatus=0, status="Draft", advance_paid=1500000.0))
		res = order.submit_sales_order("SO-1")
		self.assertEqual(res["name"], "SO-1")
		self.assertEqual(res["docstatus"], 1)

	def test_submit_don_hold_thi_chan(self):
		state = base_state()
		state.add("Sales Order", sales_order(docstatus=0, status="Draft", advance_paid=500000.0))
		with self.assertRaises(FrappeThrow) as ctx:
			order.submit_sales_order("SO-1")
		self.assertIn("HOLD", str(ctx.exception))

	def test_ke_toan_duyet_ngoai_le_hold(self):
		state = base_state()
		state.add("Sales Order", sales_order(docstatus=0, status="Draft", advance_paid=500000.0))
		res = order.accountant_approve_procurement("SO-1", note="Cho chạy tiếp")
		self.assertTrue(res["success"])
		self.assertEqual(res["docstatus"], 1)


class TestCreateSalesOrder(unittest.TestCase):
	def test_tao_don_resolve_alias_va_them_dong_truc_khi_co_gia(self):
		state = base_state()
		res = order.create_sales_order(
			{
				"customer": "COSMETIC",
				"company": "VP",
				"items": [{"item_code": "TP-001", "item_name": "Túi BABA", "qty": 10, "rate": 1000}],
				"has_new_cylinders": True,
				"cylinder_count": 2,
				"cylinder_spec": {"qty": 2, "unit_price": 500000, "supplier": "Kiến Tâm"},
			}
		)
		self.assertTrue(res["success"])
		self.assertEqual(res["status"], "Draft")
		self.assertEqual(len(state.inserted), 1)
		created = state.inserted[0]
		# alias COSMETIC → name native
		self.assertEqual(created["customer"], "CUST-1")
		self.assertEqual(created["company"], "VP")
		self.assertEqual(created["naming_series"], "DH-.YY..MM.-.###")
		self.assertEqual([row.item_code for row in created["items"]], ["TP-001", "TRUC-IN"])
		cylinder = created["items"][1]
		self.assertEqual(cylinder.qty, 2)
		self.assertEqual(cylinder.rate, 500000.0)
		self.assertEqual(cylinder.uom, "Cây")
		self.assertIn("Kiến Tâm", cylinder.item_name)

	def test_tao_don_thieu_gia_truc_thi_khong_them_dong_truc(self):
		state = base_state()
		order.create_sales_order(
			{
				"customer": "CUST-1",
				"company": "VP",
				"items": [{"item_code": "TP-001", "qty": 10, "rate": 1000}],
				"has_new_cylinders": True,
				"cylinder_count": 2,
			}
		)
		created = state.inserted[0]
		self.assertEqual([row.item_code for row in created["items"]], ["TP-001"])

	def test_tao_don_thieu_company_thi_bao_loi(self):
		state = base_state()
		state.defaults = {}
		with self.assertRaises(FrappeThrow):
			order.create_sales_order(
				{
					"customer": "CUST-1",
					"items": [{"item_code": "TP-001", "qty": 1, "rate": 1000}],
				}
			)

	def test_tao_don_thieu_khach_thi_bao_loi(self):
		base_state()
		with self.assertRaises(FrappeThrow):
			order.create_sales_order({"company": "VP", "items": [{"qty": 1, "rate": 1}]})


class TestItemDetail(unittest.TestCase):
	def test_chi_tiet_item_kem_bom_alias_mot_query(self):
		state = base_state()
		state.add(
			"Item",
			{"name": "NVL-1", "item_code": "NVL-1", "item_name": "Màng PET", "custom_alias": "PET 12mic"},
		)
		state.add("Item", {"name": "NVL-2", "item_code": "NVL-2", "item_name": "Màng PE", "custom_alias": ""})
		state.add(
			"BOM",
			{
				"name": "BOM-TP-001",
				"item": "TP-001",
				"is_default": 1,
				"is_active": 1,
				"items": [
					{"item_code": "NVL-1", "item_name": "Màng PET", "qty": 1.0, "rate": 47000.0},
					{"item_code": "NVL-2", "item_name": "Màng PE", "qty": 1.0, "rate": 45000.0},
				],
			},
		)
		res = item.get_detail("TP-001")
		self.assertEqual(res["item"]["item_code"], "TP-001")
		self.assertEqual(res["bom"]["master"]["name"], "BOM-TP-001")
		aliases = [row["custom_alias"] for row in res["bom"]["items"]]
		self.assertEqual(aliases, ["PET 12mic", "Màng PE"])
		# Chống N+1: alias lấy 1 query get_list, không get_value từng dòng
		item_value_calls = [call for call in state.calls if call[0] == "get_value" and call[1] == "Item"]
		self.assertEqual(item_value_calls, [])
		alias_calls = [call for call in state.calls if call[0] == "get_list" and call[1] == "Item"]
		self.assertEqual(len(alias_calls), 1)

	def test_chi_tiet_item_thieu_ma_thi_bao_loi(self):
		base_state()
		with self.assertRaises(FrappeThrow):
			item.get_detail("")


class TestQuotationPreview(unittest.TestCase):
	def test_preview_bg_da_luu_doc_native(self):
		state = base_state()
		state.add(
			"Quotation",
			{
				"name": "BG-1",
				"total": 1000000.0,
				"total_taxes_and_charges": 80000.0,
				"grand_total": 1080000.0,
				"total_qty": 10.0,
			},
		)
		res = bao_gia.get_quotation_price_preview(quotation="BG-1")
		self.assertEqual(res["subtotal"], 1000000.0)
		self.assertEqual(res["tax_amount"], 80000.0)
		self.assertEqual(res["vat_rate"], 8.0)
		self.assertEqual(res["grand_total"], 1080000.0)
		self.assertEqual(res["total_qty"], 10.0)
		self.assertEqual(res["cylinder_total"], 0)

	def test_boot_tra_csrf_user_company(self):
		base_state()
		res = bao_gia.get_boot()
		self.assertEqual(res["user"], "tester@vanphat.com")
		self.assertEqual(res["csrf_token"], "csrf-test")
		self.assertEqual(res["company"], "VP")


if __name__ == "__main__":
	unittest.main()
