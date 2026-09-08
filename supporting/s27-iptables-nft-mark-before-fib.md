---
id: "OEN-S27"
title: "iptables-nft PREROUTING MARK does not win before the forwarding information base"
kind: "supporting"
status: "active"
edition: 2
date_published: "2026-09-08"
author: "Eugene Armstead"
author_url: "https://www.armsteadent.com/"
canonical: "https://eugenearmstead.github.io/overlay-and-edge-notes/supporting/s27-iptables-nft-mark-before-fib.html"
keywords:
  - "iptables-nft MARK before fib"
  - "counters marked route still WAN"
  - "ip -6 route get iif tunnel"
  - "ULA /48 table 52 and main"
  - "split nft ip6tables MASQUERADE"
  - "conntrack return broken"
  - "PREROUTING MARK FIB lookup"
  - "NetfilterMode=off mark"
  - "overlay ULA missing main"
  - "ip6tables mangle MARK"
  - "nft mark not first FIB"
  - "IPv6 exit return path"
backs:
  - OEN-06
backed_by:
  []
description: "Counters look marked; ip -6 route get overlay-ula iif tunnel still shows the WAN NIC. Need mark and overlay ULA /48 on table 52 and main. Split nft plus ip6tables MASQUERADE breaks conntrack."
terms:
  - abbr: FIB
    expansion: forwarding information base
  - abbr: HTTPS
    expansion: Hypertext Transfer Protocol Secure
  - abbr: ICMP
    expansion: Internet Control Message Protocol
  - abbr: IPv6
    expansion: Internet Protocol version 6
  - abbr: MARK
    expansion: netfilter packet mark
  - abbr: MASQUERADE
    expansion: iptables masquerade (source NAT)
  - abbr: NAT
    expansion: network address translation
  - abbr: nft
    expansion: nftables (Linux packet filter)
  - abbr: NIC
    expansion: network interface card
  - abbr: OEN
    expansion: Overlay and Edge Notes
  - abbr: PREROUTING
    expansion: netfilter prerouting chain
  - abbr: SSH
    expansion: Secure Shell
  - abbr: TCP
    expansion: Transmission Control Protocol
  - abbr: ULA
    expansion: unique-local address (IPv6)
  - abbr: VPS
    expansion: Virtual Private Server
  - abbr: WAN
    expansion: Wide Area Network
---

# iptables-nft PREROUTING MARK does not win before the forwarding information base

## Context

Method behind [OEN-06](../networking/06-netfilter-off-v6-return.md).

## Topology

```text
iptables-nft PREROUTING MARK  -->  counters look marked
ip -6 route get ULA iif tunnel  -->  still WAN NIC
Need /48 on table 52 AND main
```

## Bind

Fill this table **before** any live change. Do **not** paste real values back into public notes.

| Placeholder | Operator fills | Class |
|-------------|----------------|-------|
| `<overlay-ula>` | Overlay unique-local prefix class | ULA /48; never publish |
| `<wg-iface>` | Commercial WireGuard iface | Router or VPS client |
| `<tunnel>` | Commercial tunnel iface on the exit | Iface |

## Formulas

One ip6tables NAT path. Backs [OEN-06](../networking/06-netfilter-off-v6-return.md).

## Method

One ip6tables path. ULA /48 on table 52 **and** main. MUST NOT split nft and ip6tables MASQUERADE.

## Consequences

Return path exists. Counters stop lying.

## Agent stop rule

> MUST emit bound iptables-nft MARK vs FIB checks after Bind is filled.
> MUST NOT apply `ip rule`, nft, or ip6tables until a human filled Bind.
> MUST NOT claim ICMP ping as the IPv6-return fix.
> MUST NOT split nft mark and ip6tables MASQUERADE.

## Procedure


### Copy-paste commands (after Bind)

```bash
ip -6 route get <overlay-ula> iif <wg-iface>
ip6tables -t mangle -L PREROUTING -n -v
```

1. **P1 — Route get iif tunnel.**
   - **Action:** `ip -6 route get <overlay-ula> iif <tunnel>`. If WAN NIC, mark lost the FIB.
   - **Expected:** Need routes, not more NAT.
   - **On failure:** Counters incrementing is not enough.
2. **P2 — /48 on 52 and main.**
   - **Action:** Install overlay ULA /48 both tables.
   - **Expected:** route get enters overlay.
   - **On failure:** v4 /32s existing does not imply v6 prefix.
3. **P3 — One MASQUERADE family.**
   - **Action:** Remove split nft MASQUERADE.
   - **Expected:** Conntrack return works.
   - **On failure:** No second -o public-nic MASQUERADE ([OEN-17](../networking/17-gcp-overlay-exit.md)).

## Expected samples

```text
# route get still dev <wan-iface>
```

## Verify

- route get iif tunnel uses overlay.
- Single ip6tables NAT path.
- ICMP / small ping success was **not** used as the pass criterion when this spec names TCP, SSH, or HTTPS.
- Bind table was filled by a human before any live `ip` / nft / iptables change.

## MUST NOT

- MUST NOT trust mark counters without route get.
- MUST NOT publish real ULA.
- MUST NOT apply live network or firewall changes until Bind is filled by a human.
- MUST NOT claim a fix on ICMP ping alone when Verify names TCP, SSH, or HTTPS.
- MUST NOT publish hostnames, addresses, ULAs, or custom ports.

## Page changelog

- Edition 2 (8 Sep 2026, Mountain Time): Trap-specific Bind and agent stop rule (review cleanup).

## Related specs

- [OEN-06](../networking/06-netfilter-off-v6-return.md)

