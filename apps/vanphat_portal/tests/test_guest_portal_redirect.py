"""Regression: Guest vào /portal phải bị đá về /login (không render SPA gây lag).

Bug 2026-09-16 (Sếp phát hiện thực chiến + browser-test xác nhận): Guest mở
https://app.vanphat.io.vn/portal vẫn render shell SPA ("Chưa đăng nhập", boot 403,
API 403) thay vì redirect /login. Nặng trình duyệt yếu → giật lag.
Fix: portal.py chặn Guest (redirect /login?redirect-to=/portal).
Test đọc source (không cần bench): fail nếu portal.py không chặn Guest.
"""

import os
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def read(rel):
	with open(os.path.join(REPO, rel), encoding="utf-8") as f:
		return f.read()


class TestGuestPortalRedirect(unittest.TestCase):
	def test_portal_py_blocks_guest(self):
		src = read("apps/vanphat_portal/vanphat_portal/www/portal.py")
		self.assertIn("Guest", src, "portal.py phải nhắc Guest (chặn khách chưa login)")
		self.assertIn("/login", src, "portal.py phải redirect Guest về /login")

	def test_portal_py_keeps_csrf_for_authed(self):
		src = read("apps/vanphat_portal/vanphat_portal/www/portal.py")
		self.assertIn("csrf_token", src, "portal.py vẫn cấp CSRF cho user đã login")


if __name__ == "__main__":
	unittest.main()
