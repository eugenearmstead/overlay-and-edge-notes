---
id: OEN-S19
title: "Push small overlay snapshots; do not copy-pull large JSON"
kind: supporting
status: active
edition: 1
date_published: 2026-09-08
author: Eugene Armstead
author_url: https://www.armsteadent.com/
canonical: https://eugenearmstead.github.io/overlay-and-edge-notes/supporting/s19-push-small-overlay-snapshots.html
keywords:
  - "push small overlay snapshots"
  - "do not SCP-pull large JSON"
  - "overlay SSH byte cliff JSON"
  - "fleet snapshot chunks"
  - "Tailscale SSH large JSON hang"
  - "push to hub not pull"
  - "ControlPath=none large scp"
  - "NDJSON small chunks"
  - "health snapshot overlay"
  - "SCP hang 1KB cliff"
  - "Headscale JSON over SSH"
  - "push not pull overlay"
backs:
  - OEN-01
backed_by: []
description: "Fleet snapshots: push small chunks to the hub. Do not SCP-pull large JSON over overlay SSH or you hit the byte cliff."
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
  - abbr: KB
    expansion: kilobyte
  - abbr: TCP
    expansion: Transmission Control Protocol
  - abbr: MSS
    expansion: Maximum Segment Size
  - abbr: MTU
    expansion: Maximum Transmission Unit
  - abbr: ICMP
    expansion: Internet Control Message Protocol
  - abbr: DF
    expansion: don't-fragment (IP flag)
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
  - abbr: nft
    expansion: nftables (Linux packet filter)
  - abbr: ControlPath
    expansion: OpenSSH multiplexing socket path option
  - abbr: JSON
    expansion: JavaScript Object Notation
  - abbr: SCP
    expansion: secure copy
  - abbr: Pi
    expansion: single-board computer (Raspberry Pi class)
---

# Push small overlay snapshots; do not copy-pull large JSON

## Context

Backs [OEN-S03](s03-transfer-matrix-controlpath.md) / [OEN-01](../networking/01-overlay-ssh-byte-cliff.md). Large JSON over userspace overlay SSH hangs.

## Topology

```text
[spokes] push small snapshots --> hub
MUST NOT SCP-pull large JSON over overlay SSH  ([OEN-01](../networking/01-overlay-ssh-byte-cliff.md))
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

```text
# Measure <wg-mtu> from: ip link show <wg-iface>
mss4 = <wg-mtu> - 40    # IPv4 TCP (20-byte IP + 20-byte TCP)
mss6 = <wg-mtu> - 60    # IPv6 TCP (40-byte IPv6 + 20-byte TCP)
# IPv4 DF ping: IP size ≈ payload + 28
# IPv6 DF ping: IP size ≈ payload + 48
# Historical 1160 / 1146-byte SSH cliff = wrong-scope clamp, not this recipe.
# LAN bridge MTU MUST stay 1500.
```

See [OEN-01](../networking/01-overlay-ssh-byte-cliff.md) and [OEN-S01](../supporting/s01-pmtud-size-ladder.md).

## Method

Nodes PUSH small files to `<lan-pi>`. MUST NOT pull multi-megabyte JSON over overlay SSH as the daily collector.

## Consequences

Collectors finish. SSH sessions do not freeze at the cliff.

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
ssh -o ControlPath=none <user>@<lan-pi> 'wc -c <small-snapshot>'
# If a pull of megabyte JSON hangs, this spec + OEN-01 / OEN-S03
```

1. **P1 — Size the payload.**
   - **Action:** If the JSON is hundreds of KB+, it is in the cliff zone on a bad path.
   - **Expected:** Switch to push-small or kernel SSH after path fix.
   - **On failure:** Do not raise timeout as the fix.
2. **P2 — Push to the hub.**
   - **Action:** Each node writes a small chunk and pushes to the always-on Pi.
   - **Expected:** Hub concatenates. No large pull.
   - **On failure:** Workstation is not the hub ([OEN-S13](s13-restart-always-missing-unit.md)).
3. **P3 — ControlPath=none when auditing.**
   - **Action:** Same as OEN-S03.
   - **Expected:** Mux not blamed.
   - **On failure:** Fix path still required for interactive large SSH.

## Expected samples

```text
# small chunk finishes; large JSON pull hangs at ~1 KB
```

## Verify

- Collector uses push-small.
- No SCP-pull of huge JSON over overlay SSH.
- ICMP / small ping success was **not** used as the pass criterion when this spec names TCP, SSH, or HTTPS.
- Bind table was filled by a human before any live `ip` / nft / iptables change.

## MUST NOT

- MUST NOT SCP-pull large JSON over overlay SSH as the design.
- MUST NOT use the workstation as the hub.
- MUST NOT apply live network or firewall changes until Bind is filled by a human.
- MUST NOT claim a fix on ICMP ping alone when Verify names TCP, SSH, or HTTPS.
- MUST NOT publish hostnames, addresses, ULAs, or custom ports.

## Related specs

- [OEN-01](../networking/01-overlay-ssh-byte-cliff.md)
- [OEN-S03](s03-transfer-matrix-controlpath.md)

## Prior art (Not novel)

Chunked uploads are obvious. This note is overlay SSH byte-cliff as the reason.

