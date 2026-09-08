---
id: OEN-S29
title: "Overlay peer-API stub event-loop blocks; UDP receive queue grows"
kind: supporting
status: active
edition: 1
date_published: 2026-09-08
author: Eugene Armstead
author_url: https://www.armsteadent.com/
canonical: https://eugenearmstead.github.io/overlay-and-edge-notes/supporting/s29-peerapi-stub-event-loop.html
keywords:
  - "PeerAPI stub event-loop blocks"
  - "UDP recv-Q grows"
  - "select() sync upstream DNS"
  - "cellular DNS dies stub"
  - "thread pool PeerAPI stub"
  - "upstream timeout stub"
  - "single-threaded DoH stub"
  - "recv-Q 160KB DNS"
  - "exit stub event loop"
  - "Android exit DNS timeout"
  - "PeerAPI UDP queue"
  - "do not block select DNS"
backs:
  - OEN-05
  - OEN-19
backed_by: []
description: "Synchronous upstream inside select() fills UDP recv-Q; cellular DNS dies. Thread pool plus timeouts."
terms:
  - abbr: OEN
    expansion: Overlay and Edge Notes
  - abbr: SSH
    expansion: Secure Shell
  - abbr: LAN
    expansion: Local Area Network
  - abbr: WAN
    expansion: Wide Area Network
  - abbr: KB
    expansion: kilobyte
  - abbr: TCP
    expansion: Transmission Control Protocol
  - abbr: UDP
    expansion: User Datagram Protocol
  - abbr: MTU
    expansion: Maximum Transmission Unit
  - abbr: ICMP
    expansion: Internet Control Message Protocol
  - abbr: HTTPS
    expansion: Hypertext Transfer Protocol Secure
  - abbr: DNS
    expansion: Domain Name System
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
  - abbr: nft
    expansion: nftables (Linux packet filter)
  - abbr: ControlPath
    expansion: OpenSSH multiplexing socket path option
  - abbr: Pi
    expansion: single-board computer (Raspberry Pi class)
---

# Overlay peer-API stub event-loop blocks; UDP receive queue grows

## Context

Backs [OEN-05](../networking/05-exit-peerapi-dns-stub.md). ~160 KB recv-Q under phone load in the field.

## Topology

```text
PeerAPI stub select() + sync upstream  -->  UDP recv-Q grows (~160 KB field)
cellular DNS dies
Thread pool + upstream timeout; still bind 127.0.0.1 only
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

MUST NOT sync-resolve inside select().

## Method

MUST NOT call upstream synchronously in the select loop. Thread pool + upstream timeout.

## Consequences

Cellular DNS survives bursts.

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
ssh -o ControlPath=none <user>@<exit-node> 'ss -u -n | awk "NR==1 || /:53/"'
```

1. **P1 — Watch recv-Q.**
   - **Action:** During phone soak, `ss -u` recv-Q on the stub.
   - **Expected:** Growing queue = blocked loop.
   - **On failure:** If queue stays 0, this spec does not apply.
2. **P2 — Thread pool + timeout.**
   - **Action:** Move upstream I/O off the event loop. Timeout the forward.
   - **Expected:** recv-Q stays low. Cellular DNS lives.
   - **On failure:** Do not add more inline handlers.
3. **P3 — Loopback only still.**
   - **Action:** Bind remains 127.0.0.1 ([OEN-05](../networking/05-exit-peerapi-dns-stub.md)).
   - **Expected:** Exit still works.
   - **On failure:** Do not bind overlay :53 to “help load.”

## Expected samples

```text
# Recv-Q climbing under phone soak
```

## Verify

- recv-Q near 0 under load.
- Thread pool present.
- ICMP / small ping success was **not** used as the pass criterion when this spec names TCP, SSH, or HTTPS.
- Bind table was filled by a human before any live `ip` / nft / iptables change.

## MUST NOT

- MUST NOT sync-resolve inside select().
- MUST NOT bind overlay :53.
- MUST NOT apply live network or firewall changes until Bind is filled by a human.
- MUST NOT claim a fix on ICMP ping alone when Verify names TCP, SSH, or HTTPS.
- MUST NOT publish hostnames, addresses, ULAs, or custom ports.

## Related specs

- [OEN-05](../networking/05-exit-peerapi-dns-stub.md)

## Prior art (Not novel)

Event-loop blocking is textbook. This note is PeerAPI stub + cellular DNS + recv-Q.

