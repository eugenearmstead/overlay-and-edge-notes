---
id: "OEN-S09"
title: "Playwright Desktop + iPhone + Pixel"
kind: "supporting"
status: "active"
edition: 2
date_published: "2026-09-08"
author: "Eugene Armstead"
author_url: "https://www.armsteadent.com/"
canonical: "https://eugenearmstead.github.io/overlay-and-edge-notes/supporting/s09-playwright-desktop-iphone-pixel.html"
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
backed_by:
  []
description: "Layout, nav, and hero changes need Desktop Chrome, iPhone, and Pixel device projects. WebKit binaries are not required for this gate."
terms:
  - abbr: Android
    expansion: mobile operating system
  - abbr: Chromium
    expansion: open-source browser engine
  - abbr: CSS
    expansion: Cascading Style Sheets
  - abbr: OEN
    expansion: Overlay and Edge Notes
  - abbr: Playwright
    expansion: browser automation and test runner
  - abbr: UI
    expansion: user interface
  - abbr: URL
    expansion: Uniform Resource Locator
---

# Playwright Desktop + iPhone + Pixel

## Context

A desktop-only pass misses iOS wrapping and Android overflow.

## Topology

N/A — deploy

## Bind

Fill this table **before** any live change. Do **not** paste real values back into public notes.

| Placeholder | Operator fills | Class |
|-------------|----------------|-------|
| `<worker-root>` | Worker / UI source tree | Directory |

## Formulas

Run against preview default for marketing; production for gated apps.

## Method

Run Playwright Chromium device projects for Desktop, iPhone, and Pixel on nav/hero/CSS changes.

## Consequences

Fewer “works on my monitor” ships.

## Agent stop rule

> MUST emit the Playwright Desktop + iPhone + Pixel command with `<live-url>` or `<preview-url>` filled.
> MUST NOT skip the three-device gate after nav/hero/CSS changes.
> MUST NOT apply netfilter from this page.

## Procedure


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

## MUST NOT

- MUST NOT ship hero/nav CSS with desktop-only proof.
- MUST NOT require WebKit for this gate.
- MUST NOT publish hostnames, addresses, ULAs, or custom ports.

## Page changelog

- Edition 2 (8 Sep 2026, Mountain Time): Trap-specific Bind and agent stop rule (review cleanup).

## Related specs

- [OEN-10](../web/10-one-blocking-stylesheet-variable-fonts.md)
- [OEN-11](../web/11-worker-chat-wrapper-turnstile.md)

## Prior art (Not novel)

Responsive test matrices are standard. This note is the three Chromium device projects as the gate.

