---
id: "OEN-S24"
title: "LAN DNS returning 0.0.0.0 is a sinkhole, not a site bug"
kind: "supporting"
status: "active"
edition: 2
date_published: "2026-09-08"
author: "Eugene Armstead"
author_url: "https://www.armsteadent.com/"
canonical: "https://eugenearmstead.github.io/overlay-and-edge-notes/supporting/s24-lan-dns-sinkhole-0-0-0-0.html"
keywords:
  - "LAN DNS 0.0.0.0 sinkhole"
  - "ERR_CONNECTION_REFUSED 0.0.0.0"
  - "DNS sinkhole not a site bug"
  - "LAN dig vs DNS-over-HTTPS"
  - "temporary /etc/hosts workstation"
  - "googletagmanager 0.0.0.0"
  - "Pi-hole style sinkhole"
  - "operator-approved hosts pin"
  - "blackhole DNS LAN"
  - "compare DoH vs LAN resolver"
  - "analytics curl connection refused"
  - "not a Cloudflare bug sinkhole"
backs:
  - OEN-03
  - OEN-10
backed_by:
  []
description: "LAN dig returning 0.0.0.0 is a DNS sinkhole. Compare LAN dig vs DNS-over-HTTPS. Temporary /etc/hosts on the workstation only, operator-approved. Not a website bug."
terms:
  - abbr: AAAA
    expansion: DNS IPv6 address record
  - abbr: CSS
    expansion: Cascading Style Sheets
  - abbr: DNS
    expansion: Domain Name System
  - abbr: DoH
    expansion: DNS over HTTPS
  - abbr: HTML
    expansion: HyperText Markup Language
  - abbr: HTTPS
    expansion: Hypertext Transfer Protocol Secure
  - abbr: IP
    expansion: Internet Protocol
  - abbr: LAN
    expansion: Local Area Network
  - abbr: OEN
    expansion: Overlay and Edge Notes
  - abbr: Pi
    expansion: single-board computer (Raspberry Pi class)
---

# LAN DNS returning 0.0.0.0 is a sinkhole, not a site bug

## Context

Browsers show connection refused to 0.0.0.0. Marketing sites look “down.” LAN resolver blackholed the name.

## Topology

```text
LAN dig --> 0.0.0.0   sinkhole
DoH --> real A/AAAA
Temporary /etc/hosts on the **workstation only**, operator-approved
Not a website bug ([OEN-10](../web/10-one-blocking-stylesheet-variable-fonts.md))
```

## Bind

Fill this table **before** any live change. Do **not** paste real values back into public notes.

| Placeholder | Operator fills | Class |
|-------------|----------------|-------|
| `<lan-resolver>` | LAN DNS resolver the client uses | Address; never publish |
| `<name>` | Name the sinkhole returns 0.0.0.0 for | Hostname class |

## Formulas

MUST NOT pin hosts on the origin Pi.

## Method

Compare LAN DNS vs DoH. Temporary hosts pin on the **workstation only** with operator approval. MUST NOT call it a site outage.

## Consequences

Analytics/tag hosts can be tested without blaming HTML.

## Agent stop rule

> MUST compare LAN DNS vs DNS-over-HTTPS after `<lan-resolver>` is filled.
> MUST NOT pin `/etc/hosts` on the origin Pi.
> MUST NOT call a 0.0.0.0 sinkhole a site outage.
> MUST NOT apply netfilter from this page.

## Procedure


### Copy-paste commands (after Bind)

```bash
dig +short @<lan-resolver> <name>
# Compare DoH. If LAN is 0.0.0.0 and DoH is a unicast, this spec.
```

1. **P1 — LAN vs DoH.**
   - **Action:** `dig` on LAN vs DNS-over-HTTPS for the failing name.
   - **Expected:** LAN 0.0.0.0; DoH a real address — sinkhole.
   - **On failure:** If both fail, the name is elsewhere.
2. **P2 — Workstation hosts only.**
   - **Action:** If testing requires it, operator-approved /etc/hosts on the workstation. Never on the origin Pi.
   - **Expected:** Browser reaches the real IP.
   - **On failure:** Remove when done.
3. **P3 — Not OEN-10.**
   - **Action:** Do not rewrite CSS because googletagmanager “failed.”
   - **Expected:** Site HTML is fine.
   - **On failure:** Related [OEN-03](../networking/03-router-vpn-dns-hijack.md) if :53 is hijacked.

## Expected samples

```text
0.0.0.0
```

## Verify

- Sinkhole identified via LAN vs DoH.
- No site-code “fix” for 0.0.0.0.

## MUST NOT

- MUST NOT treat 0.0.0.0 as a website bug.
- MUST NOT apply hosts pins without operator approval.
- MUST NOT pin on the origin server.
- MUST NOT publish hostnames, addresses, ULAs, or custom ports.

## Page changelog

- Edition 2 (8 Sep 2026, Mountain Time): Trap-specific Bind and agent stop rule (review cleanup).

## Related specs

- [OEN-03](../networking/03-router-vpn-dns-hijack.md)
- [OEN-10](../web/10-one-blocking-stylesheet-variable-fonts.md)

## Prior art (Not novel)

DNS sinkholes are known. This note is LAN 0.0.0.0 vs DoH plus workstation-only hosts.

