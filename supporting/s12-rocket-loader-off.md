---
id: "OEN-S12"
title: "Rocket Loader Off"
kind: "supporting"
status: "active"
edition: 2
date_published: "2026-09-08"
author: "Eugene Armstead"
author_url: "https://www.armsteadent.com/"
canonical: "https://eugenearmstead.github.io/overlay-and-edge-notes/supporting/s12-rocket-loader-off.html"
keywords:
  - "Rocket Loader Off"
  - "Cloudflare Rocket Loader inline scripts"
  - "Rocket Loader breaks analytics"
  - "Playwright smoke Rocket Loader"
  - "rewrites inline JavaScript"
  - "turn Rocket Loader Off"
  - "GA broken Rocket Loader"
  - "marketing route Rocket Loader"
  - "Cloudflare speed Rocket Loader"
  - "inline script rewrite"
  - "Workers HTML Rocket Loader"
  - "smoke test script missing"
backs:
  - OEN-09
  - OEN-10
backed_by:
  []
description: "Cloudflare Rocket Loader rewrites inline scripts and breaks analytics and Playwright smoke. Turn it Off on marketing and app routes."
terms:
  - abbr: Cloudflare
    expansion: content delivery and Workers platform
  - abbr: DOM
    expansion: Document Object Model
  - abbr: HTML
    expansion: HyperText Markup Language
  - abbr: HTTPS
    expansion: Hypertext Transfer Protocol Secure
  - abbr: OEN
    expansion: Overlay and Edge Notes
  - abbr: Playwright
    expansion: browser automation and test runner
  - abbr: URL
    expansion: Uniform Resource Locator
---

# Rocket Loader Off

## Context

One page. Cites [OEN-09](../web/09-git-merge-is-not-a-live-worker.md) and [OEN-10](../web/10-one-blocking-stylesheet-variable-fonts.md).

## Topology

N/A — deploy

## Bind

Fill this table **before** any live change. Do **not** paste real values back into public notes.

| Placeholder | Operator fills | Class |
|-------------|----------------|-------|
| `<live-url>` | Public HTTPS origin | URL |

## Method

Rocket Loader Off. Do not debug Google Analytics or smoke for a rewrite.

## Consequences

Inline GA and smoke selectors match source.

## Agent stop rule

> MUST confirm Rocket Loader is Off on the zone after Bind is filled.
> MUST NOT debug Google Analytics or smoke as a rewrite while Rocket Loader is On.
> MUST NOT apply netfilter from this page.

## Procedure


### Copy-paste commands (after Bind)

```text
# Dashboard: Rocket Loader Off for the zone used by <live-url>.
```

1. **P1 — Check the setting.**
   - **Action:** Zone/route Rocket Loader Off.
   - **Expected:** Dashboard shows Off.
   - **On failure:** On means this spec applies.
2. **P2 — View-source vs DOM.**
   - **Action:** If inline scripts were rewritten, turn Off and purge HTML ([OEN-S04](s04-purge-cdn-after-deploy.md)).
   - **Expected:** Source matches what tests expect.
   - **On failure:** Do not “fix” analytics IDs.
3. **P3 — Re-run smoke.**
   - **Action:** Playwright smoke after Off.
   - **Expected:** Pass.
   - **On failure:** A remaining fail is real.

## Expected samples

```text
# view-source no data-cfasync rocket loader wrapper around first-party analytics
```

## Verify

- Rocket Loader Off.
- Smoke matches view-source.

## MUST NOT

- MUST NOT leave Rocket Loader On for pages with inline analytics/smoke.
- MUST NOT publish hostnames, addresses, ULAs, or custom ports.

## Page changelog

- Edition 2 (8 Sep 2026, Mountain Time): Trap-specific Bind and agent stop rule (review cleanup).

## Related specs

- [OEN-09](../web/09-git-merge-is-not-a-live-worker.md)
- [OEN-S04](s04-purge-cdn-after-deploy.md)

