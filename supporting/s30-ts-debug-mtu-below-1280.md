---
id: "OEN-S30"
title: "TS_DEBUG_MTU below 1280 disables overlay IPv6"
kind: "supporting"
status: "active"
edition: 3
date_published: "2026-09-08"
author: "Eugene Armstead"
author_url: "https://www.armsteadent.com/"
canonical: "https://eugenearmstead.github.io/overlay-and-edge-notes/supporting/s30-ts-debug-mtu-below-1280.html"
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
backed_by:
  []
description: "TS_DEBUG_MTU below 1280 makes the kernel drop IPv6 on the overlay tun. Do not use it as a production clamp."
terms:
  - abbr: CLI
    expansion: command-line interface
  - abbr: ControlPath
    expansion: OpenSSH multiplexing socket path option
  - abbr: IPv6
    expansion: Internet Protocol version 6
  - abbr: LAN
    expansion: Local Area Network
  - abbr: MTU
    expansion: Maximum Transmission Unit
  - abbr: OEN
    expansion: Overlay and Edge Notes
  - abbr: RFC
    expansion: Request for Comments
  - abbr: SSH
    expansion: Secure Shell
  - abbr: VPS
    expansion: Virtual Private Server
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
| `<overlay-impl>` | Overlay implementation class | `tailscale-compatible` or other — stop and translate CLI |
| `<cloud-vps>` | Node whose overlay tun is under test | Cloud VPS |
| `<user>` | SSH user | Guest account |
| `<overlay-tun>` | Overlay tun iface | Node under test |
| `<lan-bridge>` | LAN bridge | Router (MTU 1500) |
| `<overlay-tun>` | Overlay tun iface | Node under test |

## Formulas

IPv6 minimum MTU 1280 is RFC. Unset or set ≥1280.

## Method

MUST NOT set TS_DEBUG_MTU below 1280. Raise or unset it.

## Consequences

overlay `ip -6` can exist; tun accepts v6.

## Agent stop rule

> MUST emit the `tailscaled` environ grep after `<overlay-impl>` is `tailscale-compatible` and Bind is filled.
> MUST NOT set `TS_DEBUG_MTU` below 1280 as a production clamp.
> MUST NOT shrink the LAN bridge to match a debug MTU.
> MUST NOT apply netfilter from this page.

## Procedure

This spec does not apply if `<overlay-impl>` is not tailscale-compatible.

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

Stdout of the copy-paste block when the debug env is set too low:

```text
TS_DEBUG_MTU=1000
```

Empty stdout means the variable is unset (acceptable if overlay IPv6 remains).

## Verify

- TS_DEBUG_MTU not below 1280.
- Overlay v6 not kernel-disabled by that env.

## MUST NOT

- MUST NOT ship TS_DEBUG_MTU < 1280 in production.
- MUST NOT shrink LAN because of it.
- MUST NOT publish hostnames, addresses, ULAs, or custom ports.

## Page changelog

- Edition 2 (8 Sep 2026, Mountain Time): Added overlay-impl Bind and trap-specific terms (review cleanup).

## Related specs

- [OEN-13](../networking/13-overlay-underlay-ula-layers.md)
- [OEN-S31](s31-prefixes-v6-needs-backfillips.md)

