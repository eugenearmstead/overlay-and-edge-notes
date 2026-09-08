---
id: "OEN-05"
title: "Exit-node overlay peer-API DNS stub (loopback only)"
kind: "original"
status: "active"
edition: 2
date_published: "2026-09-08"
author: "Eugene Armstead"
author_url: "https://www.armsteadent.com/"
canonical: "https://eugenearmstead.github.io/overlay-and-edge-notes/networking/05-exit-peerapi-dns-stub.html"
keywords:
  - "PeerAPI DNS"
  - "exit-node PeerAPI stub"
  - "PeerAPIURL dynamic port"
  - "Android exit DNS DoH"
  - "bind stub overlay :53 breaks exit"
  - "loopback DNS stub RD=1"
  - "tailscale status PeerAPIURL"
  - "UDP recv-Q PeerAPI"
  - "exit DNS not :53"
  - "Headscale PeerAPI"
  - "Recursion Desired stub"
  - "DoH dns-query exit"
backs:
  []
backed_by:
  - OEN-S29
  - OEN-19
description: "Android exit DNS is overlay peer-API DNS over HTTPS on a dynamic port. A loopback stub that forces Recursion Desired works; binding the stub on the overlay address:53 breaks all exit."
terms:
  - abbr: Android
    expansion: mobile operating system
  - abbr: API
    expansion: application programming interface
  - abbr: CLI
    expansion: command-line interface
  - abbr: ControlPath
    expansion: OpenSSH multiplexing socket path option
  - abbr: DNS
    expansion: Domain Name System
  - abbr: DoH
    expansion: DNS over HTTPS
  - abbr: HTTP
    expansion: Hypertext Transfer Protocol
  - abbr: HTTPS
    expansion: Hypertext Transfer Protocol Secure
  - abbr: IPv4
    expansion: Internet Protocol version 4
  - abbr: IPv6
    expansion: Internet Protocol version 6
  - abbr: JSON
    expansion: JavaScript Object Notation
  - abbr: KB
    expansion: kilobyte
  - abbr: LAN
    expansion: Local Area Network
  - abbr: nft
    expansion: nftables (Linux packet filter)
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
  - abbr: TCP
    expansion: Transmission Control Protocol
  - abbr: UDP
    expansion: User Datagram Protocol
  - abbr: Unbound
    expansion: validating recursive DNS resolver
  - abbr: UNCONN
    expansion: ss(8) unconnected socket state
  - abbr: URL
    expansion: Uniform Resource Locator
  - abbr: VM
    expansion: virtual machine
---

# Exit-node overlay peer-API DNS stub (loopback only)

## Context

Phone clients using an `<exit-node>` do not talk to a hardcoded `:53` or a guessed high port. Exit application Domain Name System (DNS) is DNS over HTTPS (DoH) to the overlay **peer application-programming interface (PeerAPI)** on a **dynamic** port (`PeerAPIURL` in `tailscale status --json`).

A local stub that listens on `127.0.0.1:53` and forwards with Recursion Desired (RD)=1 is the right shape when the exit’s local resolver would otherwise refuse RD=0 ([OEN-19](19-unbound-refuses-rd0.md)). Binding that stub on the **overlay address:53** broke **all** exit in the field.

Under phone load, a single-threaded `select()` stub that calls upstream synchronously filled the User Datagram Protocol (UDP) receive queue (~160 KB) and cellular DNS died. Thread pool plus upstream timeout fixed it ([OEN-S29](../supporting/s29-peerapi-stub-event-loop.md)).

## Topology

```text
[phone] --HTTPS DoH-->  http://<exit-node>:<ephemeral>/dns-query   (PeerAPI)
[<exit-node>]
    stub MUST bind 127.0.0.1:53 only  -->  upstream with RD=1
    MUST NOT bind overlay:53  (broke all exit in the field)
    select() MUST NOT call upstream synchronously  ([OEN-S29](../supporting/s29-peerapi-stub-event-loop.md))
```

## Bind

Fill this table **before** any live change. Do **not** paste real values back into public notes.

| Placeholder | Operator fills | Class |
|-------------|----------------|-------|
| `<overlay-impl>` | Overlay implementation class | `tailscale-compatible` or other — stop and translate CLI |
| `<user>` | SSH user | Guest account |
| `<exit-node>` | Overlay exit node | Cloud VM or LAN Pi |
| `<overlay-v4>` | Overlay IPv4 of the node under test | Overlay; never publish |
| `<peerapi-port>` | Dynamic overlay peer-API port | Ephemeral; never publish as a lab fingerprint |
| `<overlay-peer>` | Soak client (not the agent workstation) | LAN Pi or phone |
| `<exit>` | Operator fills from this procedure | Local |
| `<ephemeral>` | Peer-API listen port from status JSON | Ephemeral |

## Formulas

PeerAPI port is **dynamic**. Read it from overlay status JSON (`PeerAPIURL`). Do not hardcode 53 or a lab debug port.

## Decision

The exit DNS stub MUST listen on loopback only. It MUST force RD=1 toward the local resolver. It MUST NOT bind overlay `:53`.

The stub MUST NOT block the event loop on a synchronous upstream. Verify IPv6 **data** on a leak test, not DNS alone ([OEN-S32](../supporting/s32-dns-leak-test-not-v6-dataplane.md)).

## Consequences

- Phones can resolve through the exit.
- Binding mistakes no longer blackhole the node.
- Cellular DNS survives burst load.

## Agent stop rule

> MUST emit bound `tailscale status --json` / PeerAPIURL commands only after `<overlay-impl>` is `tailscale-compatible`.
> MUST NOT apply live nft or iptables from this DNS-stub page.
> MUST NOT file an overlay-product bug until loopback-only and RD=1 are evidenced.
> MUST NOT publish PeerAPI URLs or custom ports.

## Procedure

This spec does not apply if `<overlay-impl>` is not tailscale-compatible.

### Copy-paste commands (after Bind)

```bash
ssh -o ControlPath=none <user>@<exit-node> 'ss -ulnp | grep -E ":53|:dns"'
# Expect 127.0.0.1:53 for the stub, not overlay-v4:53.

# From a NON-exit client:
curl -sS --max-time 8 "http://<overlay-v4>:<peerapi-port>/dns-query" -H 'content-type: application/dns-message' --data-binary @- </dev/null | wc -c
# Or the overlay CLI equivalent that prints PeerAPIURL.

ss -u -n | awk 'NR==1 || /:53/'
```

If UDP recv-Q grows under phone load, follow [OEN-S29](../supporting/s29-peerapi-stub-event-loop.md).

1. **P1 — Read the live PeerAPI URL.**
   - **Action:** On `<exit-node>`, `tailscale status --json` (or equivalent) and note `PeerAPIURL`. It is HTTP DoH on an ephemeral port, not `:53`.
   - **Expected:** A URL on the overlay address with a high port.
   - **On failure:** If PeerAPI is down, heal the overlay DNS process — do not restart the coordinator ([OEN-14](14-exit-dns-is-peerapi.md)).
2. **P2 — Confirm the stub binds loopback only.**
   - **Action:** `ss` / `netstat` for UDP/TCP 53. The stub MUST show `127.0.0.1:53` (and optionally `::1`), not the overlay address.
   - **Expected:** Listen address is loopback.
   - **On failure:** If it is on the overlay address, stop the stub, rebind loopback, restart. Expect exit to recover.
3. **P3 — Forward with RD=1.**
   - **Action:** From the exit, `dig +norecurse @127.0.0.1 example.com` vs `dig @127.0.0.1 example.com`. The stub MUST turn RD on before Unbound (or equivalent).
   - **Expected:** RD=0 without the stub is REFUSED ([OEN-19](19-unbound-refuses-rd0.md)); through the stub, queries answer.
   - **On failure:** Do not point PeerAPI at loopback Unbound with RD=0.
4. **P4 — Load: receive queue must not grow.**
   - **Action:** During a phone soak, watch UDP recv-Q on the stub socket. If it climbs, the event loop is blocked ([OEN-S29](../supporting/s29-peerapi-stub-event-loop.md)).
   - **Expected:** recv-Q stays near 0. Cellular DNS keeps working.
   - **On failure:** Add a thread pool and upstream timeout; do not add more `select()` handlers that call network inline.
5. **P5 — Verify from a non-exit client.**
   - **Action:** From `<overlay-peer>` using the exit, fetch `http://<exit>:<ephemeral>/dns-query` (DoH) and `curl -6 https://example.com`.
   - **Expected:** DoH rcode NOERROR; IPv6 HTTP 200.
   - **On failure:** DNS-only success is not enough.

## Expected samples

```text
# Good listen
udp  UNCONN  0  0  127.0.0.1:53  0.0.0.0:*

# Bad listen (this spec)
udp  UNCONN  0  0  <overlay-v4>:53  0.0.0.0:*
```

## Verify

- PeerAPIURL is live; stub is loopback-only.
- RD=0 to Unbound REFUSED; RD=1 via stub answers.
- UDP recv-Q does not grow under phone load.
- IPv6 HTTP through the exit works, not only DNS.

## MUST NOT

- MUST NOT bind the DNS stub on the overlay address:53.
- MUST NOT assume PeerAPI is :53 or a fixed high port.
- MUST NOT claim exit DNS is healed from a leak-test name alone.
- MUST NOT restart the coordinator to “fix DNS.”
- MUST NOT publish hostnames, addresses, ULAs, or custom ports.

## Page changelog

- Edition 2 (8 Sep 2026, Mountain Time): Trap-specific Bind and agent stop rule (review cleanup).

## Related specs

- [OEN-14 Exit app DNS is PeerAPI](14-exit-dns-is-peerapi.md)
- [OEN-19 Unbound REFUSES RD=0](19-unbound-refuses-rd0.md)
- [OEN-S29 PeerAPI stub event-loop](../supporting/s29-peerapi-stub-event-loop.md)
- [OEN-S32 DNS leak-test vs data plane](../supporting/s32-dns-leak-test-not-v6-dataplane.md)

## Prior art (Not novel)

“Use local DNS for exit” is in public overlay docs. They rarely say loopback-only, dynamic PeerAPI port, RD=1, and non-blocking upstream as one contract.

