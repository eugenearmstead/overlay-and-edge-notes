---
id: OEN-S20
title: "SSH TCP-open with no banner is userspace-sick"
kind: supporting
status: active
edition: 1
date_published: 2026-09-08
author: Eugene Armstead
author_url: https://www.armsteadent.com/
canonical: https://eugenearmstead.github.io/overlay-and-edge-notes/supporting/s20-ssh-open-no-banner.html
keywords:
  - "SSH TCP-open with no banner"
  - "nmap open userspace sick"
  - "Dropbear no banner"
  - "consumer router SSH banner missing"
  - "reboot restores banner PeerAPI"
  - "TCP open not enough"
  - "ASUSWRT-Merlin SSH hung"
  - "overlay SSH no ident"
  - "userspace SSH sick"
  - "PeerAPI down with banner"
  - "router SSH probe banner"
  - "nmap open filtered SSH"
backs:
  - OEN-12
  - OEN-14
backed_by: []
description: "Overlay SSH TCP-open with no banner means userspace on the router is sick. nmap open is not enough. Reboot restores banner and PeerAPI together."
terms:
  - abbr: OEN
    expansion: Overlay and Edge Notes
  - abbr: SSH
    expansion: Secure Shell
  - abbr: OpenSSH
    expansion: OpenBSD Secure Shell
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
  - abbr: WireGuard
    expansion: UDP-based VPN protocol
  - abbr: DNS
    expansion: Domain Name System
  - abbr: PeerAPI
    expansion: overlay peer application-programming interface (exit DNS over HTTPS)
  - abbr: nft
    expansion: nftables (Linux packet filter)
  - abbr: FORWARD
    expansion: netfilter/iptables forward chain
  - abbr: ControlPath
    expansion: OpenSSH multiplexing socket path option
---

# SSH TCP-open with no banner is userspace-sick

## Context

nmap `open` on overlay :22 with no SSH banner: Dropbear/userspace wedged. PeerAPI often dies with it.

## Topology

```text
nmap :22 open  but  no SSH banner  -->  router userspace sick
PeerAPI often dead together
Reboot restores banner + PeerAPI
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

TCP open is not SSH healthy. MUST NOT publish custom SSH ports.

## Method

Do not treat nmap open as SSH-up. Reboot restores banner + PeerAPI. Then continue [OEN-12](../networking/12-consumer-wg-phantom-bridge.md) / [OEN-14](../networking/14-exit-dns-is-peerapi.md).

## Consequences

Operators stop waiting on a banner that will never come until reboot.

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
ssh -o ControlPath=none -o ConnectTimeout=8 <user>@<router-overlay> 'echo banner-ok'
# If TCP connects and no banner, do not debug DNS yaml first.
```

1. **P1 — Banner vs port.**
   - **Action:** nc/ssh with timeout vs nmap. Port open, no banner.
   - **Expected:** Userspace sick.
   - **On failure:** Do not raise timeout to minutes.
2. **P2 — PeerAPI together.**
   - **Action:** PeerAPIURL fetch fails on that node too.
   - **Expected:** Reboot restores both.
   - **On failure:** Do not debug DNS yaml first.
3. **P3 — After reboot.**
   - **Action:** Banner returns. Continue FORWARD/DNS specs if LAN still dead.
   - **Expected:** SSH usable.
   - **On failure:** Changelog the reboot ([OEN-18](../networking/18-per-node-changelog-contract.md)).

## Expected samples

```text
# hang after TCP connect, no OpenSSH_ banner
```

## Verify

- Banner present after recovery.
- nmap open was not trusted alone.
- ICMP / small ping success was **not** used as the pass criterion when this spec names TCP, SSH, or HTTPS.
- Bind table was filled by a human before any live `ip` / nft / iptables change.

## MUST NOT

- MUST NOT treat nmap open as SSH healthy.
- MUST NOT publish custom SSH ports.
- MUST NOT apply live network or firewall changes until Bind is filled by a human.
- MUST NOT claim a fix on ICMP ping alone when Verify names TCP, SSH, or HTTPS.
- MUST NOT publish hostnames, addresses, ULAs, or custom ports.

## Related specs

- [OEN-12](../networking/12-consumer-wg-phantom-bridge.md)
- [OEN-14](../networking/14-exit-dns-is-peerapi.md)

## Prior art (Not novel)

TCP open vs application banner is textbook. This note is router userspace + PeerAPI dying together.

