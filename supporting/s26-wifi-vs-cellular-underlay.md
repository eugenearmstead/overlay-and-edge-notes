---
id: OEN-S26
title: "Wi-Fi underlay vs cellular underlay to the same cloud exit"
kind: supporting
status: active
edition: 1
date_published: 2026-09-08
author: Eugene Armstead
author_url: https://www.armsteadent.com/
canonical: https://eugenearmstead.github.io/overlay-and-edge-notes/supporting/s26-wifi-vs-cellular-underlay.html
keywords:
  - "Wi-Fi vs cellular underlay"
  - "same cloud exit two underlays"
  - "home Wi-Fi encapsulates overlay"
  - "cellular direct to cloud"
  - "IPv4 cloud IPv6 home leak"
  - "not the GCP exit is broken"
  - "underlay WireGuard vs cellular"
  - "split v4/v6 underlay"
  - "Tailscale exit Wi-Fi cellular"
  - "Happy-Eyeballs vs underlay"
  - "phone Wi-Fi tunnel encapsulate"
  - "cellular overlay path"
backs:
  - OEN-13
  - OEN-16
  - OEN-17
backed_by: []
description: "Home Wi-Fi may encapsulate overlay inside commercial WireGuard; cellular may go direct. IPv4 can show the cloud while IPv6 leaks the home tunnel. Not “the GCP exit is broken.”"
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
  - abbr: WG
    expansion: WireGuard
  - abbr: WireGuard
    expansion: UDP-based VPN protocol
  - abbr: NAT
    expansion: network address translation
  - abbr: ULA
    expansion: unique-local address (IPv6)
  - abbr: GCP
    expansion: Google Cloud Platform
  - abbr: VM
    expansion: virtual machine
  - abbr: NIC
    expansion: network interface card
  - abbr: nft
    expansion: nftables (Linux packet filter)
  - abbr: Pi
    expansion: single-board computer (Raspberry Pi class)
  - abbr: Happy-Eyeballs
    expansion: dual-stack connection racing (RFC 8305)
  - abbr: PC
    expansion: personal computer
---

# Wi-Fi underlay vs cellular underlay to the same cloud exit

## Context

Distinct from [OEN-20](../networking/20-lan-ula-happy-eyeballs-leak.md) (LAN ULA Happy-Eyeballs while an exit is selected). This is two underlays to the same cloud exit.

## Topology

```text
Same <exit-node>, two underlays:
  home Wi-Fi MAY encapsulate overlay inside commercial WG
  cellular MAY go direct
v4 cloud / v6 home leak is NOT "GCP broken"
Distinct from [OEN-20](../networking/20-lan-ula-happy-eyeballs-leak.md)
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

Always A/B Wi-Fi vs cellular before changing GCP NAT/MTU. MUST NOT treat a Wi-Fi-only v6 leak as a broken cloud exit.

## Consequences

Fewer pointless GCP MTU changes.

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
# A/B: curl -4/-6 on Wi-Fi vs cellular with the same exit selected (phone), not the agent PC
```

1. **P1 — Same exit, two underlays.**
   - **Action:** Select `<exit-node>`. curl -4/-6 on home Wi-Fi vs cellular.
   - **Expected:** Families and egress differ by underlay.
   - **On failure:** If both underlays fail the same way, look at the exit ([OEN-17](../networking/17-gcp-overlay-exit.md)).
2. **P2 — Name encapsulation.**
   - **Action:** Wi-Fi may ride commercial WG; cellular may be direct overlay.
   - **Expected:** Do not call that “GCP broken.”
   - **On failure:** See [OEN-13](../networking/13-overlay-underlay-ula-layers.md).
3. **P3 — Distinct from OEN-20.**
   - **Action:** If LAN ULA Happy-Eyeballs, that spec. If only underlay differs, this spec.
   - **Expected:** One sentence in the incident which trap.
   - **On failure:** Do not mix the tables.

## Expected samples

```text
# Wi-Fi v6 egress = home tunnel prefix; cellular v6 = cloud
```

## Verify

- Wi-Fi vs cellular matrix recorded.
- GCP not blamed for a Wi-Fi-only encapsulate leak.
- ICMP / small ping success was **not** used as the pass criterion when this spec names TCP, SSH, or HTTPS.
- Bind table was filled by a human before any live `ip` / nft / iptables change.

## MUST NOT

- MUST NOT keep changing GCP MTU for a Wi-Fi/cellular split.
- MUST NOT publish underlay IPs.
- MUST NOT apply live network or firewall changes until Bind is filled by a human.
- MUST NOT claim a fix on ICMP ping alone when Verify names TCP, SSH, or HTTPS.
- MUST NOT publish hostnames, addresses, ULAs, or custom ports.

## Related specs

- [OEN-20](../networking/20-lan-ula-happy-eyeballs-leak.md)
- [OEN-17](../networking/17-gcp-overlay-exit.md)
- [OEN-16](../networking/16-commercial-wg-endpoint-rotation.md)

## Prior art (Not novel)

Different underlays are obvious. This note is the false “GCP exit is broken” when only Wi-Fi encapsulates.

