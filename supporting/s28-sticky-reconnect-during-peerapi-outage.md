---
id: OEN-S28
title: "Reconnect during overlay peer-API outage sticks after heal"
kind: supporting
status: active
edition: 1
date_published: 2026-09-08
author: Eugene Armstead
author_url: https://www.armsteadent.com/
canonical: https://eugenearmstead.github.io/overlay-and-edge-notes/supporting/s28-sticky-reconnect-during-peerapi-outage.html
keywords:
  - peerapi
  - android
  - reconnect
backs:
  - OEN-14
  - OEN-19
backed_by: []
description: "Phones that rejoin while DoH is dead stay stuck after PeerAPI recovers until that client toggles. Heal the exit stub, not coordinator DNS yaml. Empty use_with_exit_node does not open PeerAPI."
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
  - abbr: DNS
    expansion: Domain Name System
  - abbr: DoH
    expansion: DNS over HTTPS
  - abbr: GCP
    expansion: Google Cloud Platform
  - abbr: VM
    expansion: virtual machine
  - abbr: NIC
    expansion: network interface card
  - abbr: API
    expansion: application programming interface
  - abbr: PeerAPI
    expansion: overlay peer application-programming interface (exit DNS over HTTPS)
  - abbr: RD
    expansion: Recursion Desired (DNS flag)
  - abbr: nft
    expansion: nftables (Linux packet filter)
  - abbr: Pi
    expansion: single-board computer (Raspberry Pi class)
---

# Reconnect during overlay peer-API outage sticks after heal

## Context

Backs [OEN-14](../networking/14-exit-dns-is-peerapi.md). Sticky client after outage.

## Topology

```text
Phone reconnects while PeerAPI DoH is dead
PeerAPI heals  -->  that phone stays stuck until client toggle
Heal exit stub, not coordinator DNS yaml
```

## Bind

Fill this table **before** any live change. Do **not** paste real values back into public notes.

| Placeholder | Operator fills | Class |
|-------------|----------------|-------|
| `<exit-node>` | Overlay exit node | Cloud VM or LAN Pi used as exit |
| `<overlay-peer>` | Soak client (**not** the agent workstation) | LAN Pi |
| `<user>` | SSH user | Guest |
| `<overlay-tun>` | Overlay tun on the exit | Iface |
| `<gcp-nic>` | Public NIC on a Google Cloud guest | Iface; omit on non-GCP exits |
| `<wan-iface>` | WAN / public NIC | Iface |
| `<mss4>` / `<mss6>` | Computed from underlay or overlay tun MTU | Formulas |


## Formulas

Empty use_with_exit_node does not open PeerAPI.

## Method

Heal PeerAPI on the exit. Toggle the stuck client. MUST NOT rewrite coordinator DNS yaml (fleet reconnect).

## Consequences

New clients work; stuck phones need a toggle, not a coordinator bounce.

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
# After stub heal: new client works. Stuck phone: exit off/on or app toggle.
```

1. **P1 — Heal exit DoH.**
   - **Action:** Fix stub/RD ([OEN-05](../networking/05-exit-peerapi-dns-stub.md), [OEN-19](../networking/19-unbound-refuses-rd0.md)). New client works.
   - **Expected:** PeerAPI up.
   - **On failure:** Do not touch coordinator yaml.
2. **P2 — Toggle stuck phones.**
   - **Action:** Phones that reconnected during the outage stay dead until exit off/on or app toggle.
   - **Expected:** They recover after toggle.
   - **On failure:** Do not restart coordination for them.
3. **P3 — Empty use_with_exit_node.**
   - **Action:** That flag does not open PeerAPI.
   - **Expected:** Do not set it as a heal.
   - **On failure:** Local DNS on exit still needs the stub.

## Expected samples

```text
# new client DoH 200; sticky phone still DNS_PROBE until toggle
```

## Verify

- New client DoH works after heal.
- Stuck client documented as toggle, not yaml.
- ICMP / small ping success was **not** used as the pass criterion when this spec names TCP, SSH, or HTTPS.
- Bind table was filled by a human before any live `ip` / nft / iptables change.

## MUST NOT

- MUST NOT change coordinator DNS yaml to heal PeerAPI.
- MUST NOT expect empty use_with_exit_node to open PeerAPI.
- MUST NOT apply live network or firewall changes until Bind is filled by a human.
- MUST NOT claim a fix on ICMP ping alone when Verify names TCP, SSH, or HTTPS.
- MUST NOT publish hostnames, addresses, ULAs, or custom ports.

## Related specs

- [OEN-14](../networking/14-exit-dns-is-peerapi.md)
- [OEN-05](../networking/05-exit-peerapi-dns-stub.md)

## Prior art (Not novel)

Sticky DNS caches are known. This note is reconnect-during-PeerAPI-outage staying stuck after heal.

