"""Regression SPEC auth 2 mode slice 2 (Sếp duyệt 2026-09-16):
Local build mode (Vite dev 8090) vào thẳng /portal không cần login —
dev agent/Sếp tiện. Prod giữ nguyên chặn Guest (portal.py).
Cơ chế Vite-side only: plugin dev trong vite.config.js (không đụng code prod).
"""

import os
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def read(rel):
	with open(os.path.join(REPO, rel), encoding="utf-8") as f:
		return f.read()


class TestLocalBuildMode(unittest.TestCase):
	def test_vite_dev_has_build_mode_bypass(self):
		src = read("apps/vanphat_portal/frontend/vite.config.js")
		self.assertIn("build-mode", src.lower() + "build_mode" if False else src,
			"vite.config.js dev phải có build-mode bypass (local không login)")

	def test_prod_portal_still_blocks_guest(self):
		src = read("apps/vanphat_portal/vanphat_portal/www/portal.py")
		self.assertIn("Guest", src, "prod portal.py vẫn chặn Guest")
		self.assertIn("/login", src, "prod portal.py vẫn đá về /login")


if __name__ == "__main__":
	unittest.main()
