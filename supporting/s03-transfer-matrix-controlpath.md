---
id: "OEN-S03"
title: "1 KB vs 1 MB transfer matrix + ControlPath=none"
kind: "supporting"
status: "active"
edition: 2
date_published: "2026-09-08"
author: "Eugene Armstead"
author_url: "https://www.armsteadent.com/"
canonical: "https://eugenearmstead.github.io/overlay-and-edge-notes/supporting/s03-transfer-matrix-controlpath.html"
keywords:
  - "1 KB vs 1 MB SSH matrix"
  - "ControlPath=none overlay SSH"
  - "SSH mux death symptom"
  - "userspace vs kernel SSH"
  - "Tailscale SSH byte cliff test"
  - "large scp hang overlay"
  - "OpenSSH vs Tailscale SSH"
  - "transfer size matrix"
  - "overlay SSH 3 KB hang"
  - "do not trust mux hang"
  - "ControlMaster stale socket"
  - "path MTU SSH proof"
backs:
  - OEN-01
backed_by:
  []
description: "Prove overlay SSH size: 1 KB vs about 1 MB with ControlPath=none. Mux death is a symptom. Userspace overlay SSH is less forgiving than kernel SSH on the same host."
terms:
  - abbr: ControlPath
    expansion: OpenSSH multiplexing socket path option
  - abbr: HTTPS
    expansion: Hypertext Transfer Protocol Secure
  - abbr: ICMP
    expansion: Internet Control Message Protocol
  - abbr: KB
    expansion: kilobyte
  - abbr: LAN
    expansion: Local Area Network
  - abbr: MB
    expansion: megabyte
  - abbr: MSS
    expansion: Maximum Segment Size
  - abbr: MTU
    expansion: Maximum Transmission Unit
  - abbr: nft
    expansion: nftables (Linux packet filter)
  - abbr: OEN
    expansion: Overlay and Edge Notes
  - abbr: OpenSSH
    expansion: OpenBSD Secure Shell
  - abbr: Pi
    expansion: single-board computer (Raspberry Pi class)
  - abbr: SSH
    expansion: Secure Shell
  - abbr: TCP
    expansion: Transmission Control Protocol
  - abbr: VPS
    expansion: Virtual Private Server
  - abbr: WAN
    expansion: Wide Area Network
  - abbr: VPN
    expansion: VPN
---

# 1 KB vs 1 MB transfer matrix + ControlPath=none

## Context

[OEN-01](../networking/01-overlay-ssh-byte-cliff.md) needs a size matrix, not a vibe. Dead multiplexing sockets are a **symptom**. Userspace overlay Secure Shell (SSH) cliffs sooner than kernel OpenSSH on the same host.

## Topology

```text
[client] -o ControlPath=none --> overlay SSH
    1 KB echo/dd    vs    ~1 MB dd
    userspace overlay SSH cliffs sooner than kernel SSH on the same host
Mux death is a symptom.
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
# Size matrix is not an MSS recipe. If you then clamp LAN↔VPN, use:
mss4_wg = <wg-mtu> - 40
mss6_wg = <wg-mtu> - 60
# LAN bridge MTU MUST stay 1500.
```

See [OEN-01](../networking/01-overlay-ssh-byte-cliff.md) and [OEN-S01](s01-pmtud-size-ladder.md).

## Method

Audits MUST use `-o ControlPath=none`. Record tiny vs ~1 MB (or 3 KB+) on `<cloud-vps>` vs `<lan-pi>`, overlay SSH vs kernel SSH if both exist.

## Consequences

The byte cliff is evidenced; mux is not “the fix.”

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
ssh -o ControlPath=none <user>@<cloud-vps> 'dd if=/dev/zero bs=1024 count=1 status=none | wc -c'
ssh -o ControlPath=none <user>@<cloud-vps> 'dd if=/dev/zero bs=1024 count=1024 status=none | wc -c'
ssh -o ControlPath=none <user>@<lan-pi> 'dd if=/dev/zero bs=1024 count=1024 status=none | wc -c'
```

1. **P1 — Disable mux.**
   - **Action:** Every SSH command in the audit: `-o ControlPath=none`.
   - **Expected:** New TCP session.
   - **On failure:** Heal mux sockets; they are not the MTU fix.
2. **P2 — Tiny vs large on the cloud VPS.**
   - **Action:** Overlay SSH `echo ok` then `dd if=/dev/zero bs=1024 count=1024 | wc -c` (or `top -bn1 | wc -c`).
   - **Expected:** Tiny works; large hangs on the VPS if OEN-01 applies.
   - **On failure:** If large already works, the cliff is gone.
3. **P3 — Same client, LAN Pi and kernel SSH.**
   - **Action:** Repeat on `<lan-pi>`. If a kernel SSH door exists on the VPS, compare (custom admin port is not the daily workaround).
   - **Expected:** Pi accepts 3 KB+. Kernel SSH may pass where userspace overlay hangs.
   - **On failure:** Do not switch daily ops to the custom port; fix the path.

## Expected samples

```text
1024
# hang on VPS before path fix; 1048576 after
```

## Verify

- ControlPath=none used.
- Size matrix recorded for VPS vs Pi.
- Mux not blamed as the MTU fix.
- ICMP / small ping success was **not** used as the pass criterion when this spec names TCP, SSH, or HTTPS.
- Bind table was filled by a human before any live `ip` / nft / iptables change.

## MUST NOT

- MUST NOT use a custom kernel SSH port as the daily fix.
- MUST NOT publish that port number.
- MUST NOT skip ControlPath=none.
- MUST NOT apply live network or firewall changes until Bind is filled by a human.
- MUST NOT claim a fix on ICMP ping alone when Verify names TCP, SSH, or HTTPS.
- MUST NOT publish hostnames, addresses, ULAs, or custom ports.

## Page changelog

- Edition 2 (8 Sep 2026, Mountain Time): Added overlay-impl Bind and trap-specific terms (review cleanup).

## Related specs

- [OEN-01](../networking/01-overlay-ssh-byte-cliff.md)
- [OEN-S19](s19-push-small-overlay-snapshots.md)

