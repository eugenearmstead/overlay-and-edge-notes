---
id: "OEN-S05"
title: "Tunnel preview HIT with a stale body"
kind: "supporting"
status: "active"
edition: 2
date_published: "2026-09-08"
author: "Eugene Armstead"
author_url: "https://www.armsteadent.com/"
canonical: "https://eugenearmstead.github.io/overlay-and-edge-notes/supporting/s05-tunnel-preview-stale-hit.html"
keywords:
  - "tunnel preview HIT stale body"
  - "Cloudflare Tunnel cf-cache-status HIT"
  - "origin new preview old"
  - "purge preview URL"
  - "CDN-Cache-Control no-store HTML"
  - "cloudflared preview cache"
  - "stale HIT after origin update"
  - "Workers preview cache"
  - "cf-cache-status HIT wrong body"
  - "tunnel cache purge"
  - "preview URL still old"
  - "origin 200 stale CDN"
backs:
  - OEN-08
  - OEN-09
backed_by:
  []
description: "Origin can already be new while a Cloudflare Tunnel preview still serves HIT with a stale body until the preview URL is purged."
terms:
  - abbr: CDN
    expansion: content delivery network
  - abbr: Cloudflare
    expansion: content delivery and Workers platform
  - abbr: CSS
    expansion: Cascading Style Sheets
  - abbr: HIT
    expansion: cache HIT (content still served from cache)
  - abbr: HTML
    expansion: HyperText Markup Language
  - abbr: JS
    expansion: JavaScript
  - abbr: OEN
    expansion: Overlay and Edge Notes
  - abbr: URL
    expansion: Uniform Resource Locator
---

# Tunnel preview HIT with a stale body

## Context

Preview `cf-cache-status: HIT` with a stale body after origin is new. Prefer origin `CDN-Cache-Control: no-store` on HTML.

## Topology

N/A — deploy

## Bind

Fill this table **before** any live change. Do **not** paste real values back into public notes.

| Placeholder | Operator fills | Class |
|-------------|----------------|-------|
| `<preview-url>` | Preview origin if used | URL |

## Method

Purge the preview URL. Do not debug templates until view-source on preview matches origin.

## Consequences

False “deploy failed” reports drop.

## Agent stop rule

> MUST view-source `<preview-url>` and compare to origin after Bind is filled.
> MUST NOT debug templates until preview matches origin.
> MUST NOT treat `cf-cache-status: HIT` as a code bug.
> MUST NOT apply netfilter from this page.

## Procedure


### Copy-paste commands (after Bind)

```bash
curl -sS -D- -o /tmp/preview.body --max-time 15 <preview-url> | tr -d '\r' | grep -iE 'cf-cache-status|cdn-cache-control'
# Compare body hash to origin file; mismatch + HIT = this spec.
```

1. **P1 — Compare origin vs preview.**
   - **Action:** curl origin unique string vs preview URL headers and body.
   - **Expected:** Origin new; preview HIT stale.
   - **On failure:** If origin is also old, this is not a preview cache issue.
2. **P2 — Purge preview URL.**
   - **Action:** Purge that exact URL. Prefer no-store on HTML.
   - **Expected:** Preview body matches origin.
   - **On failure:** Workers-edit token may lack purge ([OEN-S04](s04-purge-cdn-after-deploy.md)).
3. **P3 — Do not ship ingest while iterating.**
   - **Action:** Keep [OEN-08](../web/08-worker-html-localhost-debug.md) grep clean.
   - **Expected:** No 127.0.0.1 ingest.
   - **On failure:** Debug locally in files, not page JS.

## Expected samples

```text
cf-cache-status: HIT
# body still previous deploy
```

## Verify

- Preview view-source matches origin.
- cf-cache-status is not HIT-stale.

## MUST NOT

- MUST NOT debug CSS for a stale HIT body.
- MUST NOT skip preview purge.
- MUST NOT publish hostnames, addresses, ULAs, or custom ports.

## Page changelog

- Edition 2 (8 Sep 2026, Mountain Time): Trap-specific Bind and agent stop rule (review cleanup).

## Related specs

- [OEN-S04](s04-purge-cdn-after-deploy.md)
- [OEN-09](../web/09-git-merge-is-not-a-live-worker.md)

