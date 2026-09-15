"""Seed SO mẫu + đo p95 list_orders trên site thật (chạy local, gọi qua tunnel).

Dùng: ADMIN_PASS=$(ssh ... "sudo cat /opt/vanphat/.admin-pass") python3 scripts/measure_p95.py [--seed N]
- --seed N: tạo N Sales Order mẫu từ Item/KH thật trước khi đo.
- Không --seed: chỉ đo p95 (50 request đọc list_orders page 1).
"""

import json
import os
import statistics
import sys
import time
import urllib.parse
import urllib.request
import http.cookiejar

BASE = "https://app.vanphat.io.vn"
COMPANY = "Công ty TNHH Sản Xuất Bao Bì Vạn Phát"
UA = {"User-Agent": "VPMeasure/1.0", "Accept": "application/json"}


def login(op):
    pw = os.environ["ADMIN_PASS"]
    ldata = urllib.parse.urlencode({"usr": "Administrator", "pwd": pw}).encode()
    req = urllib.request.Request(
        f"{BASE}/api/method/login", data=ldata,
        headers={**UA, "Content-Type": "application/x-www-form-urlencoded"},
    )
    with op.open(req, timeout=30) as r:
        print("login:", r.status)


def rpc(op, method, params=None):
    data = json.dumps(params or {}).encode()
    req = urllib.request.Request(
        f"{BASE}/api/method/{method}", data=data,
        headers={**UA, "Content-Type": "application/json"},
    )
    with op.open(req, timeout=60) as r:
        return json.load(r).get("message")


def seed(op, n):
    items = rpc(op, "vanphat_portal.api.item.get_list", {"page_length": 5})["items"]
    codes = [i["item_code"] for i in items[:3]]
    custs = rpc(op, "vanphat_portal.api.customer.get_list", {"page_length": 20})["customers"]
    cust = [c["name"] for c in custs if c["name"].startswith("C")][:5] or [custs[0]["name"]]
    made = 0
    for i in range(n):
        payload = {
            "customer": cust[i % len(cust)], "company": COMPANY,
            "delivery_date": "2026-10-15",
            "items": [
                {"item_code": codes[0], "item_name": "Seed A",
                 "qty": 1000 + i * 100, "rate": 5000, "uom": "Túi"},
                {"item_code": codes[1], "item_name": "Seed B",
                 "qty": 500, "rate": 8000, "uom": "Túi"},
            ],
        }
        try:
            res = rpc(op, "vanphat_portal.api.order.create_sales_order", {"payload": payload})
            made += 1
            if made <= 2:
                print("made:", res.get("name"))
        except Exception as e:
            print("FAIL:", str(e)[:200])
            break
    print("seeded:", made)


def measure(op):
    for _ in range(3):
        rpc(op, "vanphat_portal.api.order.list_orders", {"page": 1, "page_length": 15})
    ts, first = [], None
    for _ in range(50):
        t0 = time.perf_counter()
        body = rpc(op, "vanphat_portal.api.order.list_orders", {"page": 1, "page_length": 15})
        ts.append((time.perf_counter() - t0) * 1000)
        if first is None:
            first = body
    print("orders total:", (first or {}).get("total_count"),
          "rows:", len((first or {}).get("orders", [])))
    ts.sort()

    def pct(p):
        return ts[min(len(ts) - 1, int(p / 100 * len(ts)))]

    print(f"n=50 min={ts[0]:.0f} p50={pct(50):.0f} p95={pct(95):.0f} "
          f"max={ts[-1]:.0f} mean={statistics.mean(ts):.0f}ms")


def main():
    cj = http.cookiejar.CookieJar()
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    login(op)
    if len(sys.argv) == 3 and sys.argv[1] == "--seed":
        seed(op, int(sys.argv[2]))
    measure(op)


if __name__ == "__main__":
    main()
