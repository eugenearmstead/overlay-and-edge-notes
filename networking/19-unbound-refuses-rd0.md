---
id: OEN-19
title: "Local Unbound REFUSES overlay peer-API queries with Recursion Desired off"
kind: original
status: active
edition: 1
date_published: 2026-09-08
author: Eugene Armstead
author_url: https://www.armsteadent.com/
canonical: https://eugenearmstead.github.io/overlay-and-edge-notes/networking/19-unbound-refuses-rd0.html
keywords:
  - "Unbound REFUSES RD=0"
  - "PeerAPI Recursion Desired off"
  - "dnsmasq loopback Unbound REFUSED"
  - "dig +norecurse REFUSED"
  - "RD-stub before Unbound"
  - "looks like Unbound is down"
  - "exit DoH RD=0"
  - "local upstream RD=0 refuse"
  - "Headscale PeerAPI Unbound"
  - "force RD=1 stub"
  - "dnsmasq remote RD=0 works"
  - "PeerAPI DNS REFUSED"
backs: []
backed_by:
  - OEN-05
  - OEN-14
description: "Exit peer-API DNS over HTTPS sends Recursion Desired off. dnsmasq pointed at loopback Unbound returns REFUSED, which looks like Unbound is down."
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
  - abbr: DNS
    expansion: Domain Name System
  - abbr: DoH
    expansion: DNS over HTTPS
  - abbr: GCP
    expansion: Google Cloud Platform
  - abbr: VM
    expansion: virtual machine
  - abbr: NIC
    expansion: network interface card
  - abbr: API
    expansion: application programming interface
  - abbr: PeerAPI
    expansion: overlay peer application-programming interface (exit DNS over HTTPS)
  - abbr: RD
    expansion: Recursion Desired (DNS flag)
  - abbr: nft
    expansion: nftables (Linux packet filter)
  - abbr: ControlPath
    expansion: OpenSSH multiplexing socket path option
  - abbr: Pi
    expansion: single-board computer (Raspberry Pi class)
  - abbr: REFUSES
    expansion: DNS response code meaning the server will not answer
  - abbr: REFUSED
    expansion: DNS response code meaning the server will not answer
  - abbr: Unbound
    expansion: validating recursive DNS resolver
  - abbr: dnsmasq
    expansion: lightweight DNS forwarder and DHCP server
  - abbr: NOERROR
    expansion: DNS response code meaning the query succeeded
---

# Local Unbound REFUSES overlay peer-API queries with Recursion Desired off

## Context

Exit overlay peer-API (PeerAPI) DNS over HTTPS (DoH) sends Recursion Desired (RD)=0. When dnsmasq on the exit points at **loopback Unbound**, Unbound returns REFUSED. The same dnsmasq often forwards RD=0 to a *remote* upstream just fine. It looks like “Unbound is down.”

Public docs say “local DNS for exit.” They rarely document this **local-upstream RD=0 refuse**.

## Topology

```text
[PeerAPI DoH]  RD=0  -->  dnsmasq --> loopback Unbound  -->  REFUSED
Same dnsmasq forwarding RD=0 to a *remote* upstream often works
Looks like "Unbound is down"
FIX: RD-stub forces RD=1 before Unbound ([OEN-05](05-exit-peerapi-dns-stub.md))
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

`dig +norecurse` is RD=0. PeerAPI DoH uses RD=0. Local Unbound MAY refuse that.

## Decision

An RD-stub MUST force RD=1 **before** Unbound ([OEN-05](05-exit-peerapi-dns-stub.md)). Verify with `dig +norecurse @127.0.0.1` versus RD=1, then PeerAPI DoH rcode from a non-exit client.

## Consequences

- PeerAPI starts answering without replacing Unbound.
- Operators stop restarting Unbound for a flag mismatch.
- Remote-upstream confusion goes away.

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
ssh -o ControlPath=none <user>@<exit-node> 'dig +time=2 +norecurse @127.0.0.1 example.com; dig +time=2 @127.0.0.1 example.com'
```

1. **P1 — Prove RD=0 is REFUSED on loopback.**
   - **Action:** On `<exit-node>`: `dig +norecurse @127.0.0.1 example.com` and `dig @127.0.0.1 example.com`.
   - **Expected:** norecurse / RD=0 → REFUSED. RD=1 → answer (if Unbound is up).
   - **On failure:** If RD=1 is also REFUSED, Unbound really is down — fix that first.
2. **P2 — Compare a remote upstream.**
   - **Action:** Point a test dig RD=0 at a remote resolver the box is allowed to use. Many answer or recurse anyway.
   - **Expected:** Remote may work while loopback Unbound refuses — this is the trap.
   - **On failure:** Do not switch PeerAPI to a public resolver as the production fix.
3. **P3 — Insert the RD-stub.**
   - **Action:** Stub on 127.0.0.1:53 forces RD=1 then queries Unbound on another loopback port. PeerAPI keeps targeting local DNS. Bind loopback only ([OEN-05](05-exit-peerapi-dns-stub.md)).
   - **Expected:** PeerAPI DoH from `<overlay-peer>` is NOERROR.
   - **On failure:** Do not bind overlay :53.
4. **P4 — Do not pretty-print with accept-dns.**
   - **Action:** On cloud exits, leave `accept-dns=false` ([OEN-23](23-cloud-exit-accept-dns.md)).
   - **Expected:** RD=0 path still works.
   - **On failure:** Guest dns query metadata is not this path.

## Expected samples

```text
;; ->>HEADER<<- opcode: QUERY, rcode: REFUSED
```

## Verify

- dig +norecurse @127.0.0.1 without stub is REFUSED.
- Through stub / PeerAPI, queries answer.
- Stub is loopback-only.
- Unbound process was up the whole time.
- ICMP / small ping success was **not** used as the pass criterion when this spec names TCP, SSH, or HTTPS.
- Bind table was filled by a human before any live `ip` / nft / iptables change.

## MUST NOT

- MUST NOT restart Unbound as the first “DNS down” fix when RD=0 is REFUSED.
- MUST NOT send PeerAPI at overlay :53.
- MUST NOT set accept-dns=true on the exit VM to hide this.
- MUST NOT publish PeerAPI URLs with real overlay addresses.
- MUST NOT apply live network or firewall changes until Bind is filled by a human.
- MUST NOT claim a fix on ICMP ping alone when Verify names TCP, SSH, or HTTPS.
- MUST NOT publish hostnames, addresses, ULAs, or custom ports.

## Related specs

- [OEN-05 Exit PeerAPI DNS stub](05-exit-peerapi-dns-stub.md)
- [OEN-14 Exit app DNS is PeerAPI](14-exit-dns-is-peerapi.md)
- [OEN-23 Cloud-exit accept-dns](23-cloud-exit-accept-dns.md)

## Prior art (Not novel)

Unbound default recurse policy is documented. This spec’s claim is PeerAPI RD=0 plus dnsmasq-to-loopback as a false “Unbound down.”

