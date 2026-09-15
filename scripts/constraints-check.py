#!/usr/bin/env python3
"""Máy kiểm ràng buộc (CONSTRAINTS.md) — chạy được không cần bench, không cần mạng.

Hai tầng:
  floor   — luật cấm, phải bằng 0 NGAY HÔM NAY. Vi phạm = exit 1.
  ratchet — số đo hiện tại, chỉ được đi theo hướng tốt hơn baseline.
            Đây là cách áp số khi codebase chưa đạt đích (không tạo build đỏ vĩnh viễn).

Dùng:
  python3 scripts/constraints-check.py            # floor + ratchet (mặc định)
  python3 scripts/constraints-check.py floor      # chỉ floor, <2s, dùng cho pre-commit
  python3 scripts/constraints-check.py --init     # ghi lại baseline = số đo hiện tại
"""

from __future__ import annotations

import gzip
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FE = ROOT / "apps/vanphat_portal/frontend/src"
API = ROOT / "apps/vanphat_portal/vanphat_portal/api"
SCRIPTS = ROOT / "scripts"
ASSETS = ROOT / "apps/vanphat_portal/vanphat_portal/public/frontend/assets"
BASELINE = ROOT / ".constraints-baseline.json"

FE_GLOBS = ("*.vue", "*.js")
API_GLOBS = ("*.py",)
SCRIPT_GLOBS = ("*.mjs", "*.js")

# Endpoint cố ý không gated — mỗi dòng phải kèm lý do, người duyệt đọc được.
GATE_ALLOWLIST = {
    ("bao_gia.py", "get_boot"): "chỉ trả session user + csrf token cho chính người đang đăng nhập",
}

MONEY_FIELDS = (
    "grand_total",
    "net_total",
    "product_total",
    "vat_amount",
    "required_deposit",
    "advance_paid",
    "outstanding_amount",
)


def files(globs_by_dir: dict[Path, tuple[str, ...]]) -> list[Path]:
    out: list[Path] = []
    for base, patterns in globs_by_dir.items():
        for pattern in patterns:
            out.extend(sorted(base.rglob(pattern)))
    return [p for p in out if p.is_file()]


def scan(paths: list[Path], pattern: str) -> list[str]:
    rx = re.compile(pattern)
    hits: list[str] = []
    for path in paths:
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for number, line in enumerate(text.splitlines(), start=1):
            if rx.search(line):
                hits.append(f"{path.relative_to(ROOT)}:{number}")
    return hits


# ---------------------------------------------------------------- floor rules
# (id, mô tả, globs, regex). Phải bằng 0 hôm nay, nếu không phải sửa code.
# raw_fetch: api() trong useSession.js là implementation của đường fetch duy nhất.
FLOOR_EXCLUDE = {
    "raw_fetch": ("apps/vanphat_portal/frontend/src/composables/useSession.js",),
}
FLOOR_RULES = [
    ("mock_random_id", "Math.random() làm ID tài liệu", FE_GLOBS, r"Math\.random\s*\("),
    ("guest_api", "allow_guest=True trên dữ liệu nội bộ", API_GLOBS, r"allow_guest\s*=\s*True"),
    ("permissioned_get_all", "frappe.get_all trên dữ liệu có phân quyền", API_GLOBS, r"frappe\.get_all\s*\("),
    ("raw_html", "v-html trong template", FE_GLOBS, r"\bv-html\b"),
    (
        "suppression",
        "comment tắt máy kiểm (@ts-ignore/eslint-disable/noqa...)",
        FE_GLOBS + API_GLOBS,
        r"@ts-(ignore|nocheck|expect-error)|eslint-disable|\bnoqa\b|type:\s*ignore|istanbul ignore|Stryker disable|nosemgrep|gitleaks:allow",
    ),
    (
        "secret",
        "khoá/bí mật nằm trong source",
        FE_GLOBS + API_GLOBS,
        r"BEGIN (RSA|OPENSSH|EC|PGP) PRIVATE KEY|(api_secret|password|token)\s*=\s*[\"'][A-Za-z0-9/+_-]{16,}[\"']",
    ),
    ("stub", "hàm chưa làm (NotImplementedError/TODO trong API)", API_GLOBS, r"NotImplementedError|\bTODO\b|\bFIXME\b"),
    # Quy định Sếp 2026-09-15: cấm mock server/CSRF/API/local-JSON preview.
    # Browser test chỉ vs staging bench (real API + real CSRF + TEST- docs + cleanup).
    # Quét cả scripts/ vì mock cũ sống ở đó (serve-portal.mjs đã xóa).
    (
        "mock_server",
        "mock server/CSRF/API/local-JSON preview (serve-portal đã xóa)",
        SCRIPT_GLOBS,
        r"mock_csrf_token|local_quotations|local_orders|serve-portal|MASTER_ITEMS\.length",
    ),
    # Triple rule ghim 2026-09-15 (backend native + config native + visual custom):
    # mọi HTTP qua api() duy nhất; không identity/config hardcode mới trong Vue.
    ("raw_fetch", "fetch() trực tiếp trong src (phải qua api())", FE_GLOBS, r"(?<![\w$.])fetch\s*\("),
    (
        "hardcoded_user",
        "email/user hardcode trong client",
        FE_GLOBS,
        r"['\"][A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}['\"]",
    ),
    (
        "hardcoded_config",
        "option/default/label hardcode mới trong Vue (config phải từ native)",
        FE_GLOBS,
        r"<option\s+value=\"[^\"]+\"(?![^>]*v-for)|qty:\s*[0-9]{3,}|materials:\s*\[\s*['\"]",
    ),
]

# -------------------------------------------------------------- ratchet rules
# (id, mô tả, globs, regex, hướng). "down" = càng thấp càng tốt.
RATCHET_RULES = [
    (
        "client_identity",
        "danh tính user hardcode trong client",
        FE_GLOBS,
        r"[\w.+-]+@[\w-]+\.[\w.]{2,}",
        "down",
    ),
    (
        "client_money_math",
        "client tự nhân/chia trên field tiền",
        FE_GLOBS,
        r"(" + "|".join(MONEY_FIELDS) + r")\s*[*/]|[*/]\s*(" + "|".join(MONEY_FIELDS) + r")",
        "down",
    ),
    ("client_qty_reduce", "client tự cộng qty (.reduce)", FE_GLOBS, r"\.reduce\s*\(", "down"),
    ("client_magic_fallback", "fallback số thương mại cứng (|| 5000)", FE_GLOBS, r"[|?]{2}\s*[0-9]{3,}", "down"),
    ("client_hardcoded_qty", "qty mặc định cứng trong client", FE_GLOBS, r"qty:\s*[0-9]{3,}", "down"),
    (
        "swallowed_catch",
        "catch rỗng / chỉ comment (lỗi bị nuốt)",
        FE_GLOBS,
        r"catch\s*(\([^)]*\))?\s*\{\s*(//[^\n]*)?\s*\}",
        "down",
    ),
]


def api_permission_ledger() -> tuple[int, list[str]]:
    """Đếm endpoint @frappe.whitelist() không có cổng quyền nào.

    Cổng quyền = gọi trực tiếp has_permission/get_roles/... trong thân hàm,
    HOẶC gọi helper nhà mình trong `_guards` (require_doc/require_roles —
    2 hàm này bọc has_permission/get_roles native, Sếp chốt 2026-09-15).
    Hàm không whitelist (như clear_catalog_cache nội bộ) không tính endpoint.
    """
    gate = re.compile(
        r"has_permission|only_for|require_roles|require_doc|check_permission|get_roles|"
        r"session\.user\s*(==|!=)|has_role|frappe\.permissions"
    )
    total = 0
    ungated: list[str] = []
    for path in sorted(API.rglob("*.py")):
        if path.name == "_guards.py":
            continue
        lines = path.read_text(encoding="utf-8").splitlines()
        for number, line in enumerate(lines):
            if "frappe.whitelist" not in line:
                continue
            total += 1
            # thân hàm: từ decorator tới def kế tiếp cùng cấp (thụt lề 0) hoặc hết file
            body: list[str] = []
            for follow in lines[number + 1 :]:
                if follow.startswith(("def ", "@", "class ")) and body:
                    break
                body.append(follow)
            if not gate.search("\n".join(body)):
                name = next((l for l in lines[number + 1 :] if l.startswith("def ")), "?")
                func = name.strip().removeprefix("def ").split("(")[0]
                if (path.name, func) in GATE_ALLOWLIST:
                    continue
                ungated.append(f"{path.relative_to(ROOT)}:{number + 1} {name.strip()}")
    return total, ungated


def static_size() -> tuple[str, int]:
    """Entry JS lớn nhất (gzip, KB) — đo trên dist tĩnh, không cần staging."""
    if not ASSETS.is_dir():
        return ("n/a", 0)
    entries = sorted(ASSETS.glob("index-*.js"))
    if not entries:
        return ("n/a", 0)
    biggest = max(entries, key=lambda p: p.stat().st_size)
    # compresslevel 6 = mặc định của `gzip` CLI, để khớp scripts/budget-gate.sh
    kb = len(gzip.compress(biggest.read_bytes(), compresslevel=6, mtime=0)) // 1024
    return (biggest.name, kb)


def python_tests() -> int:
    proc = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "apps/vanphat_portal/tests", "-p", "test_*.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    match = re.search(r"Ran (\d+) tests?", proc.stderr + proc.stdout)
    return int(match.group(1)) if match else 0


def frontend_guard() -> int:
    """Guard composable frontend: import + khởi tạo mọi composable trong Node.

    Bắt lớp lỗi mà `vite build` không thấy (biến chưa định nghĩa trong composable).
    """
    frontend = ROOT / "apps/vanphat_portal/frontend"
    if not (frontend / "check-composables.mjs").is_file():
        return 0
    try:
        proc = subprocess.run(
            ["node", "check-composables.mjs"], cwd=frontend, capture_output=True, text=True, timeout=300
        )
    except (OSError, subprocess.TimeoutExpired):
        return 0
    return 1 if proc.returncode == 0 else 0


def measure(full: bool) -> tuple[dict[str, int], list[str], list[str]]:
    fe_paths = files({FE: FE_GLOBS})
    api_paths = files({API: API_GLOBS})
    script_paths = files({SCRIPTS: SCRIPT_GLOBS})
    all_paths = fe_paths + api_paths

    floor_failures: list[str] = []
    for rule_id, desc, globs, pattern in FLOOR_RULES:
        if globs == FE_GLOBS + API_GLOBS:
            targets = all_paths
        elif globs == API_GLOBS:
            targets = api_paths
        elif globs == SCRIPT_GLOBS:
            targets = script_paths
        else:
            targets = fe_paths
        hits = scan(targets, pattern)
        for excluded in FLOOR_EXCLUDE.get(rule_id, ()):
            hits = [hit for hit in hits if not hit.startswith(excluded + ":")]
        if hits:
            floor_failures.append(f"[{rule_id}] {desc}: {len(hits)} chỗ -> {', '.join(hits[:5])}")

    numbers: dict[str, int] = {}
    for rule_id, _desc, globs, pattern, _direction in RATCHET_RULES:
        targets = api_paths if globs == API_GLOBS else fe_paths
        numbers[rule_id] = len(scan(targets, pattern))

    total, ungated = api_permission_ledger()
    numbers["api_endpoints"] = total
    numbers["api_ungated"] = len(ungated)

    _name, kb = static_size()
    numbers["entry_gzip_kb"] = kb

    numbers["fe_test_files"] = len(
        [p for p in fe_paths if p.name.endswith((".test.js", ".spec.js", ".test.ts", ".spec.ts"))]
    )
    if full:
        numbers["py_tests"] = python_tests()
        numbers["fe_guard_ok"] = frontend_guard()

    return numbers, floor_failures, ungated


def main() -> int:
    args = sys.argv[1:]
    mode = args[0] if args else "all"
    full = mode != "floor"

    numbers, floor_failures, ungated = measure(full=full)

    if full:
        for rule_id, desc, _g, pattern, _d in RATCHET_RULES:
            if numbers.get(rule_id):
                print(f"  · {rule_id}: {numbers[rule_id]}  ({desc})")
    else:
        print("(chế độ floor: bỏ qua ratchet để chạy nhanh trong pre-commit)")

    if mode == "--init":
        BASELINE.write_text(json.dumps(numbers, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"baseline ghi vào {BASELINE.relative_to(ROOT)}: {json.dumps(numbers, sort_keys=True)}")
        return 0

    print(f"\n== FLOOR ({len(FLOOR_RULES)} luật) ==")
    if floor_failures:
        for line in floor_failures:
            print(f"[FAIL] {line}")
    else:
        print("[ok] tất cả luật cấm đều bằng 0")

    regressions: list[str] = []
    if mode != "floor":
        print("\n== RATCHET (không được xấu đi) ==")
        baseline = json.loads(BASELINE.read_text(encoding="utf-8")) if BASELINE.is_file() else {}
        if not baseline:
            print("[warn] chưa có baseline — chạy: python3 scripts/constraints-check.py --init")
        for rule_id, desc, _g, _p, direction in RATCHET_RULES + [
            ("api_ungated", "endpoint chưa có cổng quyền", None, None, "down"),
            ("entry_gzip_kb", "entry JS gzip (KB)", None, None, "down"),
            ("fe_test_files", "file test frontend", None, None, "up"),
            ("fe_guard_ok", "guard composable frontend xanh", None, None, "up"),
            ("py_tests", "test backend xanh", None, None, "up"),
        ]:
            now = numbers.get(rule_id, 0)
            was = baseline.get(rule_id, now)
            if direction == "down" and now > was:
                regressions.append(f"[{rule_id}] {desc}: {was} -> {now} (xấu đi)")
            if direction == "up" and now < was:
                regressions.append(f"[{rule_id}] {desc}: {was} -> {now} (tụt)")
            marker = "=" if now == was else ("+" if now > was else "-")
            print(f"  {marker} {rule_id}: {now} (baseline {was}) — {desc}")
        if ungated:
            print(f"\n  endpoint chưa gated ({len(ungated)}):")
            for line in ungated:
                print(f"    - {line}")

    if floor_failures or regressions:
        print("\nGATE: FAIL")
        for line in regressions:
            print(f"[FAIL] {line}")
        return 1
    print("\nGATE: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
