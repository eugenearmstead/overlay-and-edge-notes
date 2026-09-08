---
id: OEN-S25
title: "Network Time Security chrony address-family flags need a newer chrony than the distro"
kind: supporting
status: active
edition: 1
date_published: 2026-09-08
author: Eugene Armstead
author_url: https://www.armsteadent.com/
canonical: https://eugenearmstead.github.io/overlay-and-edge-notes/supporting/s25-chrony-nts-address-family.html
keywords:
  - "chrony NTS ipv6 flag distro"
  - "distro chrony parse NTS flags"
  - "Cloudflare NTS newer chrony"
  - "try v6 then v4 NTS"
  - "Network Time Security chrony"
  - "NTS address-family flags"
  - "VPS host time NTS"
  - "chrony ipv6 server option"
  - "upgrade chrony NTS"
  - "NTS handshake family"
  - "coordinator chrony NTS"
  - "time sync NTS Cloudflare"
backs:
  - OEN-15
backed_by: []
description: "Distro chrony may not parse NTS ipv6/ipv4 server flags. Use a newer chrony plus Cloudflare NTS; try v6 then v4."
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
  - abbr: HTTPS
    expansion: Hypertext Transfer Protocol Secure
  - abbr: IPv4
    expansion: Internet Protocol version 4
  - abbr: IPv6
    expansion: Internet Protocol version 6
  - abbr: WireGuard
    expansion: UDP-based VPN protocol
  - abbr: DNS
    expansion: Domain Name System
  - abbr: PeerAPI
    expansion: overlay peer application-programming interface (exit DNS over HTTPS)
  - abbr: nft
    expansion: nftables (Linux packet filter)
  - abbr: ControlPath
    expansion: OpenSSH multiplexing socket path option
  - abbr: NTS
    expansion: Network Time Security
  - abbr: Pi
    expansion: single-board computer (Raspberry Pi class)
  - abbr: Cloudflare
    expansion: content delivery and Workers platform
  - abbr: chrony
    expansion: NTP/NTS time daemon
  - abbr: NTP
    expansion: Network Time Protocol
---

# Network Time Security chrony address-family flags need a newer chrony than the distro

## Context

Backs [OEN-15](../networking/15-split-host-vs-overlay-resolver.md) host stack on the VPS. Distro chrony rejects `ipv6`/`ipv4` NTS server flags.

## Topology

```text
Distro chrony rejects NTS server ipv6/ipv4 flags
Newer chrony + Cloudflare NTS; try v6 then v4
Host time MUST NOT depend on the commercial tunnel
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

Upgrade chrony; do not comment out NTS to make it start.

## Method

Install a chrony new enough to parse address-family flags. Try NTS over IPv6 then IPv4. Host time MUST NOT depend on the commercial tunnel.

## Consequences

NTS works. Distro package is not blamed forever.

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
ssh -o ControlPath=none <user>@<cloud-vps> 'chronyd --version; chronyc sources || true'
```

1. **P1 — chrony version.**
   - **Action:** `chronyd --version`. If NTS server lines with ipv6/ipv4 fail to parse, the distro is too old.
   - **Expected:** Need newer chrony.
   - **On failure:** Do not comment out NTS “to make it start.”
2. **P2 — v6 then v4.**
   - **Action:** Cloudflare NTS (or equivalent): try IPv6 then IPv4.
   - **Expected:** chronyc sources shows NTS.
   - **On failure:** Host view still works with tunnel down ([OEN-15](../networking/15-split-host-vs-overlay-resolver.md)).
3. **P3 — Not overlay DNS.**
   - **Action:** Time is host stack, not PeerAPI.
   - **Expected:** NTP/NTS independent of exit DNS.
   - **On failure:** Do not restart coordination for time.

## Expected samples

```text
# old: invalid directive ipv6
```

## Verify

- NTS selected in chronyc.
- Tunnel-down host still steps time or at least still resolves.
- ICMP / small ping success was **not** used as the pass criterion when this spec names TCP, SSH, or HTTPS.
- Bind table was filled by a human before any live `ip` / nft / iptables change.

## MUST NOT

- MUST NOT drop NTS because the distro binary cannot parse flags — upgrade chrony.
- MUST NOT pin time to the tunnel.
- MUST NOT apply live network or firewall changes until Bind is filled by a human.
- MUST NOT claim a fix on ICMP ping alone when Verify names TCP, SSH, or HTTPS.
- MUST NOT publish hostnames, addresses, ULAs, or custom ports.

## Related specs

- [OEN-15](../networking/15-split-host-vs-overlay-resolver.md)

## Prior art (Not novel)

NTS is documented. This note is distro chrony rejecting address-family flags.

