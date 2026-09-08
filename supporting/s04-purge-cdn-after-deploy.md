---
id: OEN-S04
title: "Purge the content delivery network after deploy"
kind: supporting
status: active
edition: 1
date_published: 2026-09-08
author: Eugene Armstead
author_url: https://www.armsteadent.com/
canonical: https://eugenearmstead.github.io/overlay-and-edge-notes/supporting/s04-purge-cdn-after-deploy.html
keywords:
  - cdn
  - cache-purge
  - cloudflare
backs:
  - OEN-08
  - OEN-09
  - OEN-10
backed_by: []
description: "After a successful deploy, purge HTML. Workers-edit tokens often lack Cache Purge. Query-string cache busts do not replace a zone purge for HTML."
terms:
  - abbr: OEN
    expansion: Overlay and Edge Notes
  - abbr: SSH
    expansion: Secure Shell
  - abbr: TCP
    expansion: Transmission Control Protocol
  - abbr: ICMP
    expansion: Internet Control Message Protocol
  - abbr: HTTPS
    expansion: Hypertext Transfer Protocol Secure
  - abbr: HTML
    expansion: HyperText Markup Language
  - abbr: API
    expansion: application programming interface
  - abbr: nft
    expansion: nftables (Linux packet filter)
  - abbr: CDN
    expansion: content delivery network
  - abbr: URL
    expansion: Uniform Resource Locator
  - abbr: UI
    expansion: user interface
  - abbr: HIT
    expansion: cache HIT (content still served from cache)
  - abbr: Wrangler
    expansion: Cloudflare Workers command-line tool
  - abbr: Cloudflare
    expansion: content delivery and Workers platform
---

# Purge the content delivery network after deploy

## Context

Known Cloudflare advice. Unique add-ons: a token with Workers edit often **lacks Cache Purge**; `?v=` does not replace zone purge for HTML. Backs [OEN-08](../web/08-worker-html-localhost-debug.md), [OEN-09](../web/09-git-merge-is-not-a-live-worker.md), [OEN-10](../web/10-one-blocking-stylesheet-variable-fonts.md).

## Topology

```text
[deploy] --> origin new
[CDN] HTML still old until zone purge
Workers-edit token often LACKS Cache Purge
?v= does not replace HTML purge
```

## Bind

Fill this table **before** any live change. Do **not** paste real values back into public notes.

| Placeholder | Operator fills | Class |
|-------------|----------------|-------|
| `<worker-root>` | Worker / UI source tree | Directory on the workstation |
| `<live-url>` | Public HTTPS origin | URL the browser loads |
| `<preview-url>` | Preview origin if used | URL |
| `<html-path>` | Path that becomes a Response body | File glob |


## Formulas

```text
# Predeploy MUST fail the ship on client-executed matches:
#   127.0.0.1:7450   localhost:7450   /ingest/   X-Debug-Session-Id
# Merge ≠ live Worker. Wait ~10 minutes, then Wrangler if the Git build never started.
# Cache: Workers-edit tokens often lack Cache Purge. ?v= does not replace zone purge for HTML.
```

## Method

Purge the HTML URL (and preview URL if tunneled). If the deploy token cannot purge, say so. Prefer origin `CDN-Cache-Control: no-store` on HTML.

## Consequences

Visitors see the new HTML. Operators are not told the CDN is “haunted.”

## Agent stop rule

> A coding agent MUST emit a **bound runbook** (placeholders replaced from Bind).
> MUST NOT apply live `ip rule`, nft, iptables, ip6tables, sysctl, `wg set`, daemon restart, or deploy until a **human** filled Bind.
> MUST NOT claim a fix on ICMP ping alone when Verify names TCP, SSH, or HTTPS.
> MUST NOT file an upstream bug from this page.
> MUST NOT publish real addresses, hostnames, or custom ports.

## Procedure

Placeholders only until Bind is filled: `<cloud-vps>`, `<lan-pi>`, `<overlay-peer>`, `<exit-node>`, `<wg-iface>`, `<gcp-nic>`, plus the Bind extras on this page.

### Copy-paste commands (after Bind)

```bash
curl -sS -D- -o /dev/null --max-time 15 <live-url> | tr -d '\r' | grep -i cf-cache-status
```

1. **P1 — Check token scopes.**
   - **Action:** If purge API 403s, the Workers-edit token lacks Cache Purge.
   - **Expected:** Operator uses dashboard or a dedicated purge token.
   - **On failure:** Do not keep deploying hoping ?v= fixes HTML.
2. **P2 — Purge HTML URL.**
   - **Action:** Purge production (and preview) HTML. View-source the unique string.
   - **Expected:** Body matches origin.
   - **On failure:** HIT with stale body is [OEN-S05](s05-tunnel-preview-stale-hit.md).
3. **P3 — Origin no-store on HTML.**
   - **Action:** Prefer `CDN-Cache-Control: no-store` on HTML responses.
   - **Expected:** HTML is not a long-lived HIT.
   - **On failure:** Assets may still cache.

## Expected samples

```text
cf-cache-status: HIT
```

## Verify

- Live view-source has the new string.
- Purge token limitation was stated if it applied.
- ICMP / small ping success was **not** used as the pass criterion when this spec names TCP, SSH, or HTTPS.
- Bind table was filled by a human before any live `ip` / nft / iptables change.

## MUST NOT

- MUST NOT treat ?v= as a substitute for HTML zone purge.
- MUST NOT hide a 403 purge as a code bug.
- MUST NOT apply live network or firewall changes until Bind is filled by a human.
- MUST NOT claim a fix on ICMP ping alone when Verify names TCP, SSH, or HTTPS.
- MUST NOT publish hostnames, addresses, ULAs, or custom ports.

## Related specs

- [OEN-09](../web/09-git-merge-is-not-a-live-worker.md)
- [OEN-S05](s05-tunnel-preview-stale-hit.md)

## Prior art (Not novel)

Cloudflare purge docs exist. This note is the Workers-edit token gap plus ?v= does not replace HTML purge.

