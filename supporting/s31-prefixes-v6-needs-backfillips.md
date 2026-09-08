---
id: OEN-S31
title: "prefixes.v6 needs nodes backfillips, not restart alone"
kind: supporting
status: active
edition: 1
date_published: 2026-09-08
author: Eugene Armstead
author_url: https://www.armsteadent.com/
canonical: https://eugenearmstead.github.io/overlay-and-edge-notes/supporting/s31-prefixes-v6-needs-backfillips.html
keywords:
  - "prefixes.v6 needs backfillips"
  - "nodes backfillips --force"
  - "restart alone tailscale ip -6 empty"
  - "Headscale prefixes.v6 existing nodes"
  - "ULA missing after enable v6"
  - "backfillips then restart"
  - "tailscale ip -6 empty"
  - "self-hosted coordination ULA"
  - "existing nodes no IPv6"
  - "prefixes.v6 rollout"
  - "Headscale backfillips"
  - "enable IPv6 overlay nodes"
backs:
  - OEN-13
backed_by: []
description: "Enabling prefixes.v6 on existing nodes needs nodes backfillips --force then restart. Restart alone leaves tailscale ip -6 empty."
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
  - abbr: IPv6
    expansion: Internet Protocol version 6
  - abbr: WireGuard
    expansion: UDP-based VPN protocol
  - abbr: ULA
    expansion: unique-local address (IPv6)
  - abbr: nft
    expansion: nftables (Linux packet filter)
  - abbr: ControlPath
    expansion: OpenSSH multiplexing socket path option
  - abbr: Pi
    expansion: single-board computer (Raspberry Pi class)
---

# prefixes.v6 needs nodes backfillips, not restart alone

## Context

Existing nodes do not grow ULA because a flag flipped. New nodes might. Backs [OEN-13](../networking/13-overlay-underlay-ula-layers.md).

## Topology

```text
prefixes.v6 enabled  +  restart only  -->  tailscale ip -6 empty on EXISTING nodes
Need nodes backfillips --force then restart
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

Do not bind HTTPS to missing ULA.

## Method

After prefixes.v6, run coordination `nodes backfillips --force` (or equivalent) then restart those nodes. MUST NOT expect restart alone.

## Consequences

Existing nodes get overlay IPv6. Binds that waited for ULA can start.

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
ssh -o ControlPath=none <user>@<cloud-vps> 'tailscale ip -6 || true'
# Coordinator: backfill existing nodes (private ops), then restart those nodes.
```

1. **P1 — See empty ip -6.**
   - **Action:** `tailscale ip -6` empty after prefixes.v6 + restart only.
   - **Expected:** Need backfill.
   - **On failure:** Do not bind HTTPS to missing ULA.
2. **P2 — backfillips --force.**
   - **Action:** On the coordinator, backfill existing nodes, then restart nodes.
   - **Expected:** `ip -6` populated.
   - **On failure:** Do not paste node IDs publicly.
3. **P3 — Then bind.**
   - **Action:** Services that need ULA start after the address exists ([OEN-13](../networking/13-overlay-underlay-ula-layers.md)).
   - **Expected:** No boot hole.
   - **On failure:** Ops SSH still overlay v4.

## Expected samples

```text
# empty ip -6 after restart-only
```

## Verify

- Existing node has overlay v6 after backfill+restart.
- Restart-only was not enough.
- ICMP / small ping success was **not** used as the pass criterion when this spec names TCP, SSH, or HTTPS.
- Bind table was filled by a human before any live `ip` / nft / iptables change.

## MUST NOT

- MUST NOT claim restart alone backfills prefixes.v6.
- MUST NOT publish node IDs or ULAs.
- MUST NOT apply live network or firewall changes until Bind is filled by a human.
- MUST NOT claim a fix on ICMP ping alone when Verify names TCP, SSH, or HTTPS.
- MUST NOT publish hostnames, addresses, ULAs, or custom ports.

## Related specs

- [OEN-13](../networking/13-overlay-underlay-ula-layers.md)

## Prior art (Not novel)

Prefix enable is documented. This note is existing nodes needing backfillips --force.

