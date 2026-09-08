---
id: OEN-06
title: "Netfilter-off IPv6 return-path blackhole"
kind: original
status: active
edition: 1
date_published: 2026-09-08
author: Eugene Armstead
author_url: https://www.armsteadent.com/
canonical: https://eugenearmstead.github.io/overlay-and-edge-notes/networking/06-netfilter-off-v6-return.html
keywords:
  - exit-node
  - ipv6
  - netfilter
  - fib
backs: []
backed_by:
  - OEN-S27
description: "With overlay netfilter off, an nft prerouting mark does not win the first IPv6 route lookup. Use one ip6tables path and install the overlay unique-local /48 on table 52 and main."
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
  - abbr: MTU
    expansion: Maximum Transmission Unit
  - abbr: ICMP
    expansion: Internet Control Message Protocol
  - abbr: HTTP
    expansion: Hypertext Transfer Protocol
  - abbr: HTTPS
    expansion: Hypertext Transfer Protocol Secure
  - abbr: IPv4
    expansion: Internet Protocol version 4
  - abbr: IPv6
    expansion: Internet Protocol version 6
  - abbr: DNS
    expansion: Domain Name System
  - abbr: NAT
    expansion: network address translation
  - abbr: SNAT
    expansion: source network address translation
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
  - abbr: FORWARD
    expansion: netfilter/iptables forward chain
  - abbr: MASQUERADE
    expansion: iptables masquerade (source NAT)
  - abbr: PREROUTING
    expansion: netfilter prerouting chain
  - abbr: MARK
    expansion: netfilter packet mark
  - abbr: ControlPath
    expansion: OpenSSH multiplexing socket path option
  - abbr: Pi
    expansion: single-board computer (Raspberry Pi class)
  - abbr: POSTROUTING
    expansion: netfilter postrouting chain
---

# Netfilter-off IPv6 return-path blackhole

## Context

On a cloud Virtual Private Server (VPS) `<exit-node>` with overlay **NetfilterMode=off**, IPv6 exit can egress while return dies. Source network address translation (SNAT) / MASQUERADE counters increment; `FORWARD` from the commercial tunnel toward the overlay stays 0. `ip -6 route get <overlay-ula> iif <tunnel>` points at the **public NIC**, not back into overlay.

nft prerouting MARK on the overlay iface did **not** apply before the first forwarding information base (FIB) lookup when the backend was iptables-nft. Unmarked IPv6 went out the VPS public NIC. Splitting nft mark plus a separate ip6tables MASQUERADE broke conntrack return.

IPv4 often already has /32 overlays on table 52 and main. The IPv6 unique-local address (ULA) **/48** was missing with netfilter off.

## Topology

```text
[exit client] --v6--> [<exit-node> overlay]
    mark in PREROUTING (iptables-nft)  --X-->  first FIB lookup still uses WAN NIC  (TRAP)
    ip -6 route get <overlay-ula> iif <tunnel>  shows <wan-iface>   (proof)
    FIX: overlay ULA /48 on table 52 AND main; one ip6tables MASQUERADE path
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

Do not publish a real ULA. Use `<overlay-ula>` as a prefix class (`/48`). Measure, do not invent table numbers if this guest uses another policy table — list `ip -6 rule` first.

## Decision

Use **one** ip6tables path: mangle PREROUTING MARK plus source-based MASQUERADE on the tunnel. Install the overlay ULA `/48` on **table 52 and main**.

MUST NOT split nft + ip6tables MASQUERADE. MUST NOT paste a real node ULA in public text — write `<overlay-ula>` / “overlay ULA /48”.

## Consequences

- Exit-client IPv6 HTTPS returns.
- FORWARD tunnel→overlay counters increment.
- Conntrack stays on one family of tools.

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
ssh -o ControlPath=none <user>@<exit-node> 'ip -6 rule; ip -6 route show table 52; ip -6 route show table main | head'
ip -6 route get <overlay-ula> iif <wg-iface>
# Want: via overlay, not dev <wan-iface> / <gcp-nic>

ip6tables -t mangle -S PREROUTING
ip6tables -t nat -S POSTROUTING
nft list ruleset | grep -i masquerade || true
```

MUST NOT split nft MASQUERADE and ip6tables MASQUERADE. MUST NOT add a second `-o <gcp-nic>` MASQUERADE ([OEN-17](17-gcp-overlay-exit.md)).

1. **P1 — Capture the blackhole signature.**
   - **Action:** On `<exit-node>`, attempt exit-client `curl -6`. Watch ip6tables SNAT/MASQUERADE counters vs FORWARD `<tunnel>→overlay`. `ip -6 route get <overlay-ula> iif <tunnel>`.
   - **Expected:** SNAT increments; FORWARD overlay is 0; route get shows the public NIC.
   - **On failure:** If FORWARD already carries return, this spec does not apply.
2. **P2 — One ip6tables path.**
   - **Action:** Remove extra nft MASQUERADE on `<gcp-nic>` or the VPS NIC. Keep mangle PREROUTING MARK and MASQUERADE on the **tunnel** in ip6tables only ([OEN-S27](../supporting/s27-iptables-nft-mark-before-fib.md)).
   - **Expected:** No duplicate masquerade. One tool family.
   - **On failure:** Do not add more NAT to “help.”
3. **P3 — Install overlay ULA /48 on table 52 and main.**
   - **Action:** `ip -6 route` in table 52 and main. Add the overlay ULA `/48` via the overlay iface on **both** if missing.
   - **Expected:** `ip -6 route get <overlay-ula> iif <tunnel>` now enters overlay, not the public NIC.
   - **On failure:** Restarting overlay alone does not install the prefix — add the route.
4. **P4 — Soak IPv6 from a LAN Pi.**
   - **Action:** On `<overlay-peer>`, select `<exit-node>`, `curl -6 https://example.com`, then clear the exit.
   - **Expected:** HTTP 200. Egress is the cloud, not the home tunnel.
   - **On failure:** If v4 works and v6 leaks home on Wi-Fi, see [OEN-20](20-lan-ula-happy-eyeballs-leak.md) / [OEN-S26](../supporting/s26-wifi-vs-cellular-underlay.md).

## Expected samples

```text
# Trap: mark counters up, route still WAN
<overlay-ula> from :: via <link-local> dev <wan-iface> src <gua>

# After /48 on table 52 and main
<overlay-ula> from :: dev <overlay-tun> src <overlay-v6>
```

## Verify

- FORWARD tunnel→overlay increments on v6 return.
- ULA /48 exists on table 52 and main.
- No split nft+ip6tables MASQUERADE.
- example.com 200 over IPv6 through the exit from a non-workstation client.
- ICMP / small ping success was **not** used as the pass criterion when this spec names TCP, SSH, or HTTPS.
- Bind table was filled by a human before any live `ip` / nft / iptables change.

## MUST NOT

- MUST NOT publish real overlay ULA node addresses.
- MUST NOT split nft mark and ip6tables MASQUERADE.
- MUST NOT add a second IPv6 MASQUERADE on the public NIC ([OEN-17](17-gcp-overlay-exit.md)).
- MUST NOT test from the agent workstation ([OEN-S18](../supporting/s18-do-not-set-exit-on-agent-workstation.md)).
- MUST NOT apply live network or firewall changes until Bind is filled by a human.
- MUST NOT claim a fix on ICMP ping alone when Verify names TCP, SSH, or HTTPS.
- MUST NOT publish hostnames, addresses, ULAs, or custom ports.

## Related specs

- [OEN-17 Google Cloud overlay exit](17-gcp-overlay-exit.md)
- [OEN-S27 iptables-nft MARK before FIB](../supporting/s27-iptables-nft-mark-before-fib.md)
- [OEN-S32 DNS leak-test vs data plane](../supporting/s32-dns-leak-test-not-v6-dataplane.md)
- [OEN-13 Overlay vs underlay vs unique-local](13-overlay-underlay-ula-layers.md)

## Prior art (Not novel)

Policy routing and table 52 appear in overlay exit docs. This spec’s claim is netfilter-off + nft mark missing the first FIB lookup + missing v6 /48 + split MASQUERADE as one failure cluster.

