"""Regression SPEC auth 2 mode (Sếp duyệt 2026-09-16):
- Prod bắt login bằng ID (username/email/SĐT) + mật khẩu.
- Local build mode (Vite dev) không cần login.
Slice 1: login.html chấp nhận ID — placeholder + message không gắn SĐT.
"""

import os
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def read(rel):
	with open(os.path.join(REPO, rel), encoding="utf-8") as f:
		return f.read()


class TestLoginAcceptsId(unittest.TestCase):
	def test_login_placeholder_accepts_id(self):
		src = read("apps/vanphat_portal/vanphat_portal/www/login.html")
		self.assertNotIn("Nhập số điện thoại", src,
			"placeholder không được gắn riêng SĐT — prod login bằng ID")
		self.assertIn("usr", src, "form vẫn POST usr như ERP native")

	def test_login_empty_message_mentions_id(self):
		src = read("apps/vanphat_portal/vanphat_portal/www/login.html")
		self.assertNotIn("số điện thoại và mật khẩu", src,
			"message trống phải nói ID, không riêng SĐT")


if __name__ == "__main__":
	unittest.main()
