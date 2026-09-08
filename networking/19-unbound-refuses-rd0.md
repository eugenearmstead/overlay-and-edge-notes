---
id: "OEN-19"
title: "Local Unbound REFUSES overlay peer-API queries with Recursion Desired off"
kind: "original"
status: "active"
edition: 2
date_published: "2026-09-08"
author: "Eugene Armstead"
author_url: "https://www.armsteadent.com/"
canonical: "https://eugenearmstead.github.io/overlay-and-edge-notes/networking/19-unbound-refuses-rd0.html"
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
backs:
  []
backed_by:
  - OEN-05
  - OEN-14
description: "Exit peer-API DNS over HTTPS sends Recursion Desired off. dnsmasq pointed at loopback Unbound returns REFUSED, which looks like Unbound is down."
terms:
  - abbr: API
    expansion: application programming interface
  - abbr: CLI
    expansion: command-line interface
  - abbr: ControlPath
    expansion: OpenSSH multiplexing socket path option
  - abbr: DNS
    expansion: Domain Name System
  - abbr: dnsmasq
    expansion: lightweight DNS forwarder and DHCP server
  - abbr: DoH
    expansion: DNS over HTTPS
  - abbr: HTTPS
    expansion: Hypertext Transfer Protocol Secure
  - abbr: LAN
    expansion: Local Area Network
  - abbr: NOERROR
    expansion: DNS response code meaning the query succeeded
  - abbr: OEN
    expansion: Overlay and Edge Notes
  - abbr: PeerAPI
    expansion: overlay peer application-programming interface (exit DNS over HTTPS)
  - abbr: Pi
    expansion: single-board computer (Raspberry Pi class)
  - abbr: RD
    expansion: Recursion Desired (DNS flag)
  - abbr: REFUSED
    expansion: DNS response code meaning the server will not answer
  - abbr: REFUSES
    expansion: DNS response code meaning the server will not answer
  - abbr: SSH
    expansion: Secure Shell
  - abbr: Unbound
    expansion: validating recursive DNS resolver
  - abbr: VM
    expansion: virtual machine
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
| `<overlay-impl>` | Overlay implementation class | `tailscale-compatible` or other — stop and translate CLI |
| `<user>` | SSH user | Guest account |
| `<exit-node>` | Overlay exit node | Cloud VM or LAN Pi |
| `<overlay-peer>` | Soak client (not the agent workstation) | LAN Pi or phone |

## Formulas

`dig +norecurse` is RD=0. PeerAPI DoH uses RD=0. Local Unbound MAY refuse that.

## Decision

An RD-stub MUST force RD=1 **before** Unbound ([OEN-05](05-exit-peerapi-dns-stub.md)). Verify with `dig +norecurse @127.0.0.1` versus RD=1, then PeerAPI DoH rcode from a non-exit client.

## Consequences

- PeerAPI starts answering without replacing Unbound.
- Operators stop restarting Unbound for a flag mismatch.
- Remote-upstream confusion goes away.

## Agent stop rule

> MUST emit bound Unbound/dnsmasq RD=0 queries after Bind is filled.
> MUST NOT set `accept-dns=true` on a cloud exit to hide REFUSED.
> MUST NOT apply netfilter from this page.

## Procedure

This spec does not apply if `<overlay-impl>` is not tailscale-compatible.

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

## MUST NOT

- MUST NOT restart Unbound as the first “DNS down” fix when RD=0 is REFUSED.
- MUST NOT send PeerAPI at overlay :53.
- MUST NOT set accept-dns=true on the exit VM to hide this.
- MUST NOT publish PeerAPI URLs with real overlay addresses.
- MUST NOT publish hostnames, addresses, ULAs, or custom ports.

## Page changelog

- Edition 2 (8 Sep 2026, Mountain Time): Trap-specific Bind and agent stop rule (review cleanup).

## Related specs

- [OEN-05 Exit PeerAPI DNS stub](05-exit-peerapi-dns-stub.md)
- [OEN-14 Exit app DNS is PeerAPI](14-exit-dns-is-peerapi.md)
- [OEN-23 Cloud-exit accept-dns](23-cloud-exit-accept-dns.md)

## Prior art (Not novel)

Unbound default recurse policy is documented. This spec’s claim is PeerAPI RD=0 plus dnsmasq-to-loopback as a false “Unbound down.”

