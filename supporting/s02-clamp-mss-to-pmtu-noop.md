---
id: OEN-S02
title: "clamp-mss-to-pmtu is a no-op when ICMP is dropped"
kind: supporting
status: active
edition: 1
date_published: 2026-09-08
author: Eugene Armstead
author_url: https://www.armsteadent.com/
canonical: https://eugenearmstead.github.io/overlay-and-edge-notes/supporting/s02-clamp-mss-to-pmtu-noop.html
keywords:
  - "clamp-mss-to-pmtu no-op"
  - "ICMP blackholed MSS clamp"
  - "explicit --set-mss"
  - "TCPMSS clamp-mss-to-pmtu"
  - "learned PMTU missing"
  - "fragmentation-needed dropped"
  - "iptables set-mss vs clamp"
  - "PMTUD blackhole MSS"
  - "don't-fragment ping"
  - "WireGuard MSS recipe"
  - "nft TCPMSS set"
  - "path MTU ICMP silent"
backs:
  - OEN-01
  - OEN-02
backed_by: []
description: "iptables --clamp-mss-to-pmtu uses learned path MTU. When ICMP fragmentation-needed is blackholed, the clamp does nothing; use explicit --set-mss."
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
  - abbr: VPN
    expansion: Virtual Private Network
  - abbr: KB
    expansion: kilobyte
  - abbr: TCP
    expansion: Transmission Control Protocol
  - abbr: MSS
    expansion: Maximum Segment Size
  - abbr: TCPMSS
    expansion: iptables/nft target that sets TCP Maximum Segment Size
  - abbr: MTU
    expansion: Maximum Transmission Unit
  - abbr: ICMP
    expansion: Internet Control Message Protocol
  - abbr: PMTU
    expansion: path Maximum Transmission Unit
  - abbr: PMTUD
    expansion: path MTU discovery
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
  - abbr: FORWARD
    expansion: netfilter/iptables forward chain
  - abbr: Pi
    expansion: single-board computer (Raspberry Pi class)
  - abbr: Chromium
    expansion: open-source browser engine
  - abbr: Inter
    expansion: variable sans-serif font family
---

# clamp-mss-to-pmtu is a no-op when ICMP is dropped

## Context

The usual recipe `TCPMSS --clamp-mss-to-pmtu` on Local Area Network (LAN)↔Virtual Private Network (VPN) FORWARD does **nothing useful** when Internet Control Message Protocol (ICMP) path MTU discovery (PMTUD) is blackholed — common on commercial WireGuard. Packet counters may increment while Maximum Segment Size (MSS) never changes. Backs [OEN-01](../networking/01-overlay-ssh-byte-cliff.md) and [OEN-02](../networking/02-chromium-tls-pmtu.md).

## Topology

```text
LAN<->VPN FORWARD TCPMSS --clamp-mss-to-pmtu
ICMP frag-needed blackholed  -->  learned PMTU never updates  -->  clamp is a no-op
FIX: explicit --set-mss <mss4>/<mss6>
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

Use explicit `TCPMSS --set-mss` with a value under the tunnel payload (example 1200). MUST NOT treat clamp-to-pmtu as the LAN↔VPN fix when ICMP is dropped.

## Consequences

Chromium and overlay Secure Shell (SSH) large output start working without shrinking the LAN bridge to the tunnel Maximum Transmission Unit (MTU).

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
iptables -S FORWARD | grep -i tcpmss
ip6tables -S FORWARD | grep -i tcpmss
# Replace clamp-mss-to-pmtu with --set-mss "$mss4" / "$mss6" on <lan-bridge><-><wg-iface> only.
```

1. **P1 — See clamp-to-pmtu with no learned PMTU.**
   - **Action:** List FORWARD TCPMSS. Note `--clamp-mss-to-pmtu`. Don't-fragment ladder ([OEN-S01](s01-pmtud-size-ladder.md)) still cliffs; Chromium still closes.
   - **Expected:** Rule exists; TCP still too large.
   - **On failure:** If ICMP frag-needed is visible, clamp-to-pmtu MAY work — this spec does not apply.
2. **P2 — Replace with explicit --set-mss.**
   - **Action:** On LAN↔`<wg-iface>` v4 and v6, `--set-mss` under tunnel payload. Keep LAN 1500.
   - **Expected:** Chromium HTTPS and/or overlay SSH 3 KB+ work.
   - **On failure:** Do not also shrink the LAN MTU.
3. **P3 — Confirm ICMP still dropped.**
   - **Action:** Large DF ping may still fail; TCP now fits because MSS was forced.
   - **Expected:** TCP works; ICMP PMTUD remains blackholed.
   - **On failure:** That split is expected.

## Expected samples

```text
# Counters increment, Chromium still closes — clamp-to-pmtu learned nothing
TCPMSS  ...  clamp to PMTU  pkts:N
```

## Verify

- Explicit --set-mss on LAN↔VPN only.
- LAN MTU 1500.
- Browser or SSH symptom gone.
- ICMP / small ping success was **not** used as the pass criterion when this spec names TCP, SSH, or HTTPS.
- Bind table was filled by a human before any live `ip` / nft / iptables change.

## MUST NOT

- MUST NOT rely on --clamp-mss-to-pmtu when ICMP is dropped.
- MUST NOT shrink the LAN bridge to make the ladder green.
- MUST NOT clamp overlay return.
- MUST NOT apply live network or firewall changes until Bind is filled by a human.
- MUST NOT claim a fix on ICMP ping alone when Verify names TCP, SSH, or HTTPS.
- MUST NOT publish hostnames, addresses, ULAs, or custom ports.

## Related specs

- [OEN-01](../networking/01-overlay-ssh-byte-cliff.md)
- [OEN-02](../networking/02-chromium-tls-pmtu.md)
- [OEN-S01](s01-pmtud-size-ladder.md)

## Prior art (Not novel)

clamp-mss-to-pmtu is the man-page default. This note exists because commercial-VPN ICMP blackholes make it a no-op.

