---
id: "OEN-S04"
title: "Purge the content delivery network after deploy"
kind: "supporting"
status: "active"
edition: 2
date_published: "2026-09-08"
author: "Eugene Armstead"
author_url: "https://www.armsteadent.com/"
canonical: "https://eugenearmstead.github.io/overlay-and-edge-notes/supporting/s04-purge-cdn-after-deploy.html"
keywords:
  - "purge CDN after deploy"
  - "Workers-edit lacks Cache Purge"
  - "query string not HTML purge"
  - "Cloudflare zone purge"
  - "CDN-Cache-Control no-store"
  - "?v= cache bust HTML"
  - "Cloudflare Cache Purge token"
  - "stale HTML after deploy"
  - "purge preview URL"
  - "Wrangler deploy then purge"
  - "Workers cache API permission"
  - "HTML still old after ship"
backs:
  - OEN-08
  - OEN-09
  - OEN-10
backed_by:
  []
description: "After a successful deploy, purge HTML. Workers-edit tokens often lack Cache Purge. Query-string cache busts do not replace a zone purge for HTML."
terms:
  - abbr: API
    expansion: application programming interface
  - abbr: CDN
    expansion: content delivery network
  - abbr: Cloudflare
    expansion: content delivery and Workers platform
  - abbr: HIT
    expansion: cache HIT (content still served from cache)
  - abbr: HTML
    expansion: HyperText Markup Language
  - abbr: HTTPS
    expansion: Hypertext Transfer Protocol Secure
  - abbr: OEN
    expansion: Overlay and Edge Notes
  - abbr: URL
    expansion: Uniform Resource Locator
---

# Purge the content delivery network after deploy

## Context

Known Cloudflare advice. Unique add-ons: a token with Workers edit often **lacks Cache Purge**; `?v=` does not replace zone purge for HTML. Backs [OEN-08](../web/08-worker-html-localhost-debug.md), [OEN-09](../web/09-git-merge-is-not-a-live-worker.md), [OEN-10](../web/10-one-blocking-stylesheet-variable-fonts.md).

## Topology

N/A — deploy

## Bind

Fill this table **before** any live change. Do **not** paste real values back into public notes.

| Placeholder | Operator fills | Class |
|-------------|----------------|-------|
| `<live-url>` | Public HTTPS origin | URL |

## Method

Purge the HTML URL (and preview URL if tunneled). If the deploy token cannot purge, say so. Prefer origin `CDN-Cache-Control: no-store` on HTML.

## Consequences

Visitors see the new HTML. Operators are not told the CDN is “haunted.”

## Agent stop rule

> MUST emit the purge command for `<live-url>` (and `<preview-url>` if used) after Bind is filled.
> MUST NOT claim a deploy is visible while CDN still HITs a stale body.
> MUST say so if the token cannot purge.
> MUST NOT apply netfilter from this page.

## Procedure


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

## MUST NOT

- MUST NOT treat ?v= as a substitute for HTML zone purge.
- MUST NOT hide a 403 purge as a code bug.
- MUST NOT publish hostnames, addresses, ULAs, or custom ports.

## Page changelog

- Edition 2 (8 Sep 2026, Mountain Time): Trap-specific Bind and agent stop rule (review cleanup).

## Related specs

- [OEN-09](../web/09-git-merge-is-not-a-live-worker.md)
- [OEN-S05](s05-tunnel-preview-stale-hit.md)

