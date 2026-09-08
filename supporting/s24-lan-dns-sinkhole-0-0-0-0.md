---
id: OEN-S24
title: "LAN DNS returning 0.0.0.0 is a sinkhole, not a site bug"
kind: supporting
status: active
edition: 1
date_published: 2026-09-08
author: Eugene Armstead
author_url: https://www.armsteadent.com/
canonical: https://eugenearmstead.github.io/overlay-and-edge-notes/supporting/s24-lan-dns-sinkhole-0-0-0-0.html
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
backed_by: []
description: "LAN dig returning 0.0.0.0 is a DNS sinkhole. Compare LAN dig vs DNS-over-HTTPS. Temporary /etc/hosts on the workstation only, operator-approved. Not a website bug."
terms:
  - abbr: OEN
    expansion: Overlay and Edge Notes
  - abbr: SSH
    expansion: Secure Shell
  - abbr: LAN
    expansion: Local Area Network
  - abbr: WAN
    expansion: Wide Area Network
  - abbr: TCP
    expansion: Transmission Control Protocol
  - abbr: MTU
    expansion: Maximum Transmission Unit
  - abbr: ICMP
    expansion: Internet Control Message Protocol
  - abbr: HTTPS
    expansion: Hypertext Transfer Protocol Secure
  - abbr: HTML
    expansion: HyperText Markup Language
  - abbr: CSS
    expansion: Cascading Style Sheets
  - abbr: IP
    expansion: Internet Protocol
  - abbr: WireGuard
    expansion: UDP-based VPN protocol
  - abbr: DNS
    expansion: Domain Name System
  - abbr: DoH
    expansion: DNS over HTTPS
  - abbr: nft
    expansion: nftables (Linux packet filter)
  - abbr: Pi
    expansion: single-board computer (Raspberry Pi class)
  - abbr: AAAA
    expansion: DNS IPv6 address record
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
| `<wg-iface>` | Consumer-router WireGuard client iface | Iface |
| `<lan-bridge>` | LAN bridge | Iface; MTU 1500 |
| `<wan-iface>` | WAN iface | Iface |
| `<lan-resolver>` | Intended LAN DNS | Address; never publish |


## Formulas

MUST NOT pin hosts on the origin Pi.

## Method

Compare LAN DNS vs DoH. Temporary hosts pin on the **workstation only** with operator approval. MUST NOT call it a site outage.

## Consequences

Analytics/tag hosts can be tested without blaming HTML.

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
- ICMP / small ping success was **not** used as the pass criterion when this spec names TCP, SSH, or HTTPS.
- Bind table was filled by a human before any live `ip` / nft / iptables change.

## MUST NOT

- MUST NOT treat 0.0.0.0 as a website bug.
- MUST NOT apply hosts pins without operator approval.
- MUST NOT pin on the origin server.
- MUST NOT apply live network or firewall changes until Bind is filled by a human.
- MUST NOT claim a fix on ICMP ping alone when Verify names TCP, SSH, or HTTPS.
- MUST NOT publish hostnames, addresses, ULAs, or custom ports.

## Related specs

- [OEN-03](../networking/03-router-vpn-dns-hijack.md)
- [OEN-10](../web/10-one-blocking-stylesheet-variable-fonts.md)

## Prior art (Not novel)

DNS sinkholes are known. This note is LAN 0.0.0.0 vs DoH plus workstation-only hosts.

