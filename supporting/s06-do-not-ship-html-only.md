---
id: "OEN-S06"
title: "Do not ship HTML-only"
kind: "supporting"
status: "active"
edition: 2
date_published: "2026-09-08"
author: "Eugene Armstead"
author_url: "https://www.armsteadent.com/"
canonical: "https://eugenearmstead.github.io/overlay-and-edge-notes/supporting/s06-do-not-ship-html-only.html"
keywords:
  - "do not ship HTML-only"
  - "CSS 404 looks like CSS bug"
  - "JS images must 200"
  - "layout destroying miss"
  - "rsync HTML without assets"
  - "static site missing <site.css>"
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
backed_by:
  []
description: "CSS, JavaScript, and images must return 200. A layout-destroying miss looks like a CSS bug."
terms:
  - abbr: CSS
    expansion: Cascading Style Sheets
  - abbr: HTML
    expansion: HyperText Markup Language
  - abbr: HTTP
    expansion: Hypertext Transfer Protocol
  - abbr: HTTPS
    expansion: Hypertext Transfer Protocol Secure
  - abbr: JS
    expansion: JavaScript
  - abbr: OEN
    expansion: Overlay and Edge Notes
  - abbr: Playwright
    expansion: browser automation and test runner
  - abbr: RAM
    expansion: random-access memory
  - abbr: URL
    expansion: Uniform Resource Locator
---

# Do not ship HTML-only

## Context

HTML-only rsync to the wrong tree looks deployed. Layout explodes. Operators rewrite CSS.

## Topology

N/A — deploy

## Bind

Fill this table **before** any live change. Do **not** paste real values back into public notes.

| Placeholder | Operator fills | Class |
|-------------|----------------|-------|
| `<live-url>` | Public HTTPS origin | URL |
| `<site.css>` | Origin stylesheet filename | Asset |

## Method

Ship CSS/JS/images with HTML. Check 200s. Canonical disk then RAM origin is [OEN-S08](s08-canonical-disk-tmpfs-origin.md).

## Consequences

“CSS bugs” that were 404s go away.

## Agent stop rule

> MUST emit a bound asset-curl list (`<live-url>` + every href/src) after Bind is filled.
> MUST NOT deploy until that list is HTTP 200.
> MUST NOT call a 404 stylesheet a CSS bug.
> MUST NOT file an upstream CSS/browser bug from this page.

## Procedure


### Copy-paste commands (after Bind)

```bash
for u in <live-url> <live-url>/<site.css>; do curl -sS -o /dev/null -w '%{http_code} %{url_effective}\n' --max-time 15 "$u"; done
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
404 https://example.example/<site.css>
```

## Verify

- Asset URLs 200.
- Correct tree synced.

## MUST NOT

- MUST NOT call a 404 stylesheet a CSS bug.
- MUST NOT HTML-only rsync to the RAM tree.
- MUST NOT publish hostnames, addresses, ULAs, or custom ports.

## Page changelog

- Edition 2 (8 Sep 2026, Mountain Time): Trap-specific Bind and agent stop rule (review cleanup).

## Related specs

- [OEN-S08](s08-canonical-disk-tmpfs-origin.md)
- [OEN-10](../web/10-one-blocking-stylesheet-variable-fonts.md)

