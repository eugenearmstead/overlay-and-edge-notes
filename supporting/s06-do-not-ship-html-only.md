---
id: OEN-S06
title: "Do not ship HTML-only"
kind: supporting
status: active
edition: 1
date_published: 2026-09-08
author: Eugene Armstead
author_url: https://www.armsteadent.com/
canonical: https://eugenearmstead.github.io/overlay-and-edge-notes/supporting/s06-do-not-ship-html-only.html
keywords:
  - "do not ship HTML-only"
  - "CSS 404 looks like CSS bug"
  - "JS images must 200"
  - "layout destroying miss"
  - "rsync HTML without assets"
  - "static site missing chrome.css"
  - "Cloudflare origin 404 CSS"
  - "deploy incomplete assets"
  - "HTML 200 CSS 404"
  - "verify every static URL"
  - "Playwright asset 200"
  - "tmpfs origin missing files"
backs:
  - OEN-08
  - OEN-09
  - OEN-10
  - OEN-11
backed_by: []
description: "CSS, JavaScript, and images must return 200. A layout-destroying miss looks like a CSS bug."
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
  - abbr: CSS
    expansion: Cascading Style Sheets
  - abbr: JS
    expansion: JavaScript
  - abbr: nft
    expansion: nftables (Linux packet filter)
  - abbr: URL
    expansion: Uniform Resource Locator
  - abbr: UI
    expansion: user interface
  - abbr: RAM
    expansion: random-access memory
  - abbr: tmpfs
    expansion: temporary file system in RAM
  - abbr: Playwright
    expansion: browser automation and test runner
  - abbr: Wrangler
    expansion: Cloudflare Workers command-line tool
---

# Do not ship HTML-only

## Context

HTML-only rsync to the wrong tree looks deployed. Layout explodes. Operators rewrite CSS.

## Topology

```text
[HTML 200] + [chrome.css 404]  looks like a "CSS bug"
Ship HTML + CSS + JS + images together
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

Ship CSS/JS/images with HTML. Check 200s. Canonical disk then RAM origin is [OEN-S08](s08-canonical-disk-tmpfs-origin.md).

## Consequences

“CSS bugs” that were 404s go away.

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
for u in <live-url> <live-url>/chrome.css; do curl -sS -o /dev/null -w '%{http_code} %{url_effective}\n' --max-time 15 "$u"; done
```

1. **P1 — List assets in the new HTML.**
   - **Action:** Extract href/src. curl each with -o /dev/null -w '%{http_code}'.
   - **Expected:** All 200.
   - **On failure:** A 404 is a ship miss, not a selector bug.
2. **P2 — Confirm the tree you synced.**
   - **Action:** Persistent canonical vs tmpfs serve ([OEN-S08](s08-canonical-disk-tmpfs-origin.md)).
   - **Expected:** You synced the tree the origin actually reads.
   - **On failure:** HTML-only to the other tree looks live and broken.
3. **P3 — Layout gate.**
   - **Action:** Playwright three devices if nav/hero/CSS changed ([OEN-S09](s09-playwright-desktop-iphone-pixel.md)).
   - **Expected:** Layout holds.
   - **On failure:** Do not skip because “it was only HTML.”

## Expected samples

```text
200 https://example.example/
404 https://example.example/chrome.css
```

## Verify

- Asset URLs 200.
- Correct tree synced.
- ICMP / small ping success was **not** used as the pass criterion when this spec names TCP, SSH, or HTTPS.
- Bind table was filled by a human before any live `ip` / nft / iptables change.

## MUST NOT

- MUST NOT call a 404 stylesheet a CSS bug.
- MUST NOT HTML-only rsync to the RAM tree.
- MUST NOT apply live network or firewall changes until Bind is filled by a human.
- MUST NOT claim a fix on ICMP ping alone when Verify names TCP, SSH, or HTTPS.
- MUST NOT publish hostnames, addresses, ULAs, or custom ports.

## Related specs

- [OEN-S08](s08-canonical-disk-tmpfs-origin.md)
- [OEN-10](../web/10-one-blocking-stylesheet-variable-fonts.md)

## Prior art (Not novel)

Broken asset 404s are obvious in hindsight. This note exists because they present as design bugs.

