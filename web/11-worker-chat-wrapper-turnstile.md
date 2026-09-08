---
id: OEN-11
title: "Worker chat wrapper, Turnstile, sanitize large-language-model drift"
kind: original
status: active
edition: 1
date_published: 2026-09-08
author: Eugene Armstead
author_url: https://www.armsteadent.com/
canonical: https://eugenearmstead.github.io/overlay-and-edge-notes/web/11-worker-chat-wrapper-turnstile.html
keywords:
  - cloudflare-workers
  - turnstile
  - chat
  - sanitize
backs: []
backed_by:
  - OEN-S06
  - OEN-S09
description: "Iframe a Worker chat only when copy is stable. Otherwise use a same-origin wrapper, optional reverse-proxy API, send official FAQ every request, strip forbidden phrases client-side, gate with Turnstile."
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
  - abbr: API
    expansion: application programming interface
  - abbr: nft
    expansion: nftables (Linux packet filter)
  - abbr: FAQ
    expansion: frequently asked questions
  - abbr: URL
    expansion: Uniform Resource Locator
  - abbr: UI
    expansion: user interface
  - abbr: Playwright
    expansion: browser automation and test runner
  - abbr: Turnstile
    expansion: Cloudflare bot challenge widget
  - abbr: AUD
    expansion: OAuth audience identifier
  - abbr: DOM
    expansion: Document Object Model
  - abbr: NAP
    expansion: name, address, and phone (local-business citation data)
---

# Worker chat wrapper, Turnstile, sanitize large-language-model drift

## Context

Worker chat on a static site: iframe the Worker only when copy is stable. Otherwise a same-origin wrapper (`chatbot.html`) plus optional nginx `/chatbot-api/` proxy. Send official frequently asked questions (FAQ) every request. Strip forbidden phrases client-side before display. Gate the iframe with Turnstile. Bilingual privacy links.

MUST NOT publish lead-feed URLs, Access audience (AUD) values, Signal, or device-snapshot as a tracking recipe. [OEN-08](08-worker-html-localhost-debug.md) still applies to the wrapper HTML.

## Topology

```text
[static origin]
    iframe Worker chat     -- only if copy is stable
    else chatbot.html wrapper + optional same-origin /chatbot-api/ proxy
    FAQ every request; strip forbidden phrases before paint; Turnstile gate
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

MUST NOT publish lead-feed URLs, Access AUDs, or device-snapshot recipes. [OEN-08](08-worker-html-localhost-debug.md) still applies.

## Decision

Prefer same-origin wrapper when the model drifts. MUST sanitize on the client before paint. MUST send the official FAQ payload every request. MUST NOT ship localhost ingest in the wrapper.

## Consequences

- Drifted phrases never reach the visitor.
- Turnstile reduces anonymous scrape of the iframe.
- Privacy links stay on the wrapper, not only the Worker origin.

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
- ICMP / small ping success was **not** used as the pass criterion when this spec names TCP, SSH, or HTTPS.
- Bind table was filled by a human before any live `ip` / nft / iptables change.

## MUST NOT

- MUST NOT publish lead-feed URLs, Access AUDs, Signal, or device-snapshot recipes.
- MUST NOT ship localhost debug beacons in the wrapper.
- MUST NOT iframe an unstable Worker without a sanitizer.
- MUST NOT skip bilingual privacy links the site already uses elsewhere.
- MUST NOT apply live network or firewall changes until Bind is filled by a human.
- MUST NOT claim a fix on ICMP ping alone when Verify names TCP, SSH, or HTTPS.
- MUST NOT publish hostnames, addresses, ULAs, or custom ports.

## Related specs

- [OEN-08 Localhost debug beacons](08-worker-html-localhost-debug.md)
- [OEN-10 One blocking stylesheet](10-one-blocking-stylesheet-variable-fonts.md)
- [OEN-S06 Do not ship HTML-only](../supporting/s06-do-not-ship-html-only.md)
- [OEN-S09 Playwright three devices](../supporting/s09-playwright-desktop-iphone-pixel.md)

## Prior art (Not novel)

Turnstile and iframe chat are documented. This spec’s claim is wrapper-when-drift plus client sanitize plus FAQ-every-request plus what not to publish.

