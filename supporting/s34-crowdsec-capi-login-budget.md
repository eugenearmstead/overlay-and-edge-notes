---
id: OEN-S34
title: "CrowdSec free-tier Central API login budget"
kind: supporting
status: active
edition: 1
date_published: 2026-09-08
author: Eugene Armstead
author_url: https://www.armsteadent.com/
canonical: https://eugenearmstead.github.io/overlay-and-edge-notes/supporting/s34-crowdsec-capi-login-budget.html
keywords:
  - crowdsec
  - capi
  - rate-limit
backs:
  - OEN-07
backed_by: []
description: "CrowdSec free-tier about 20 CAPI logins per 50 minutes per source IP yields HTTP 403 for about an hour. Cache cscli capi status; do not loop it."
terms:
  - abbr: OEN
    expansion: Overlay and Edge Notes
  - abbr: SSH
    expansion: Secure Shell
  - abbr: VPS
    expansion: Virtual Private Server
  - abbr: LAN
    expansion: Local Area Network
  - abbr: WAN
    expansion: Wide Area Network
  - abbr: TCP
    expansion: Transmission Control Protocol
  - abbr: MSS
    expansion: Maximum Segment Size
  - abbr: MTU
    expansion: Maximum Transmission Unit
  - abbr: ICMP
    expansion: Internet Control Message Protocol
  - abbr: HTTP
    expansion: Hypertext Transfer Protocol
  - abbr: HTTPS
    expansion: Hypertext Transfer Protocol Secure
  - abbr: IP
    expansion: Internet Protocol
  - abbr: IPv4
    expansion: Internet Protocol version 4
  - abbr: IPv6
    expansion: Internet Protocol version 6
  - abbr: WireGuard
    expansion: UDP-based VPN protocol
  - abbr: API
    expansion: application programming interface
  - abbr: CAPI
    expansion: CrowdSec Central API
  - abbr: nft
    expansion: nftables (Linux packet filter)
  - abbr: Pi
    expansion: single-board computer (Raspberry Pi class)
  - abbr: systemd
    expansion: Linux service manager
  - abbr: CrowdSec
    expansion: open-source IDS/IPS with a Central API
  - abbr: SLI
    expansion: service level indicator
  - abbr: POST
    expansion: HTTP method
---

# CrowdSec free-tier Central API login budget

## Context

Method behind [OEN-07](../networking/07-crowdsec-capi-403.md). Docker healthchecks are documented; native systemd+collector is the unique stack.

## Topology

```text
~20 CAPI logins / 50 min / source IP  -->  HTTP 403 ~1 h
Cache cscli capi status; dummy POST for 401 vs 403
```

## Bind

Fill this table **before** any live change. Do **not** paste real values back into public notes.

| Placeholder | Operator fills | Class |
|-------------|----------------|-------|
| `<cloud-vps>` | Overlay SSH target | Cloud VPS |
| `<lan-pi>` | Overlay SSH target | LAN Pi |
| `<user>` | SSH user | Guest account |
| `<wg-iface>` | Commercial WireGuard iface | Router or VPS client |
| `<wan-iface>` | WAN iface | Router |
| `<lan-bridge>` | LAN bridge | Router (MTU 1500) |
| `<overlay-tun>` | Overlay tun iface | Node under test |
| `<wg-mtu>` | MTU integer from `ip link` | Measured |
| `<mss4>` / `<mss6>` | Computed MSS | Formulas |
| `<vps-public-v4>` / `<vps-public-v6>` | VPS public addresses | WAN; never publish |
| `<overlay-v4>` / `<overlay-v6>` | Overlay addresses | Overlay; never publish |


## Formulas

Backs [OEN-07](../networking/07-crowdsec-capi-403.md).

## Method

Cache CAPI status. Nested SLI probes MUST skip live cscli. Dummy enroll POST for 401 vs 403 without more logins.

## Consequences

The VPS IPv4 can cool down. IPv6 may still be 401.

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
curl -4 -sS -o /dev/null -w '%{http_code}\n' --max-time 15 -X POST https://api.crowdsec.net/v2/watchers
curl -6 -sS -o /dev/null -w '%{http_code}\n' --max-time 15 -X POST https://api.crowdsec.net/v2/watchers
```

1. **P1 — Stop the loop.**
   - **Action:** Disable repeating cscli capi status.
   - **Expected:** No further logins this window.
   - **On failure:** Retries keep the 403.
2. **P2 — Dummy POST matrix.**
   - **Action:** Unauthenticated enroll POST v4 vs v6 ([OEN-07](../networking/07-crowdsec-capi-403.md)).
   - **Expected:** 401 vs 403 per family.
   - **On failure:** No credentials.
3. **P3 — Cache.**
   - **Action:** Health reads cache or logs. Far below ~20/50 min.
   - **Expected:** Collector quiet.
   - **On failure:** One cscli after hosts unpin if needed.

## Expected samples

```text
403
401
```

## Verify

- No looping cscli.
- Budget respected.
- Dummy matrix used instead of more logins.
- ICMP / small ping success was **not** used as the pass criterion when this spec names TCP, SSH, or HTTPS.
- Bind table was filled by a human before any live `ip` / nft / iptables change.

## MUST NOT

- MUST NOT loop cscli capi status.
- MUST NOT publish VPS IPs.
- MUST NOT apply live network or firewall changes until Bind is filled by a human.
- MUST NOT claim a fix on ICMP ping alone when Verify names TCP, SSH, or HTTPS.
- MUST NOT publish hostnames, addresses, ULAs, or custom ports.

## Related specs

- [OEN-07](../networking/07-crowdsec-capi-403.md)

## Prior art (Not novel)

CrowdSec documents the free-tier login budget. This note is cache-and-dummy-POST as the native-host contract.

