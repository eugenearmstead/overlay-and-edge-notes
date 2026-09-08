---
id: OEN-S12
title: "Rocket Loader Off"
kind: supporting
status: active
edition: 1
date_published: 2026-09-08
author: Eugene Armstead
author_url: https://www.armsteadent.com/
canonical: https://eugenearmstead.github.io/overlay-and-edge-notes/supporting/s12-rocket-loader-off.html
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
backed_by: []
description: "Cloudflare Rocket Loader rewrites inline scripts and breaks analytics and Playwright smoke. Turn it Off on marketing and app routes."
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
  - abbr: nft
    expansion: nftables (Linux packet filter)
  - abbr: URL
    expansion: Uniform Resource Locator
  - abbr: UI
    expansion: user interface
  - abbr: Playwright
    expansion: browser automation and test runner
  - abbr: Wrangler
    expansion: Cloudflare Workers command-line tool
  - abbr: Cloudflare
    expansion: content delivery and Workers platform
  - abbr: Rocket
    expansion: Cloudflare Rocket Loader
  - abbr: DOM
    expansion: Document Object Model
---

# Rocket Loader Off

## Context

One page. Cites [OEN-09](../web/09-git-merge-is-not-a-live-worker.md) and [OEN-10](../web/10-one-blocking-stylesheet-variable-fonts.md).

## Topology

```text
Cloudflare Rocket Loader ON  -->  rewrites inline scripts
Breaks analytics and Playwright smoke
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

Rocket Loader Off. Do not debug Google Analytics or smoke for a rewrite.

## Consequences

Inline GA and smoke selectors match source.

## Agent stop rule

> A coding agent MUST emit a **bound runbook** (placeholders replaced from Bind).
> MUST NOT apply live `ip rule`, nft, iptables, ip6tables, sysctl, `wg set`, daemon restart, or deploy until a **human** filled Bind.
> MUST NOT claim a fix on ICMP ping alone when Verify names TCP, SSH, or HTTPS.
> MUST NOT file an upstream bug from this page.
> MUST NOT publish real addresses, hostnames, or custom ports.

## Procedure

Placeholders only until Bind is filled: `<cloud-vps>`, `<lan-pi>`, `<overlay-peer>`, `<exit-node>`, `<wg-iface>`, `<gcp-nic>`, plus the Bind extras on this page.

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
- ICMP / small ping success was **not** used as the pass criterion when this spec names TCP, SSH, or HTTPS.
- Bind table was filled by a human before any live `ip` / nft / iptables change.

## MUST NOT

- MUST NOT leave Rocket Loader On for pages with inline analytics/smoke.
- MUST NOT apply live network or firewall changes until Bind is filled by a human.
- MUST NOT claim a fix on ICMP ping alone when Verify names TCP, SSH, or HTTPS.
- MUST NOT publish hostnames, addresses, ULAs, or custom ports.

## Related specs

- [OEN-09](../web/09-git-merge-is-not-a-live-worker.md)
- [OEN-S04](s04-purge-cdn-after-deploy.md)

## Prior art (Not novel)

Cloudflare documents Rocket Loader. This note is Off as a contract for inline-script sites.

