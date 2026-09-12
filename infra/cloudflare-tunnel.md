# Cloudflare Tunnel — public access without open ports (Sếp locked 2026-09-10)

Run on the VPS alongside compose. `cloudflared` maps a public hostname to
local `http://frontend:8080` (compose binds frontend to 127.0.0.1 only).

## Setup (once, on VPS)

1. `cloudflared tunnel login` (needs a Cloudflare account + domain).
2. `cloudflared tunnel create vanphat-erp`.
3. `cloudflared tunnel route dns vanphat-erp erp.<domain>`.
4. Write `infra/cloudflared-config.yml` (values only, never commit secrets):

```yaml
tunnel: <TUNNEL-ID>
credentials-file: /etc/cloudflared/<TUNNEL-ID>.json
ingress:
  - hostname: erp.<domain>
    service: http://127.0.0.1:8080
  - service: http_status:404
```

5. Run: `cloudflared tunnel --config infra/cloudflared-config.yml run vanphat-erp`
   (or as a systemd service for auto-restart).

## Notes

- Frappe site name must equal the public hostname (`erp.<domain>`); set it at
  `bench new-site` time. The compose `FRAPPE_SITE_NAMER_HEADER: host` keeps
  Host-based site resolution.
- No firewall port needs opening for HTTP. SSH stays key-only on a custom port.
