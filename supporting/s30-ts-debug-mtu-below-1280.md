---
id: OEN-S30
title: "TS_DEBUG_MTU below 1280 disables overlay IPv6"
kind: supporting
status: active
edition: 1
date_published: 2026-09-08
author: Eugene Armstead
author_url: https://www.armsteadent.com/
canonical: https://eugenearmstead.github.io/overlay-and-edge-notes/supporting/s30-ts-debug-mtu-below-1280.html
keywords:
  - "TS_DEBUG_MTU below 1280"
  - "overlay IPv6 disabled MTU"
  - "kernel drops v6 on tun"
  - "do not use TS_DEBUG_MTU production"
  - "Tailscale debug MTU IPv6"
  - "tun IPv6 1280 minimum"
  - "TS_DEBUG_MTU clamp"
  - "overlay v6 gone after debug MTU"
  - "Headscale IPv6 MTU"
  - "1280 IPv6 minimum"
  - "debug MTU kills v6"
  - "tailscaled IPv6 dropped"
backs:
  - OEN-13
  - OEN-17
backed_by: []
description: "TS_DEBUG_MTU below 1280 makes the kernel drop IPv6 on the overlay tun. Do not use it as a production clamp."
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
  - abbr: nft
    expansion: nftables (Linux packet filter)
  - abbr: ControlPath
    expansion: OpenSSH multiplexing socket path option
  - abbr: Pi
    expansion: single-board computer (Raspberry Pi class)
  - abbr: RFC
    expansion: Request for Comments
---

# TS_DEBUG_MTU below 1280 disables overlay IPv6

## Context

Backs [OEN-13](../networking/13-overlay-underlay-ula-layers.md). v6 silently disappears.

## Topology

```text
TS_DEBUG_MTU < 1280  -->  kernel drops IPv6 on overlay tun
Not a production clamp
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

IPv6 minimum MTU 1280 is RFC. Unset or set ≥1280.

## Method

MUST NOT set TS_DEBUG_MTU below 1280. Raise or unset it.

## Consequences

overlay `ip -6` can exist; tun accepts v6.

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
ssh -o ControlPath=none <user>@<cloud-vps> 'tr "\0" "\n" < /proc/$(pidof tailscaled)/environ 2>/dev/null | grep TS_DEBUG_MTU || true'
```

1. **P1 — Check the env.**
   - **Action:** If TS_DEBUG_MTU < 1280, that disables overlay IPv6.
   - **Expected:** Unset or set ≥1280.
   - **On failure:** Do not use it to “fix browsing.”
2. **P2 — Confirm tun v6.**
   - **Action:** `tailscale ip -6` / `ip -6 addr` on the overlay iface.
   - **Expected:** Address present; pings not kernel-dropped for MTU<1280.
   - **On failure:** Then [OEN-S31](s31-prefixes-v6-needs-backfillips.md) if still empty.
3. **P3 — LAN stays 1500.**
   - **Action:** Do not shrink LAN to match a debug MTU ([OEN-01](../networking/01-overlay-ssh-byte-cliff.md)).
   - **Expected:** LAN 1500.
   - **On failure:** Debug env is not a LAN policy.

## Expected samples

```text
TS_DEBUG_MTU=1000   # disables overlay v6
```

## Verify

- TS_DEBUG_MTU not below 1280.
- Overlay v6 not kernel-disabled by that env.
- ICMP / small ping success was **not** used as the pass criterion when this spec names TCP, SSH, or HTTPS.
- Bind table was filled by a human before any live `ip` / nft / iptables change.

## MUST NOT

- MUST NOT ship TS_DEBUG_MTU < 1280 in production.
- MUST NOT shrink LAN because of it.
- MUST NOT apply live network or firewall changes until Bind is filled by a human.
- MUST NOT claim a fix on ICMP ping alone when Verify names TCP, SSH, or HTTPS.
- MUST NOT publish hostnames, addresses, ULAs, or custom ports.

## Related specs

- [OEN-13](../networking/13-overlay-underlay-ula-layers.md)
- [OEN-S31](s31-prefixes-v6-needs-backfillips.md)

## Prior art (Not novel)

IPv6 minimum MTU 1280 is RFC. This note is the overlay debug env violating it.

