"""Regression: CD path-filter phải coi www/*.py là backend + restart backend.

Bug 2026-09-16 (thực chiến): CD xếp www/portal.py là frontend-only → skip
migrate + chỉ nginx reload → gunicorn không nạp portal.py mới → Guest vẫn lọt
/portal dù code đã sync. Phải restart backend mới hết (đã restart tay).
Fix cd.yml 3-tier:
- MIGRATE (bench migrate): api/ + patches/ + hooks.py (chạm DocType/schema).
- RESTART backend (gunicorn nạp lại www/*.py): www/*.py.
- FRONTEND-ONLY (nginx reload): còn lại (html/assets/src...).
Test đọc cd.yml (không cần VPS): fail nếu thiếu tier restart www.
"""

import os
import re
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def read(rel):
	with open(os.path.join(REPO, rel), encoding="utf-8") as f:
		return f.read()


class TestCdWwwRestart(unittest.TestCase):
	def test_cd_has_www_py_restart_tier(self):
		src = read(".github/workflows/cd.yml")
		self.assertIn("www/", src, "cd.yml phải nhắc www/ (tier restart backend)")
		self.assertIn("restart backend", src.lower(), "cd.yml phải có bước restart backend")

	def test_cd_www_py_pattern(self):
		src = read(".github/workflows/cd.yml")
		m = re.search(r"www/[^']*py", src)
		self.assertIsNotNone(m, "cd.yml phải có pattern www/*.py riêng (không gộp frontend-only)")

	def test_cd_safe_default_non_git(self):
		# /opt/vanphat không phải git repo (git archive sync) → CHANGED rỗng
		# → mặc định an toàn migrate + restart, || true để set -e không kill.
		src = read(".github/workflows/cd.yml")
		self.assertIn("|| true", src, "CHANGED phải có || true (non-git repo)")
		self.assertIn('Non-git sync dir', src, "phải có nhánh default-safe migrate + restart")

	def test_cd_backend_poll_fails_loud(self):
		# Poll frappe.ping phải exit 1 rõ khi backend không hồi (không đi tiếp).
		src = read(".github/workflows/cd.yml")
		self.assertIn("BACKEND_UP", src, "phải track trạng thái backend sau restart")
		self.assertIn("did not recover", src, "phải fail rõ khi backend không hồi")

	def test_cd_keeps_migrate_for_api(self):
		src = read(".github/workflows/cd.yml")
		self.assertIn("migrate", src, "cd.yml vẫn giữ bench migrate cho api/DocType")


if __name__ == "__main__":
	unittest.main()
