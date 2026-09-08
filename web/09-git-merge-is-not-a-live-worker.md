---
id: OEN-09
title: "Git merge is not a live Worker (timed Wrangler fallback)"
kind: original
status: active
edition: 1
date_published: 2026-09-08
author: Eugene Armstead
author_url: https://www.armsteadent.com/
canonical: https://eugenearmstead.github.io/overlay-and-edge-notes/web/09-git-merge-is-not-a-live-worker.html
keywords:
  - "git merge is not a live Worker"
  - "Cloudflare Git build lag"
  - "Wrangler timed fallback"
  - "Workers-edit token lacks Cache Purge"
  - "connected Worker never started"
  - "GitLab merge not deployed"
  - "wrangler deploy after 10 minutes"
  - "Cloudflare Builds stuck"
  - "Rocket Loader Off"
  - "source of truth vs live Worker"
  - "Workers cache purge token"
  - "preview HIT stale body"
backs: []
backed_by:
  - OEN-S04
  - OEN-S05
  - OEN-S07
  - OEN-S12
description: "A merged git source of truth is not a live Cloudflare Worker. Wait about ten minutes, then Wrangler without asking. Workers-edit tokens often lack Cache Purge."
terms:
  - abbr: OEN
    expansion: Overlay and Edge Notes
  - abbr: SSH
    expansion: Secure Shell
  - abbr: TCP
    expansion: Transmission Control Protocol
  - abbr: ICMP
    expansion: Internet Control Message Protocol
  - abbr: HTTP
    expansion: Hypertext Transfer Protocol
  - abbr: HTTPS
    expansion: Hypertext Transfer Protocol Secure
  - abbr: HTML
    expansion: HyperText Markup Language
  - abbr: CSS
    expansion: Cascading Style Sheets
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
  - abbr: Rocket
    expansion: Cloudflare Rocket Loader
---

# Git merge is not a live Worker (timed Wrangler fallback)

## Context

Connected Cloudflare Git builds can lag or never start. Merge is source-of-truth only. After about ten minutes with no successful Worker update, Wrangler upload MUST run without asking the operator. Separate Workers (chat, gated apps) often **are not** on the Git build at all.

A token with Workers edit often **lacks Cache Purge** — say so; use the dashboard or a dedicated purge token ([OEN-S04](../supporting/s04-purge-cdn-after-deploy.md)). Tunnel preview can show `cf-cache-status: HIT` with a **stale body** ([OEN-S05](../supporting/s05-tunnel-preview-stale-hit.md)). Rocket Loader Off ([OEN-S12](../supporting/s12-rocket-loader-off.md)). Git merge `405` while mergeability is pending is timing, not a dead token ([OEN-S07](../supporting/s07-git-merge-405-pending.md)).

## Topology

```text
[git merge] --> connected Cloudflare Git build  (MAY lag or never start)
        \
         +-- wait ~10 min --> Wrangler upload if no live Worker update
Separate Workers (chat, gated apps) often are NOT on the Git build
Tunnel preview: cf-cache-status HIT with stale body ([OEN-S05](../supporting/s05-tunnel-preview-stale-hit.md))
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

## Decision

Treat merge as source only. Wait ~10 minutes. Then Wrangler. Purge with a token that can purge. Prefer origin `CDN-Cache-Control: no-store` on HTML.

## Consequences

- Production HTML matches the merged source even when Git builds stall.
- Operators hear “purge token missing” instead of “cache is haunted.”
- Preview HIT-with-stale-body is a known purge, not a code bug.

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
# After a merge, wait ~10 minutes. If the live Worker did not update, Wrangler without asking.
# Purge: Workers-edit token often lacks Cache Purge — dashboard or dedicated token ([OEN-S04](../supporting/s04-purge-cdn-after-deploy.md)).
curl -sS -D- -o /dev/null --max-time 15 <live-url> | tr -d '\r' | grep -iE 'cf-cache-status|cf-ray|age:'
```

1. **P1 — Confirm merge vs live Worker.**
   - **Action:** Note merge time. Fetch the Worker version / `modified_on` (or equivalent) and a unique string from live HTML.
   - **Expected:** If live still lacks the string after ~10 minutes, Git build did not ship.
   - **On failure:** A lone merge HTTP 405 is [OEN-S07](../supporting/s07-git-merge-405-pending.md) — wait mergeability, do not declare a dead token yet.
2. **P2 — Wrangler fallback without asking.**
   - **Action:** Deploy the same tree with Wrangler. Confirm the Worker version advanced.
   - **Expected:** Live HTML contains the unique string.
   - **On failure:** If Wrangler auth fails, tell the operator immediately — that is not a wait-longer case.
3. **P3 — Purge HTML; do not trust ?v= alone.**
   - **Action:** Purge the HTML URL. If the Workers-edit token cannot purge, say so and use dashboard or a purge token ([OEN-S04](../supporting/s04-purge-cdn-after-deploy.md)).
   - **Expected:** cf-cache-status is not HIT with a stale body. View-source matches origin.
   - **On failure:** Tunnel preview HIT-stale is [OEN-S05](../supporting/s05-tunnel-preview-stale-hit.md).
4. **P4 — Rocket Loader Off on that zone/route.**
   - **Action:** If analytics or smoke broke after ship, confirm Rocket Loader is Off ([OEN-S12](../supporting/s12-rocket-loader-off.md)).
   - **Expected:** Inline scripts are not rewritten.
   - **On failure:** Do not debug CSS for a Rocket Loader rewrite.

## Expected samples

```text
cf-cache-status: HIT
# Origin already new; body still old until purge
```

## Verify

- Live Worker version is new; HTML has the merged unique string.
- HTML purged or origin no-store.
- Auth failures were reported, not waited out.
- Chat/gated Workers not on the Git build were deployed separately if they changed.
- ICMP / small ping success was **not** used as the pass criterion when this spec names TCP, SSH, or HTTPS.
- Bind table was filled by a human before any live `ip` / nft / iptables change.

## MUST NOT

- MUST NOT treat git merge as a live Worker.
- MUST NOT wait indefinitely for a Git build that never started.
- MUST NOT hide a 401/unauthorized token as “wait longer.”
- MUST NOT ship localhost debug beacons ([OEN-08](08-worker-html-localhost-debug.md)).
- MUST NOT apply live network or firewall changes until Bind is filled by a human.
- MUST NOT claim a fix on ICMP ping alone when Verify names TCP, SSH, or HTTPS.
- MUST NOT publish hostnames, addresses, ULAs, or custom ports.

## Related specs

- [OEN-08 Localhost debug beacons](08-worker-html-localhost-debug.md)
- [OEN-S04 Purge the CDN](../supporting/s04-purge-cdn-after-deploy.md)
- [OEN-S05 Tunnel preview stale HIT](../supporting/s05-tunnel-preview-stale-hit.md)
- [OEN-S07 Git merge 405 pending](../supporting/s07-git-merge-405-pending.md)
- [OEN-S12 Rocket Loader Off](../supporting/s12-rocket-loader-off.md)

## Prior art (Not novel)

Cloudflare Git builds and Wrangler are documented. This spec’s claim is the timed fallback plus purge-token gap plus preview HIT-stale as one ops contract.

