"""Regression TRIỆT ĐỂ desk redirect (Sếp chốt 2026-09-16: chặn cả 3, về portal hết).

Bug thực chiến: ẩn danh mở /desk → login?redirect-to=/desk → login xong về
/desk (Frappe nặng, lag). Browser-test repro: AFTER LOGIN via /desk → /desk.
Root cause: login.py + login.html ưu tiên redirect-to mù quáng (nhận /desk).

Fix:
1. login.py: redirect-to chỉ nhận path nội bộ portal (/portal...), còn lại → /portal.
2. login.html JS: cùng allowlist phía client.
3. Gốc / (home): về /portal (không kẹt ở login không redirect).
Test đọc source (không cần bench): fail nếu còn redirect mù.
"""

import os
import re
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def read(rel):
	with open(os.path.join(REPO, rel), encoding="utf-8") as f:
		return f.read()


class TestNoDeskRedirect(unittest.TestCase):
	def test_login_py_allowlists_portal(self):
		src = read("apps/vanphat_portal/vanphat_portal/www/login.py")
		self.assertNotIn('"/app"', src, "login.py không đá về /app")
		self.assertNotIn('"/desk"', src, "login.py không đá về /desk")
		self.assertIn("/portal", src, "login.py default /portal")

	def test_login_html_allowlists_portal(self):
		src = read("apps/vanphat_portal/vanphat_portal/www/login.html")
		# JS phải validate redirect-to, không gán mù vào location.
		self.assertNotIn('params.get("redirect-to") || "/portal"', src,
			"login.html không gán redirect-to mù quáng")

	def test_no_bare_desk_app_defaults(self):
		for rel in (
			"apps/vanphat_portal/vanphat_portal/www/login.py",
			"apps/vanphat_portal/vanphat_portal/www/login.html",
			"apps/vanphat_portal/vanphat_portal/www/portal.py",
			"apps/vanphat_portal/frontend/src/composables/useSession.js",
		):
			src = read(rel)
			self.assertNotIn('"/app"', src, f"{rel} không default /app")
			self.assertNotIn("'/app'", src, f"{rel} không default /app")
			self.assertNotIn('"/desk"', src, f"{rel} không default /desk")
			self.assertNotIn("'/desk'", src, f"{rel} không default /desk")


if __name__ == "__main__":
	unittest.main()
