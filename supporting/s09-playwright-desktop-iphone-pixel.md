---
id: OEN-S09
title: "Playwright Desktop + iPhone + Pixel"
kind: supporting
status: active
edition: 1
date_published: 2026-09-08
author: Eugene Armstead
author_url: https://www.armsteadent.com/
canonical: https://eugenearmstead.github.io/overlay-and-edge-notes/supporting/s09-playwright-desktop-iphone-pixel.html
keywords:
  - "Playwright Desktop iPhone Pixel"
  - "Chromium device projects"
  - "layout nav hero three viewports"
  - "WebKit binaries not required"
  - "Playwright iPhone smoke"
  - "Pixel Android project"
  - "responsive CSS Playwright"
  - "site smoke Desktop Chrome"
  - "hero layout regression"
  - "Playwright test:smoke"
  - "iOS Android Chromium"
  - "nav footer legal smoke"
backs:
  - OEN-10
  - OEN-11
backed_by: []
description: "Layout, nav, and hero changes need Desktop Chrome, iPhone, and Pixel device projects. WebKit binaries are not required for this gate."
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
  - abbr: CSS
    expansion: Cascading Style Sheets
  - abbr: nft
    expansion: nftables (Linux packet filter)
  - abbr: URL
    expansion: Uniform Resource Locator
  - abbr: UI
    expansion: user interface
  - abbr: Playwright
    expansion: browser automation and test runner
  - abbr: WebKit
    expansion: Apple browser engine
  - abbr: Android
    expansion: mobile operating system
  - abbr: Chromium
    expansion: open-source browser engine
---

# Playwright Desktop + iPhone + Pixel

## Context

A desktop-only pass misses iOS wrapping and Android overflow.

## Topology

```text
Playwright projects: Desktop Chrome + iPhone + Pixel
Layout/nav/hero changes need all three
WebKit binaries not required for this gate
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

Run against preview default for marketing; production for gated apps.

## Method

Run Playwright Chromium device projects for Desktop, iPhone, and Pixel on nav/hero/CSS changes.

## Consequences

Fewer “works on my monitor” ships.

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
cd <worker-root> && npx playwright test --project=desktop --project=iphone --project=pixel
```

1. **P1 — Three projects.**
   - **Action:** Desktop Chrome + iPhone + Pixel (Chromium device emulation).
   - **Expected:** All three pass.
   - **On failure:** WebKit binaries not required for this gate.
2. **P2 — Exercise the changed flow.**
   - **Action:** Clicks/nav, not a single screenshot.
   - **Expected:** Behavior holds.
   - **On failure:** Empty and error states if the change touches them.
3. **P3 — Base URL.**
   - **Action:** Marketing often preview; gated apps may be production with auth out of band.
   - **Expected:** Tests hit the intended origin.
   - **On failure:** Do not hit localhost ingest ([OEN-08](../web/08-worker-html-localhost-debug.md)).

## Expected samples

```text
3 passed
```

## Verify

- Three device projects green for the change.
- ICMP / small ping success was **not** used as the pass criterion when this spec names TCP, SSH, or HTTPS.
- Bind table was filled by a human before any live `ip` / nft / iptables change.

## MUST NOT

- MUST NOT ship hero/nav CSS with desktop-only proof.
- MUST NOT require WebKit for this gate.
- MUST NOT apply live network or firewall changes until Bind is filled by a human.
- MUST NOT claim a fix on ICMP ping alone when Verify names TCP, SSH, or HTTPS.
- MUST NOT publish hostnames, addresses, ULAs, or custom ports.

## Related specs

- [OEN-10](../web/10-one-blocking-stylesheet-variable-fonts.md)
- [OEN-11](../web/11-worker-chat-wrapper-turnstile.md)

## Prior art (Not novel)

Responsive test matrices are standard. This note is the three Chromium device projects as the gate.

