---
id: "OEN-11"
title: "Worker chat wrapper, Turnstile, sanitize large-language-model drift"
kind: "original"
status: "active"
edition: 2
date_published: "2026-09-08"
author: "Eugene Armstead"
author_url: "https://www.armsteadent.com/"
canonical: "https://eugenearmstead.github.io/overlay-and-edge-notes/web/11-worker-chat-wrapper-turnstile.html"
keywords:
  - "Worker chat iframe vs wrapper"
  - "Cloudflare Turnstile chat"
  - "sanitize LLM drift"
  - "same-origin chatbot.html"
  - "nginx chatbot-api proxy"
  - "Turnstile gate iframe"
  - "strip forbidden phrases client"
  - "Worker chat FAQ every request"
  - "Cloudflare Worker chatbot"
  - "bilingual privacy chat"
  - "iframe only when copy stable"
  - "LLM output sanitize"
backs:
  []
backed_by:
  - OEN-S06
  - OEN-S09
description: "Iframe a Worker chat only when copy is stable. Otherwise use a same-origin wrapper, optional reverse-proxy API, send official FAQ every request, strip forbidden phrases client-side, gate with Turnstile."
terms:
  - abbr: API
    expansion: application programming interface
  - abbr: AUD
    expansion: OAuth audience identifier
  - abbr: CSS
    expansion: Cascading Style Sheets
  - abbr: DOM
    expansion: Document Object Model
  - abbr: FAQ
    expansion: frequently asked questions
  - abbr: HTML
    expansion: HyperText Markup Language
  - abbr: HTTPS
    expansion: Hypertext Transfer Protocol Secure
  - abbr: JS
    expansion: JavaScript
  - abbr: NAP
    expansion: name, address, and phone (local-business citation data)
  - abbr: OEN
    expansion: Overlay and Edge Notes
  - abbr: Playwright
    expansion: browser automation and test runner
  - abbr: Turnstile
    expansion: Cloudflare bot challenge widget
  - abbr: UI
    expansion: user interface
  - abbr: URL
    expansion: Uniform Resource Locator
---

# Worker chat wrapper, Turnstile, sanitize large-language-model drift

## Context

Worker chat on a static site: iframe the Worker only when copy is stable. Otherwise a same-origin wrapper (`chatbot.html`) plus optional nginx `/chatbot-api/` proxy. Send official frequently asked questions (FAQ) every request. Strip forbidden phrases client-side before display. Gate the iframe with Turnstile. Bilingual privacy links.

MUST NOT publish lead-feed URLs, Access audience (AUD) values, Signal, or device-snapshot as a tracking recipe. [OEN-08](08-worker-html-localhost-debug.md) still applies to the wrapper HTML.

## Topology

N/A — deploy

## Bind

Fill this table **before** any live change. Do **not** paste real values back into public notes.

| Placeholder | Operator fills | Class |
|-------------|----------------|-------|
| `<worker-root>` | Worker / UI source tree | Directory |
| `<live-url>` | Public HTTPS origin | URL |

## Formulas

MUST NOT publish lead-feed URLs, Access AUDs, or device-snapshot recipes. [OEN-08](08-worker-html-localhost-debug.md) still applies.

## Decision

Prefer same-origin wrapper when the model drifts. MUST sanitize on the client before paint. MUST send the official FAQ payload every request. MUST NOT ship localhost ingest in the wrapper.

## Consequences

- Drifted phrases never reach the visitor.
- Turnstile reduces anonymous scrape of the iframe.
- Privacy links stay on the wrapper, not only the Worker origin.

## Agent stop rule

> MUST emit wrapper vs iframe and Turnstile checks with `<live-url>` filled.
> MUST NOT deploy until Bind is filled.
> MUST NOT publish site secrets, Access ids, or prompt text that identifies a lab.
> MUST NOT apply netfilter from this page.

## Procedure


### Copy-paste commands (after Bind)

```bash
rg -n "127\\.0\\.0\\.1:7450|X-Debug-Session-Id|/ingest/" <worker-root> || true
curl -sS -o /dev/null -w '%{http_code}\n' --max-time 15 <live-url>/chatbot.html
```

1. **P1 — Choose iframe vs wrapper.**
   - **Action:** If copy is stable and the Worker origin is acceptable in an iframe, iframe. If the model invents services or NAP, use `chatbot.html` same-origin plus optional `/chatbot-api/` proxy.
   - **Expected:** Visitor never sees a raw drifting iframe without sanitizer.
   - **On failure:** Do not mix both without a single source of CSS ([OEN-S06](../supporting/s06-do-not-ship-html-only.md)).
2. **P2 — FAQ every request; strip forbidden phrases.**
   - **Action:** The client sends the official FAQ (or the Worker injects it). Before `textContent`/HTML insert, strip a deny-list of phrases.
   - **Expected:** Forbidden phrases never appear in the DOM.
   - **On failure:** Server-only filter is not enough if the Worker streams.
3. **P3 — Turnstile gate; privacy links.**
   - **Action:** Gate the iframe or form with Turnstile. Link privacy in both languages the site uses.
   - **Expected:** No chat UI until Turnstile succeeds (or documented fallback).
   - **On failure:** Do not log Turnstile tokens in page JS.
4. **P4 — Safety grep and layout gate.**
   - **Action:** `rg` for 127.0.0.1 ingest ([OEN-08](08-worker-html-localhost-debug.md)). Playwright Desktop + iPhone + Pixel ([OEN-S09](../supporting/s09-playwright-desktop-iphone-pixel.md)).
   - **Expected:** No ingest strings. Layout holds on three devices.
   - **On failure:** A missing CSS 404 looks like a “chat CSS bug” ([OEN-S06](../supporting/s06-do-not-ship-html-only.md)).

## Expected samples

```text
# No ingest strings in view-source; Turnstile present before chat UI
```

## Verify

- Wrapper or iframe policy is documented and matches live HTML.
- Forbidden phrases cannot render.
- Turnstile gates the chat.
- No localhost ingest; no lead-feed or Access AUDs in the public spec or page.

## MUST NOT

- MUST NOT publish lead-feed URLs, Access AUDs, Signal, or device-snapshot recipes.
- MUST NOT ship localhost debug beacons in the wrapper.
- MUST NOT iframe an unstable Worker without a sanitizer.
- MUST NOT skip bilingual privacy links the site already uses elsewhere.
- MUST NOT publish hostnames, addresses, ULAs, or custom ports.

## Page changelog

- Edition 2 (8 Sep 2026, Mountain Time): Trap-specific Bind and agent stop rule (review cleanup).

## Related specs

- [OEN-08 Localhost debug beacons](08-worker-html-localhost-debug.md)
- [OEN-10 One blocking stylesheet](10-one-blocking-stylesheet-variable-fonts.md)
- [OEN-S06 Do not ship HTML-only](../supporting/s06-do-not-ship-html-only.md)
- [OEN-S09 Playwright three devices](../supporting/s09-playwright-desktop-iphone-pixel.md)

