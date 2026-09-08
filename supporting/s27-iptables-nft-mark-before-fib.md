---
id: OEN-S27
title: "iptables-nft PREROUTING MARK does not win before the forwarding information base"
kind: supporting
status: active
edition: 1
date_published: 2026-09-08
author: Eugene Armstead
author_url: https://www.armsteadent.com/
canonical: https://eugenearmstead.github.io/overlay-and-edge-notes/supporting/s27-iptables-nft-mark-before-fib.html
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
backed_by: []
description: "Counters look marked; ip -6 route get overlay-ula iif tunnel still shows the WAN NIC. Need mark and overlay ULA /48 on table 52 and main. Split nft plus ip6tables MASQUERADE breaks conntrack."
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
  - abbr: HTTPS
    expansion: Hypertext Transfer Protocol Secure
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
  - abbr: FIB
    expansion: forwarding information base
  - abbr: nft
    expansion: nftables (Linux packet filter)
  - abbr: MASQUERADE
    expansion: iptables masquerade (source NAT)
  - abbr: PREROUTING
    expansion: netfilter prerouting chain
  - abbr: MARK
    expansion: netfilter packet mark
  - abbr: Pi
    expansion: single-board computer (Raspberry Pi class)
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
| `<exit-node>` | Overlay exit node | Cloud VM or LAN Pi used as exit |
| `<overlay-peer>` | Soak client (**not** the agent workstation) | LAN Pi |
| `<user>` | SSH user | Guest |
| `<overlay-tun>` | Overlay tun on the exit | Iface |
| `<gcp-nic>` | Public NIC on a Google Cloud guest | Iface; omit on non-GCP exits |
| `<wan-iface>` | WAN / public NIC | Iface |
| `<mss4>` / `<mss6>` | Computed from underlay or overlay tun MTU | Formulas |


## Formulas

One ip6tables NAT path. Backs [OEN-06](../networking/06-netfilter-off-v6-return.md).

## Method

One ip6tables path. ULA /48 on table 52 **and** main. MUST NOT split nft and ip6tables MASQUERADE.

## Consequences

Return path exists. Counters stop lying.

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

## Related specs

- [OEN-06](../networking/06-netfilter-off-v6-return.md)

## Prior art (Not novel)

Policy routing is documented. This note is iptables-nft mark missing the first FIB lookup.

