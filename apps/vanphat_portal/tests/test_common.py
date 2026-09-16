"""Test helper dùng chung + hàm thuần vừa tách khỏi order.py (sau refactor).

Chạy: python3 -m unittest discover -s apps/vanphat_portal/tests -p "test_*.py"
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from frappe_stub import FakeDoc, State, install  # noqa: E402

install()

from vanphat_portal.api import _common, order  # noqa: E402


def fresh_state(**defaults):
	state = State()
	state.defaults = defaults or {"Company": "VP"}
	_, state = install(state)
	return state


class TestCommonPagination(unittest.TestCase):
	def test_mac_dinh_15_va_tran_100(self):
		self.assertEqual(_common.paginate(), (1, 15, 0))
		self.assertEqual(_common.paginate(page=2), (2, 15, 15))
		self.assertEqual(_common.paginate(page=3, page_length=50), (3, 50, 100))
		self.assertEqual(_common.paginate(page_length=500), (1, 100, 0))
		self.assertEqual(_common.paginate(page_length=0), (1, 15, 0))
		self.assertEqual(_common.paginate(page=-5), (1, 15, 0))

	def test_mac_dinh_rieng_cho_master_100(self):
		self.assertEqual(_common.paginate(default=100), (1, 100, 0))
		self.assertEqual(_common.paginate(page=2, default=100), (2, 100, 100))

	def test_page_result_du_5_key_va_total_pages(self):
		res = _common.page_result("items", [{"a": 1}], 2, 15, 31)
		self.assertEqual(res["items"], [{"a": 1}])
		self.assertEqual(res["page"], 2)
		self.assertEqual(res["page_length"], 15)
		self.assertEqual(res["total_count"], 31)
		self.assertEqual(res["total_pages"], 3)
		self.assertEqual(_common.page_result("items", [], 1, 15, 0)["total_pages"], 1)

	def test_text_chuan_hoa(self):
		self.assertEqual(_common.text(None), "")
		self.assertEqual(_common.text("  abc  "), "abc")
		self.assertEqual(_common.text(12), "12")

	def test_as_json(self):
		self.assertEqual(_common.as_json('{"a": 1}'), {"a": 1})
		self.assertEqual(_common.as_json({"a": 1}), {"a": 1})
		self.assertIsNone(_common.as_json(None))


class TestResolveCustomer(unittest.TestCase):
	def test_native_alias_ten_va_khong_thay(self):
		state = fresh_state()
		state.add("Customer", {"name": "CUST-1", "alias": "COSMETIC", "customer_name": "Cosmetic JSC"})
		self.assertEqual(_common.resolve_customer("CUST-1"), "CUST-1")
		self.assertEqual(_common.resolve_customer("COSMETIC"), "CUST-1")
		self.assertEqual(_common.resolve_customer("Cosmetic JSC"), "CUST-1")
		self.assertIsNone(_common.resolve_customer("KHONG-CO"))
		self.assertIsNone(_common.resolve_customer(None))

	def test_loi_db_thi_tra_none(self):
		fresh_state()
		original = _common.frappe.db.exists

		def boom(*args, **kwargs):
			raise RuntimeError("db down")

		_common.frappe.db.exists = boom
		try:
			self.assertIsNone(_common.resolve_customer("CUST-1"))
		finally:
			_common.frappe.db.exists = original


class TestLineClassification(unittest.TestCase):
	def test_is_cylinder_line(self):
		self.assertTrue(order._is_cylinder_line("TRUC-IN", "Trục in (2 cây)"))
		self.assertTrue(order._is_cylinder_line("X-TRUC-1", "Bất kỳ"))
		self.assertTrue(order._is_cylinder_line("TP-001", "Trục in kèm"))
		self.assertTrue(order._is_cylinder_line("TP-001", "TRUC in"))
		self.assertFalse(order._is_cylinder_line("TP-001", "Túi đựng nước giặt BABA"))
		self.assertFalse(order._is_cylinder_line(None, None))

	def test_order_tab(self):
		self.assertEqual(order._order_tab("NGCS-00001", "Túi phôi"), "ngcs")
		self.assertEqual(order._order_tab("TP-001", "Túi NGCS in sẵn"), "ngcs")
		self.assertEqual(order._order_tab("TMD-00001", "Túi nilon"), "mua_ngoai")
		self.assertEqual(order._order_tab("TP-001", "Màng đơn PE"), "mua_ngoai")
		self.assertEqual(order._order_tab("TP-00001", "Túi đựng nước giặt"), "xuong_sx")
		self.assertEqual(order._order_tab(None, None), "xuong_sx")

	def test_order_product_group_theo_du_lieu_that(self):
		self.assertEqual(
			order._item_product_group("TP-00001", "Túi đựng nước giặt 888 3.2Kg"), "Túi màng ghép"
		)
		self.assertEqual(
			order._item_product_group("BTP-00001", "Cuộn màng ghép PET/PA/PE 3 lớp"), "Cuộn màng ghép"
		)
		self.assertEqual(
			order._item_product_group("NGCS-00001", "Túi phôi nước giặt in sẵn nhỏ 2L"), "Túi NGCS"
		)
		# KNOWN: TMD hiện chưa khớp nhánh nào (tên "Túi nilon HD..." + code đã upper) → rơi về mặc định.
		# Giữ nguyên hành vi cũ; sửa phân loại TMD là việc riêng cần Sếp chốt.
		self.assertEqual(order._item_product_group("TMD-00001", "Túi nilon HD quai thỏ"), "Túi màng ghép")

	def test_order_tab_of_group(self):
		self.assertEqual(order._order_tab_of_group("Túi NGCS"), "ngcs")
		self.assertEqual(order._order_tab_of_group("Túi màng đơn"), "mua_ngoai")
		self.assertEqual(order._order_tab_of_group("Cuộn màng ghép"), "xuong_sx")
		self.assertEqual(order._order_tab_of_group(None), "xuong_sx")


class TestCylinderSpec(unittest.TestCase):
	def test_pending_khi_chua_co_gia(self):
		state = order._cylinder_spec_state({"qty": 2, "supplier": " Kiến Tâm "})
		self.assertEqual(state["qty"], 2)
		self.assertEqual(state["unit_price"], 0.0)
		self.assertEqual(state["supplier"], "Kiến Tâm")
		self.assertTrue(state["pending"])

	def test_co_gia_thi_khong_pending(self):
		state = order._cylinder_spec_state({"cylinder_count": 3, "unit_price": "500000"})
		self.assertEqual(state["qty"], 3)
		self.assertEqual(state["unit_price"], 500000.0)
		self.assertFalse(state["pending"])

	def test_spec_rong(self):
		state = order._cylinder_spec_state(None)
		self.assertEqual((state["qty"], state["pending"]), (0, False))
		self.assertEqual(order._cylinder_item_name(2, ""), "Trục in (2 cây, NCC —)")
		self.assertIn("Kiến Tâm", order._cylinder_item_name(2, "Kiến Tâm"))


class TestDepositPctMap(unittest.TestCase):
	def test_gom_2_query_va_fallback_co_log(self):
		state = fresh_state()
		state.add("Customer", {"name": "CUST-1", "payment_terms": "Cọc 50-50"})
		state.add("Customer", {"name": "CUST-2", "payment_terms": None})
		state.add("Payment Terms Template Detail", {"parent": "Cọc 50-50", "invoice_portion": 50.0})

		pcts = order._deposit_pct_map(["CUST-1", "CUST-2", "CUST-1", None])

		self.assertEqual(pcts, {"CUST-1": 0.5, "CUST-2": 0.5})
		by_doctype = {}
		for call in state.calls:
			if call[0] == "get_list":
				by_doctype[call[1]] = by_doctype.get(call[1], 0) + 1
		# chống N+1: 1 query Customer + 1 query template cho cả 2 KH
		self.assertEqual(by_doctype.get("Customer"), 1)
		self.assertEqual(by_doctype.get("Payment Terms Template Detail"), 1)
		# batch Single: đúng 1 lần đọc Van Phat Settings cho cả map
		single_calls = [c for c in state.calls if c[0] == "get_single_value"]
		self.assertEqual(len(single_calls), 1)
		# ADR-002: fallback 50% phải được ghi log
		self.assertTrue(any(level == "warning" for level, _ in state.logs))

	def test_template_portion_0_thi_fallback(self):
		state = fresh_state()
		state.add("Customer", {"name": "CUST-1", "payment_terms": "Cọc 0"})
		state.add("Payment Terms Template Detail", {"parent": "Cọc 0", "invoice_portion": 0.0})
		self.assertEqual(order._deposit_pct_map(["CUST-1"]), {"CUST-1": 0.5})

	def test_default_doc_tu_single_desk(self):
		state = fresh_state()
		state.set_single("Van Phat Settings", "default_deposit_pct", 30.0)
		state.add("Customer", {"name": "CUST-9"})
		self.assertEqual(order._deposit_pct_map(["CUST-9"]), {"CUST-9": 0.3})
		self.assertEqual(order._get_deposit_pct("CUST-9"), 0.3)

	def test_single_thieu_thi_throw_chu_khong_so_cung(self):
		from frappe_stub import FrappeThrow

		state = fresh_state()
		state.set_single("Van Phat Settings", "default_deposit_pct", None)
		state.add("Customer", {"name": "CUST-9"})
		with self.assertRaises(FrappeThrow) as ctx:
			order._deposit_pct_map(["CUST-9"])
		self.assertIn("Van Phat Settings", str(ctx.exception))

	def test_single_validate_0_am_vuot_100_rong(self):
		from frappe_stub import FrappeThrow

		for bad in (0, -5, 101, "", None):
			state = fresh_state()
			state.set_single("Van Phat Settings", "default_deposit_pct", bad)
			state.add("Customer", {"name": "CUST-9"})
			with self.assertRaises(FrappeThrow, msg="pct={!r}".format(bad)):
				order._default_deposit_pct()

	def test_map_truyen_default_tai_dung_khong_doc_single(self):
		state = fresh_state()
		state.add("Customer", {"name": "CUST-9"})
		pcts = order._deposit_pct_map(["CUST-9"], 0.3)
		self.assertEqual(pcts, {"CUST-9": 0.3})
		self.assertEqual([c for c in state.calls if c[0] == "get_single_value"], [])

	def test_map_rong_khong_doc_single(self):
		state = fresh_state()
		state.set_single("Van Phat Settings", "default_deposit_pct", None)
		self.assertEqual(order._deposit_pct_map([]), {})
		self.assertEqual(order._deposit_pct_map([None]), {})


class TestOrderLifecycle(unittest.TestCase):
	def _doc(self, **overrides):
		doc = {
			"doctype": "Sales Order",
			"name": "SO-1",
			"customer": "CUST-1",
			"docstatus": 0,
			"net_total": 2000000.0,
			"total_taxes_and_charges": 160000.0,
			"grand_total": 2160000.0,
			"advance_paid": 0.0,
			"items": [
				{"item_code": "TP-001", "item_name": "Túi BABA", "qty": 100, "amount": 1000000.0},
				{"item_code": "TRUC-IN", "item_name": "Trục in (2 cây)", "qty": 2, "amount": 1000000.0},
			],
		}
		doc.update(overrides)
		return FakeDoc(doc)

	def _state(self):
		state = fresh_state()
		state.add("Customer", {"name": "CUST-1", "payment_terms": "Cọc 50-50"})
		state.add("Payment Terms Template Detail", {"parent": "Cọc 50-50", "invoice_portion": 50.0})
		state.add("Customer Credit Limit", {"parent": "CUST-1", "credit_limit": 0.0})
		return state

	def test_tien_va_trang_thai_don_nhap_chua_coc(self):
		self._state()
		life = order._order_lifecycle(self._doc())
		self.assertEqual(life["net_total"], 2000000.0)
		self.assertEqual(life["vat_rate"], 8.0)
		self.assertEqual(life["product_total"], 1000000.0)
		self.assertEqual(life["cylinder_total"], 1000000.0)
		self.assertEqual(life["product_qty"], 100)
		self.assertEqual(life["required_deposit"], 1500000.0)
		self.assertEqual(life["payment_type"], "Trả trước")
		self.assertEqual(life["order_state"], "Chờ cọc")
		self.assertFalse(life["can_submit"])
		self.assertFalse(life["is_hold"])

	def test_du_coc_thi_cho_kich_hoat(self):
		self._state()
		life = order._order_lifecycle(self._doc(advance_paid=1500000.0))
		self.assertEqual(life["order_state"], "Đủ cọc (Chờ kích hoạt)")
		self.assertTrue(life["can_submit"])
		self.assertEqual(life["outstanding_amount"], 660000.0)

	def test_coc_mot_phan_thi_hold(self):
		self._state()
		life = order._order_lifecycle(self._doc(advance_paid=500000.0))
		self.assertTrue(life["is_hold"])
		self.assertFalse(life["can_submit"])
		self.assertEqual(life["order_state"], "HOLD (Thiếu cọc)")

	def test_tra_sau_thi_can_submit_ngay(self):
		state = self._state()
		state.rows["Customer Credit Limit"] = [{"parent": "CUST-1", "credit_limit": 50000000.0}]
		life = order._order_lifecycle(self._doc())
		self.assertEqual(life["payment_type"], "Trả sau")
		self.assertTrue(life["can_submit"])
		self.assertEqual(life["order_state"], "Chờ kích hoạt (Trả sau)")


class TestOrderStatusHelpers(unittest.TestCase):
	def test_required_deposit_tra_sau_bang_0(self):
		self.assertEqual(order._required_deposit("Trả sau", 1000000.0, 0.5, 200000.0), 0.0)

	def test_required_deposit_tra_truoc(self):
		self.assertEqual(
			order._required_deposit("Trả trước", 1000000.0, 0.5, 200000.0), 700000.0
		)

	def test_list_status_hold_chi_khi_thieu_coc_mot_phan(self):
		st = order._order_status(0, "Trả trước", 500000.0, 1500000.0)
		self.assertEqual(
			(st["label"], st["css_class"], st["is_hold"], st["can_submit"]),
			("HOLD", "status-hold", True, False),
		)
		self.assertEqual(st["state"], "HOLD (Thiếu cọc)")

	def test_list_status_tra_sau_bao_gio_cung_khong_hold(self):
		st = order._order_status(0, "Trả sau", 0.0, 0.0)
		self.assertEqual(
			(st["label"], st["css_class"], st["is_hold"], st["can_submit"]),
			("Đã duyệt", "status-ordered", False, True),
		)
		self.assertEqual(st["state"], "Chờ kích hoạt (Trả sau)")

	def test_list_status_da_duyet_giu_nguyen(self):
		st = order._order_status(1, "Trả trước", 500000.0, 1500000.0)
		self.assertEqual((st["label"], st["css_class"], st["is_hold"]), ("Đã duyệt", "status-ordered", False))

	def test_submitted_thieu_coc_khong_hold_state_truthful(self):
		# submitted qua duyệt HOLD ngoại lệ nhưng vẫn thiếu cọc: không HOLD nữa,
		# state truthful "Chính thức (Trả trước)", không submit lại.
		for advance, state in ((500000.0, "Chính thức (Trả trước)"), (0.0, "Chính thức (Trả trước)")):
			st = order._order_status(1, "Trả trước", advance, 1500000.0)
			self.assertEqual(st["label"], "Đã duyệt")
			self.assertEqual(st["state"], state)
			self.assertFalse(st["is_hold"])
			self.assertFalse(st["can_submit"])

	def test_submitted_du_coc_state_khong_cung_so(self):
		# Single cấu hình được → state generic, không cứng ">=50%".
		st = order._order_status(1, "Trả trước", 1500000.0, 1500000.0)
		self.assertEqual(st["state"], "Chính thức (Đã đủ cọc)")
		self.assertNotIn("50", st["state"])

	def test_detail_va_list_cung_mot_model(self):
		# product_total 3.000.000 x 50% = required 1.500.000 (không trục).
		cases = [
			(0.0, 1500000.0, "Chờ cọc", False, False),
			(500000.0, 1500000.0, "HOLD (Thiếu cọc)", True, False),
			(1500000.0, 1500000.0, "Đủ cọc (Chờ kích hoạt)", False, True),
		]
		for advance, required, state, is_hold, can_submit in cases:
			st = order._order_status(0, "Trả trước", advance, required)
			self._lifecycle_state()
			life = order._order_lifecycle(self._doc_for_status(advance))
			self.assertEqual((st["state"], st["is_hold"], st["can_submit"]), (state, is_hold, can_submit))
			self.assertEqual(
				(life["order_state"], life["is_hold"], life["can_submit"]),
				(state, is_hold, can_submit),
			)
			self.assertEqual(life["required_deposit"], required)

	def _lifecycle_state(self):
		state = fresh_state()
		state.add("Customer", {"name": "CUST-1", "payment_terms": "Cọc 50-50"})
		state.add("Payment Terms Template Detail", {"parent": "Cọc 50-50", "invoice_portion": 50.0})
		state.add("Customer Credit Limit", {"parent": "CUST-1", "credit_limit": 0.0})
		return state

	def _doc_for_status(self, advance):
		from frappe_stub import FakeDoc

		return FakeDoc({
			"doctype": "Sales Order",
			"name": "SO-1",
			"customer": "CUST-1",
			"docstatus": 0,
			"net_total": 3000000.0,
			"total_taxes_and_charges": 0.0,
			"grand_total": 3000000.0,
			"advance_paid": advance,
			"items": [
				{"item_code": "TP-001", "item_name": "Túi", "qty": 100, "amount": 3000000.0},
			],
		})


if __name__ == "__main__":
	unittest.main()
