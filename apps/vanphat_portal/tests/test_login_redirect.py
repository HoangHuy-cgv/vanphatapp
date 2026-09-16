"""Regression: login xong phải về /portal, không về /app (Desk nặng gây lag).

Bug 2026-09-15 (Sếp phát hiện thực chiến): login đáp xuống /desk gây lag.
Fix: login.py + login.html default redirect /portal (redirect-to ưu tiên).
Test đọc source (không cần bench): fail nếu còn default /app.
"""

import os
import re
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def read(rel):
	with open(os.path.join(REPO, rel), encoding="utf-8") as f:
		return f.read()


class TestLoginRedirect(unittest.TestCase):
	def test_login_py_default_portal(self):
		src = read("apps/vanphat_portal/vanphat_portal/www/login.py")
		self.assertIn('"/portal"', src, "login.py phải default /portal")
		self.assertNotIn('"/app"', src, "login.py không còn default /app")

	def test_login_html_default_portal(self):
		src = read("apps/vanphat_portal/vanphat_portal/www/login.html")
		# Allowlist redirect-to kín traversal: chỉ /portal hoặc /portal/...,
		# reject .. và backslash — còn lại → /portal.
		self.assertIn('startsWith("/portal/")', src, "login.html phải allowlist /portal/")
		self.assertIn('".."', src, "login.html phải reject traversal ..")
		self.assertIn('"/portal"', src, "login.html fallback phải là /portal")

	def test_no_desk_default_redirect(self):
		for rel in (
			"apps/vanphat_portal/vanphat_portal/www/login.py",
			"apps/vanphat_portal/vanphat_portal/www/login.html",
			"apps/vanphat_portal/frontend/src/composables/useSession.js",
		):
			src = read(rel)
			self.assertNotIn('"/app"', src, f"{rel} không default /app")
			self.assertNotIn("'/app'", src, f"{rel} không default /app")


if __name__ == "__main__":
	unittest.main()
