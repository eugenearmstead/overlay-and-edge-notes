---
id: OEN-08
title: Do not ship localhost debug beacons in Worker HTML
kind: original
status: active
edition: 1
date_published: 2026-09-07
author: Eugene Armstead
author_url: https://www.armsteadent.com/
canonical: https://eugenearmstead.github.io/overlay-and-edge-notes/web/08-worker-html-localhost-debug.html
keywords:
  - cloudflare-workers
  - localhost
  - local-network-access
  - debug-beacons
backs: []
backed_by: []
description: Agent debug templates that fetch 127.0.0.1 ingest URLs must never ship in Cloudflare Worker HTML; browsers prompt for local-network access on public HTTPS pages.
terms:
  - abbr: OEN
    expansion: Overlay and Edge Notes
  - abbr: HTML
    expansion: HyperText Markup Language
  - abbr: JS
    expansion: JavaScript
  - abbr: HTTP
    expansion: Hypertext Transfer Protocol
  - abbr: HTTPS
    expansion: Hypertext Transfer Protocol Secure
  - abbr: URL
    expansion: Uniform Resource Locator
  - abbr: CDN
    expansion: content delivery network
  - abbr: NDJSON
    expansion: newline-delimited JavaScript Object Notation
  - abbr: LNA
    expansion: Local Network Access (browser permission)
  - abbr: UI
    expansion: user interface
  - abbr: PC
    expansion: personal computer
  - abbr: JS
    expansion: JavaScript
  - abbr: JSON
    expansion: JavaScript Object Notation
  - abbr: HIT
    expansion: cache HIT (content still served from cache)
  - abbr: CSS
    expansion: Cascading Style Sheets
---

# Do not ship localhost debug beacons in Worker HTML

## Context

Coding-agent debug templates often inject a browser beacon:

```js
fetch('http://127.0.0.1:7450/ingest/…', { /* headers include X-Debug-Session-Id */ })
```

That is fine inside a **local** app on the author’s machine. It is not fine inside HyperText Markup Language (HTML) or JavaScript (JS) that a **Cloudflare Worker** (or any public `https://` origin) sends to a real browser.

Chromium and Brave then prompt: **“Access other apps and services on this device”** (Local Network Access). The site owner should not be the first person to see that prompt on a live page.

A Worker `fetch('http://127.0.0.1:…')` on the **edge** is also useless: the isolate cannot reach the author’s personal computer (PC). It is dead code plus noise.

Local Network Access (LNA) itself is documented. The unique warning is **shipping agent ingest into Worker-rendered HTML**.

## Decision

Anything that becomes a Hypertext Transfer Protocol (HTTP) **Response body** (HTML templates, inline `<script>`, bundled browser JS) MUST NOT contain:

- `127.0.0.1:7450` or `localhost:7450`
- `/ingest/` debug paths of that family
- `X-Debug-Session-Id`

Predeploy MUST grep the Worker/UI tree and **fail the ship** on client-executed hits.

Log from office scripts that write newline-delimited JSON (NDJSON) to a local file, or from temporary **server** `console.log` / audit rows — not from page JS.

## Consequences

- Public pages stop triggering local-network permission prompts.
- Debug still exists, just not in the browser.
- If a prompt already fired, remove beacons, redeploy, and tell the operator to **Block** once if the old page is cached, then hard-refresh.

## Procedure

Placeholders: a Worker or static origin that emits HTML. No private site internals.

1. **P1 — Search the ship tree before deploy.**
   - **Action:** From the Worker/UI root:

     ```bash
     rg -n "127\\.0\\.0\\.1:7450|localhost:7450|/ingest/[0-9a-f-]{8}|X-Debug-Session-Id" src/ public/ || true
     ```

   - **Expected:** No matches in files that land in a Response body (`*.html`, `ui.js` templates, browser bundles).
   - **On failure:** Treat hits as blockers. Delete or gate them behind a build that never ships.

2. **P2 — Classify leftover hits.**
   - **Action:** If `rg` matches an agent-only Node script that never ships, keep it off the bundle. Prefer file logging.
   - **Expected:** Client-executed strings are clean. Agent-only scripts MAY log locally.
   - **On failure:** Move instrumentation out of templates.

3. **P3 — Do not add edge fetch to loopback.**
   - **Action:** Review Worker `fetch` handlers for `127.0.0.1` / `localhost`.
   - **Expected:** None. The edge cannot reach the author’s machine.
   - **On failure:** Remove it. Use `console.log` on the isolate or an origin you actually control.

4. **P4 — After a bad ship, clean cache.**
   - **Action:** Remove beacons, redeploy, purge the HTML URL if a content delivery network (CDN) caches it (forthcoming OEN-S04). Ask the operator to Block the prompt if it still appears, then hard-refresh.
   - **Expected:** View-source on the live HTML has zero `7450` / `X-Debug-Session-Id`.
   - **On failure:** Search generated strings, not only source files (templates may interpolate).

## Verify

- Predeploy `rg` is clean for client-executed paths.
- Live view-source has no loopback ingest URL.
- No Worker code fetches loopback.
- A browser on a fresh profile does not show a local-network permission prompt on that page.

## MUST NOT

- MUST NOT leave Cursor/agent ingest beacons in Worker HTML, even “just for this debug session.”
- MUST NOT fetch `127.0.0.1` from page JS on a public `https://` origin.
- MUST NOT fetch `127.0.0.1` from the Worker isolate expecting to reach the author’s PC.
- MUST NOT ship HTML comments that still contain ingest URLs (view-source is public).
- MUST NOT tell the operator the prompt is a “browser bug” before grepping the response body.

## Related specs

- OEN-09 Git merge is not a live Worker (forthcoming)
- OEN-S04 purge the CDN after deploy (forthcoming)
- OEN-S05 tunnel preview HIT with a stale body (forthcoming)
- OEN-S06 do not ship HTML-only (forthcoming)

## Prior art (Not novel)

Local Network Access prompts and “don’t call localhost from production” are known. This spec’s claim is the **agent-ingest + Worker HTML** failure mode: templates designed for a desktop debug port leaking onto a public HTTPS response.
