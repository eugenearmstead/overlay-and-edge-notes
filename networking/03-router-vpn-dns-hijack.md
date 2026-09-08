---
id: OEN-03
title: "Router VPN DNS hijack looks like a path-MTU problem"
kind: original
status: active
edition: 1
date_published: 2026-09-08
author: Eugene Armstead
author_url: https://www.armsteadent.com/
canonical: https://eugenearmstead.github.io/overlay-and-edge-notes/networking/03-router-vpn-dns-hijack.html
keywords:
  - "router VPN DNS hijack"
  - "ASUSWRT-Merlin DNSVPN2"
  - "DNS Server DNAT port 53"
  - "ERR_TIMED_OUT Tailscale off"
  - "looks like path MTU"
  - "LAN DNS hung"
  - "consumer router VPN DNS"
  - "DNS hijack vs PMTU"
  - "WireGuard DNS Server field"
  - "IPv6 stall DNS"
  - "destination NAT :53"
  - "Merlin DNSVPN2"
backs: []
backed_by:
  - OEN-S24
description: "Consumer-router VPN DNS Server fields can destination-NAT LAN port 53 into the tunnel, producing hung DNS and browser timeouts that look like a path-MTU failure."
terms:
  - abbr: OEN
    expansion: Overlay and Edge Notes
  - abbr: SSH
    expansion: Secure Shell
  - abbr: LAN
    expansion: Local Area Network
  - abbr: WAN
    expansion: Wide Area Network
  - abbr: VPN
    expansion: Virtual Private Network
  - abbr: TCP
    expansion: Transmission Control Protocol
  - abbr: UDP
    expansion: User Datagram Protocol
  - abbr: MSS
    expansion: Maximum Segment Size
  - abbr: MTU
    expansion: Maximum Transmission Unit
  - abbr: ICMP
    expansion: Internet Control Message Protocol
  - abbr: PMTU
    expansion: path Maximum Transmission Unit
  - abbr: DF
    expansion: don't-fragment (IP flag)
  - abbr: TLS
    expansion: Transport Layer Security
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
  - abbr: DNS
    expansion: Domain Name System
  - abbr: DoH
    expansion: DNS over HTTPS
  - abbr: NAT
    expansion: network address translation
  - abbr: DNAT
    expansion: destination network address translation
  - abbr: nft
    expansion: nftables (Linux packet filter)
  - abbr: Happy-Eyeballs
    expansion: dual-stack connection racing (RFC 8305)
  - abbr: REFUSED
    expansion: DNS response code meaning the server will not answer
  - abbr: DHCP
    expansion: Dynamic Host Configuration Protocol
  - abbr: RA
    expansion: Router Advertisement (IPv6)
  - abbr: ASUSWRT-Merlin
    expansion: consumer-router firmware class
  - abbr: Chromium
    expansion: open-source browser engine
  - abbr: ASUSWRT
    expansion: ASUS consumer-router firmware family
---

# Router VPN DNS hijack looks like a path-MTU problem

## Context

Browser `ERR_TIMED_OUT`, IPv6 stall, or “the site is down” can appear **with overlay off**. Operators then clamp Maximum Segment Size (MSS) or shrink the Local Area Network (LAN) bridge — the [OEN-02](02-chromium-tls-pmtu.md) playbook — and nothing changes.

On ASUSWRT-Merlin-class firmware, filling WireGuard **DNS Server** fields can enable a destination network address translation (DNAT) helper (`DNSVPN2`) that steers LAN `:53` into the tunnel. When that resolver is unreachable, hung Domain Name System (DNS) looks like path Maximum Transmission Unit (MTU) or Happy-Eyeballs. A leak-test page that still shows “VPN DNS” is **not** proof the path is fine.

Public wording: consumer Merlin-class firmware, LAN DNS hijack into a commercial WireGuard client. MUST NOT name the commercial provider.

## Topology

```text
[LAN client] --UDP/TCP 53--> [<lan-resolver> intended]
                 \
                  +-- DNAT (firmware DNSVPN2-class) --> <wg-iface> tunnel DNS  (TRAP)

Overlay MAY be off. Browser ERR_TIMED_OUT still happens.
```

## Bind

Fill this table **before** any live change. Do **not** paste real values back into public notes.

| Placeholder | Operator fills | Class |
|-------------|----------------|-------|
| `<wg-iface>` | Consumer-router WireGuard client iface | Iface |
| `<lan-bridge>` | LAN bridge | Iface; MTU 1500 |
| `<wan-iface>` | WAN iface | Iface |
| `<lan-resolver>` | Intended LAN DNS | Address; never publish |


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

## Decision

Operators MUST check tunnel DNS hijack **before** MSS.

- VPN **DNS Server** fields on the consumer router client SHOULD be empty when LAN devices already have a working resolver.
- Operators MUST compare LAN `dig` with DNS over HTTPS (DoH). If LAN is sinkhole or timeout and DoH works, this is DNS, not MTU.
- Overlay being down is a useful A/B: if the browser still fails with overlay off, stop blaming overlay.

## Consequences

- Clearing the hijack restores LAN DNS without touching MTU.
- MSS work is not wasted on a DNS outage.
- LAN clients keep their advertised resolver instead of a tunnel-only one.

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
# Overlay off on the client, then:
dig +time=2 +tries=1 @<lan-resolver> example.com
# Compare with DNS over HTTPS (operator's DoH tool). If LAN fails and DoH works, this is DNS.

iptables -t nat -S | grep -i -E '53|dnat|dns' || true
ip6tables -t nat -S | grep -i -E '53|dnat|dns' || true
nft list ruleset | grep -i -E 'dport 53|dnat' || true
```

Empty the consumer-router WireGuard **DNS Server** fields. Do not shrink `<lan-bridge>` MTU.

1. **P1 — Reproduce with overlay off.**
   - **Action:** Disable overlay on the client. Retry the failing HTTPS site in Chromium and with `curl`.
   - **Expected:** Failure remains. This is not overlay mesh MTU.
   - **On failure:** If failure disappears, go to [OEN-02](02-chromium-tls-pmtu.md) / [OEN-01](01-overlay-ssh-byte-cliff.md) instead.
2. **P2 — Compare LAN DNS vs DNS over HTTPS.**
   - **Action:** `dig @<lan-resolver> example.com` with a short timeout. Then resolve the same name over DoH (or any resolver not on LAN `:53`).
   - **Expected:** LAN times out, REFUSED, or returns `0.0.0.0` while DoH works — or LAN is slow enough that browsers look hung.
   - **On failure:** If both work, DNS hijack is not this incident. Continue to MTU.
3. **P3 — Inspect the router VPN DNS fields.**
   - **Action:** On the consumer router WireGuard client, read DNS Server. Check for DNAT of LAN `:53` toward the tunnel (`DNSVPN2` or firmware equivalent).
   - **Expected:** A populated DNS Server plus DNAT rules matches this trap.
   - **On failure:** Do not add tunnel DNS “to fix” LAN; that is how the trap is installed.
4. **P4 — Empty the VPN DNS Server; keep LAN resolver.**
   - **Action:** Clear the WireGuard DNS Server fields. Confirm DNAT toward the tunnel is gone. Leave LAN DHCP/RA DNS as the intended resolver.
   - **Expected:** LAN `dig` returns real answers. Browser loads.
   - **On failure:** If LAN still returns `0.0.0.0`, follow [OEN-S24](../supporting/s24-lan-dns-sinkhole-0-0-0-0.md).

## Expected samples

```text
# Hung LAN DNS
;; connection timed out; no servers could be reached

# Sinkhole
example.com.  0  IN  A  0.0.0.0
```

## Verify

- Overlay off: site loads in Chromium.
- LAN dig and DoH agree on non-sinkhole answers.
- VPN DNS Server fields are empty; no LAN `:53` DNAT into `<wg-iface>`.
- LAN bridge MTU was not changed as part of this fix.
- ICMP / small ping success was **not** used as the pass criterion when this spec names TCP, SSH, or HTTPS.
- Bind table was filled by a human before any live `ip` / nft / iptables change.

## MUST NOT

- MUST NOT name the commercial VPN provider.
- MUST NOT “fix” hung DNS by shrinking the LAN bridge or adding tunnel DNS servers.
- MUST NOT treat a leak-test DNS name as proof of a working data path.
- MUST NOT publish LAN resolver addresses.
- MUST NOT apply live network or firewall changes until Bind is filled by a human.
- MUST NOT claim a fix on ICMP ping alone when Verify names TCP, SSH, or HTTPS.
- MUST NOT publish hostnames, addresses, ULAs, or custom ports.

## Related specs

- [OEN-02 Chromium TLS vs curl](02-chromium-tls-pmtu.md)
- [OEN-S24 LAN DNS returning 0.0.0.0](../supporting/s24-lan-dns-sinkhole-0-0-0-0.md)
- [OEN-16 Commercial WireGuard endpoint rotation](16-commercial-wg-endpoint-rotation.md)

## Prior art (Not novel)

VPN DNS on routers is a known footgun. This spec’s claim is that Merlin-class DNSVPN2 hijack **mimics** browser PMTU, so MSS-first diagnosis is wrong.

