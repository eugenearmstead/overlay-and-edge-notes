---
id: "OEN-13"
title: "Overlay ≠ underlay ≠ tunnel unique-local ≠ LAN unique-local"
kind: "original"
status: "active"
edition: 2
date_published: "2026-09-08"
author: "Eugene Armstead"
author_url: "https://www.armsteadent.com/"
canonical: "https://eugenearmstead.github.io/overlay-and-edge-notes/networking/13-overlay-underlay-ula-layers.html"
keywords:
  - "overlay vs underlay vs ULA"
  - "tunnel ULA vs LAN ULA"
  - "bind overlay v4 and node ULA"
  - "do not bind WAN ::"
  - "prefixes.v6 backfillips"
  - "IPv6-only mesh not ops target"
  - "Tailscale ULA layers"
  - "Headscale unique-local"
  - "ssh overlay v4 rides WAN v6"
  - "HTTP overlay v6 brackets"
  - "four address layers"
  - "TS_DEBUG_MTU overlay IPv6"
backs:
  []
backed_by:
  - OEN-S30
  - OEN-S31
  - OEN-S26
description: "Four address layers get conflated: WAN global, overlay unique-local, commercial-tunnel addresses, and LAN unique-local. Bind overlay services to specific overlay v4 and node unique-local, not WAN ::."
terms:
  - abbr: CLI
    expansion: command-line interface
  - abbr: ControlPath
    expansion: OpenSSH multiplexing socket path option
  - abbr: GUA
    expansion: global unicast address (IPv6)
  - abbr: Happy-Eyeballs
    expansion: dual-stack connection racing (RFC 8305)
  - abbr: HTTP
    expansion: Hypertext Transfer Protocol
  - abbr: HTTPS
    expansion: Hypertext Transfer Protocol Secure
  - abbr: IPv4
    expansion: Internet Protocol version 4
  - abbr: IPv6
    expansion: Internet Protocol version 6
  - abbr: LAN
    expansion: Local Area Network
  - abbr: MTU
    expansion: Maximum Transmission Unit
  - abbr: OEN
    expansion: Overlay and Edge Notes
  - abbr: Pi
    expansion: single-board computer (Raspberry Pi class)
  - abbr: SSH
    expansion: Secure Shell
  - abbr: ULA
    expansion: unique-local address (IPv6)
  - abbr: VPS
    expansion: Virtual Private Server
  - abbr: WAN
    expansion: Wide Area Network
---

# Overlay ≠ underlay ≠ tunnel unique-local ≠ LAN unique-local

## Context

People treat “the IPv6 address” as one thing. There are four layers:

1. Host Wide Area Network (WAN) global unicast (GUA)
2. Overlay unique-local address (ULA) on the mesh
3. Commercial-tunnel addresses
4. Local Area Network (LAN) ULA

Secure Shell (SSH) to overlay IPv4 can ride WAN IPv6. SSH to overlay IPv6 can ride LAN IPv4. IPv6-only mesh is not a practical ops target.

`TS_DEBUG_MTU` below 1280 disables overlay IPv6 ([OEN-S30](../supporting/s30-ts-debug-mtu-below-1280.md)). Coordination `prefixes.v6` on **existing** nodes needs `nodes backfillips` (or equivalent); restart alone leaves `tailscale ip -6` empty ([OEN-S31](../supporting/s31-prefixes-v6-needs-backfillips.md)).

## Topology

```text
Layer 1  host WAN GUA
Layer 2  overlay ULA / overlay v4
Layer 3  commercial-tunnel addresses
Layer 4  LAN ULA

ssh to overlay v4 MAY ride WAN v6 underlay
ssh to overlay v6 MAY ride LAN v4 underlay
IPv6-only mesh is not a practical ops target
```

## Bind

Fill this table **before** any live change. Do **not** paste real values back into public notes.

| Placeholder | Operator fills | Class |
|-------------|----------------|-------|
| `<overlay-impl>` | Overlay implementation class | `tailscale-compatible` or other — stop and translate CLI |
| `<user>` | SSH user | Guest account |
| `<cloud-vps>` | Cloud VPS under test | Cloud VPS |
| `<lan-pi>` | Always-on LAN Pi | LAN Pi |

## Formulas

Existing nodes do not grow overlay IPv6 from a prefixes flag + restart alone ([OEN-S31](../supporting/s31-prefixes-v6-needs-backfillips.md)). `TS_DEBUG_MTU` < 1280 disables overlay IPv6 ([OEN-S30](../supporting/s30-ts-debug-mtu-below-1280.md)).

## Decision

Bind overlay services to **specific** overlay IPv4 **and** node ULA — not WAN `::`. Do **not** bind login HTTPS to overlay ULA if that address is missing at boot.

Default ops SSH stays on overlay IPv4. HTTP overlay IPv6 needs brackets. MUST NOT treat IPv6-only mesh as an ops goal.

## Consequences

- Services stay up when one layer is missing.
- Operators stop debugging “the VPS IPv6” when they meant overlay ULA.
- Existing nodes actually receive ULA after prefix enable.

## Agent stop rule

> MUST emit bound `ip addr` / overlay vs underlay / ULA checks after Bind is filled.
> This spec does not apply if `<overlay-impl>` is not tailscale-compatible when using overlay CLI.
> MUST NOT apply netfilter from this page.
> MUST NOT publish unique-local or public addresses.

## Procedure

This spec does not apply if `<overlay-impl>` is not tailscale-compatible.

### Copy-paste commands (after Bind)

```bash
ssh -o ControlPath=none <user>@<cloud-vps> 'ip -4 addr; ip -6 addr; ip -6 route | head'
# Bind overlay services to specific overlay v4 AND node ULA — not WAN ::
# Default ops SSH stays overlay v4. HTTP overlay v6 URLs need brackets.
```

1. **P1 — Name the four addresses on one node.**
   - **Action:** On `<cloud-vps>` and `<lan-pi>`, list WAN GUA, overlay IPv4, overlay IPv6/ULA, tunnel address, LAN ULA. Write a four-row table. No public paste of real values.
   - **Expected:** Four distinct scopes. Overlay v6 may be empty until backfill.
   - **On failure:** If overlay v6 is empty, do not bind services to it ([OEN-S31](../supporting/s31-prefixes-v6-needs-backfillips.md)).
2. **P2 — See that SSH overlay v4 may ride WAN v6.**
   - **Action:** `ssh` to the overlay IPv4 while watching underlay (`ss` / `tcpdump` on WAN vs LAN). Repeat to overlay IPv6 if present.
   - **Expected:** Underlay family need not match overlay family.
   - **On failure:** Do not “fix” this by forcing IPv6-only mesh.
3. **P3 — Bind explicitly.**
   - **Action:** Overlay listeners: specific overlay IPv4 and node ULA. Not `::` on WAN. HTTPS login MUST NOT target overlay ULA until `ip -6` shows it at boot.
   - **Expected:** Process listens where you documented. Boot does not take down login if ULA is late.
   - **On failure:** If ULA appears only after backfillips, sequence the bind after that.
4. **P4 — Do not drop overlay IPv6 with debug MTU.**
   - **Action:** If `TS_DEBUG_MTU` is set below 1280, remove or raise it ([OEN-S30](../supporting/s30-ts-debug-mtu-below-1280.md)).
   - **Expected:** `tailscale ip -6` can exist; kernel is not dropping v6 on the tun.
   - **On failure:** Do not use debug MTU as a production clamp.

## Expected samples

```text
# Overlay v6 empty after prefixes.v6 + restart only — need backfillips
```

## Verify

- Four-layer table exists in the private ops notes (not in this public spec).
- Login HTTPS is not bound to a missing overlay ULA.
- Ops SSH default is overlay IPv4.
- TS_DEBUG_MTU is not below 1280.

## MUST NOT

- MUST NOT publish real ULA, GUA, or overlay addresses.
- MUST NOT bind WAN `::` for overlay-only services.
- MUST NOT expect restart alone to backfill prefixes.v6.
- MUST NOT treat IPv6-only overlay as the daily control plane.
- MUST NOT publish hostnames, addresses, ULAs, or custom ports.

## Page changelog

- Edition 2 (8 Sep 2026, Mountain Time): Trap-specific Bind and agent stop rule (review cleanup).

## Related specs

- [OEN-20 LAN ULA Happy-Eyeballs leak](20-lan-ula-happy-eyeballs-leak.md)
- [OEN-S26 Wi-Fi vs cellular underlay](../supporting/s26-wifi-vs-cellular-underlay.md)
- [OEN-S30 TS_DEBUG_MTU below 1280](../supporting/s30-ts-debug-mtu-below-1280.md)
- [OEN-S31 prefixes.v6 needs backfillips](../supporting/s31-prefixes-v6-needs-backfillips.md)

