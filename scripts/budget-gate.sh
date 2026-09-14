#!/usr/bin/env bash
# P5 CI gate tối giản (Zero-Node: đo trên dist static, không cần staging).
# AGENTS.md §4: initial JS gzip ≤170KB warn / 300KB fail; async chunk warn 500KB.
set -u
ASSETS="apps/vanphat_portal/vanphat_portal/public/frontend/assets"
FAIL=0
WARN=0
check() {
  f="$1"; limit="$2"; level="$3"; label="$4"
  [ -f "$f" ] || return 0
  size=$(gzip -c "$f" | wc -c)
  kb=$((size / 1024))
  if [ "$kb" -gt "$limit" ]; then
    echo "[$level] $label: ${kb}KB gzip > ${limit}KB — $f"
    if [ "$level" = "FAIL" ]; then FAIL=1; else WARN=1; fi
  else
    echo "[ok] $label: ${kb}KB gzip (≤${limit}KB)"
  fi
}
echo "== initial =="
for f in "$ASSETS"/index-*.js; do check "$f" 300 FAIL "initial"; done
for f in "$ASSETS"/index-*.js; do check "$f" 170 WARN "initial-warn"; done
echo "== async chunks =="
for f in "$ASSETS"/*.js; do
  case "$f" in */index-*.js|*/vendor-*.js) continue;; esac
  check "$f" 500 WARN "chunk"
done
echo "== fonts =="
for f in "$ASSETS"/*.woff2; do
  [ -f "$f" ] || continue
  kb=$(($(stat -c%s "$f") / 1024))
  echo "[info] font: ${kb}KB — $f"
done
if [ "$FAIL" -eq 1 ]; then echo "GATE: FAIL"; exit 1; fi
if [ "$WARN" -eq 1 ]; then echo "GATE: WARN (pass)"; fi
echo "GATE: PASS"
