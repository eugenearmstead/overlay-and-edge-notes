---
id: OEN-S14
title: "Broadcom in-kernel WireGuard SUnreclaim (flow-cache/runner A/B fail)"
kind: supporting
status: active
edition: 1
date_published: 2026-09-08
author: Eugene Armstead
author_url: https://www.armsteadent.com/
canonical: https://eugenearmstead.github.io/overlay-and-edge-notes/supporting/s14-broadcom-wg-sunreclaim.html
keywords:
  - wireguard
  - sunreclaim
  - broadcom
backs:
  - OEN-12
backed_by: []
description: "In-kernel WireGuard on a Broadcom consumer router leaked about 6–8 MB/h of SUnreclaim. drop_caches did not free it. Flow-cache off and runner off A/Bs were negative."
terms:
  - abbr: OEN
    expansion: Overlay and Edge Notes
  - abbr: SSH
    expansion: Secure Shell
  - abbr: LAN
    expansion: Local Area Network
  - abbr: WAN
    expansion: Wide Area Network
  - abbr: VPN
    expansion: Virtual Private Network
  - abbr: MB
    expansion: megabyte
  - abbr: TCP
    expansion: Transmission Control Protocol
  - abbr: MTU
    expansion: Maximum Transmission Unit
  - abbr: ICMP
    expansion: Internet Control Message Protocol
  - abbr: HTTPS
    expansion: Hypertext Transfer Protocol Secure
  - abbr: IPv4
    expansion: Internet Protocol version 4
  - abbr: IPv6
    expansion: Internet Protocol version 6
  - abbr: WG
    expansion: WireGuard
  - abbr: WireGuard
    expansion: UDP-based VPN protocol
  - abbr: DNS
    expansion: Domain Name System
  - abbr: nft
    expansion: nftables (Linux packet filter)
  - abbr: FC
    expansion: flow-cache (Broadcom hardware forwarding cache)
---

# Broadcom in-kernel WireGuard SUnreclaim (flow-cache/runner A/B fail)

## Context

Scheduled reboot is an ops workaround, not a root-cause fix. Skip tables that list IPv4 ports while the tunnel underlay is IPv6 do not help. Scrubbed measurements only.

## Topology

```text
Broadcom in-kernel WireGuard  -->  SUnreclaim / skbuff slope ~6-8 MB/h
drop_caches does not free it
flow-cache off / runner off A/B were negative
Scheduled reboot is ops workaround, not root cause
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

Skip tables that list IPv4 ports while underlay is IPv6 do not help. Scrubbed measurements only.

## Method

Record the slope. Do not claim flow-cache or runner off as the fix after negative A/B. MUST NOT file a public firmware thread this round.

## Consequences

Operators plan reboot windows honestly. They stop toggling FC/runner as if it were proven.

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
# On the router after Bind:
grep -E 'SUnreclaim|MemFree' /proc/meminfo
```

1. **P1 — Measure SUnreclaim slope.**
   - **Action:** Sample /proc/meminfo SUnreclaim over hours while the in-kernel WG client is up.
   - **Expected:** ~6–8 MB/h class slope (order of magnitude).
   - **On failure:** If slope is zero, this spec does not apply.
2. **P2 — drop_caches does not free it.**
   - **Action:** `echo 3 > /proc/sys/vm/drop_caches` (know this is disruptive). SUnreclaim stays.
   - **Expected:** Not page cache.
   - **On failure:** Do not loop drop_caches.
3. **P3 — Negative A/B.**
   - **Action:** Flow-cache off and runner off did not stop the slope. IPv4 skip tables with IPv6 underlay did not help.
   - **Expected:** Do not keep those as “the fix.”
   - **On failure:** Reboot remains an ops workaround.

## Expected samples

```text
SUnreclaim:   climbing across hours
```

## Verify

- Slope documented without hostnames.
- FC/runner not claimed as fix.
- ICMP / small ping success was **not** used as the pass criterion when this spec names TCP, SSH, or HTTPS.
- Bind table was filled by a human before any live `ip` / nft / iptables change.

## MUST NOT

- MUST NOT open a public firmware thread from this note.
- MUST NOT publish serials or full syslog.
- MUST NOT name the commercial VPN.
- MUST NOT apply live network or firewall changes until Bind is filled by a human.
- MUST NOT claim a fix on ICMP ping alone when Verify names TCP, SSH, or HTTPS.
- MUST NOT publish hostnames, addresses, ULAs, or custom ports.

## Related specs

- [OEN-12](../networking/12-consumer-wg-phantom-bridge.md)

## Prior art (Not novel)

skbuff leaks are discussed in firmware circles. This note is the measured slope plus failed A/Bs without a public thread.

