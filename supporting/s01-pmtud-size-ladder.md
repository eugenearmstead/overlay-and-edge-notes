---
id: OEN-S01
title: Don't-fragment ping size ladder (path MTU discovery)
kind: supporting
status: active
edition: 1
date_published: 2026-09-07
author: Eugene Armstead
author_url: https://www.armsteadent.com/
canonical: https://eugenearmstead.github.io/overlay-and-edge-notes/supporting/s01-pmtud-size-ladder.html
keywords:
  - pmtud
  - df-ping
  - path-mtu
backs:
  - OEN-01
  - OEN-02
  - OEN-04
backed_by: []
description: Measure path MTU with don't-fragment ping size ladders. Small ICMP can succeed while large TCP still dies.
terms:
  - abbr: OEN
    expansion: Overlay and Edge Notes
  - abbr: DF
    expansion: don't-fragment (IP flag)
  - abbr: PMTUD
    expansion: path MTU discovery
  - abbr: MTU
    expansion: Maximum Transmission Unit
  - abbr: ICMP
    expansion: Internet Control Message Protocol
  - abbr: TCP
    expansion: Transmission Control Protocol
  - abbr: MSS
    expansion: Maximum Segment Size
  - abbr: TCPMSS
    expansion: iptables/nft target that sets TCP Maximum Segment Size
  - abbr: TLS
    expansion: Transport Layer Security
  - abbr: SSH
    expansion: Secure Shell
  - abbr: IP
    expansion: Internet Protocol
  - abbr: IPv4
    expansion: Internet Protocol version 4
  - abbr: IPv6
    expansion: Internet Protocol version 6
  - abbr: LAN
    expansion: Local Area Network
  - abbr: WAN
    expansion: Wide Area Network
  - abbr: VPN
    expansion: Virtual Private Network
  - abbr: WG
    expansion: WireGuard
  - abbr: WireGuard
    expansion: UDP-based VPN protocol
  - abbr: VPS
    expansion: Virtual Private Server
  - abbr: DNS
    expansion: Domain Name System
  - abbr: HTTPS
    expansion: Hypertext Transfer Protocol Secure
  - abbr: ClientHello
    expansion: TLS handshake message sent by the client
  - abbr: KB
    expansion: kilobyte
  - abbr: UDP
    expansion: User Datagram Protocol
---

# Don't-fragment ping size ladder (path MTU discovery)

## Context

This is a **method**, not an original trap. It is how [OEN-01](../networking/01-overlay-ssh-byte-cliff.md) proved overlay Secure Shell (SSH) cliffs, and how forthcoming OEN-02 / OEN-04 separate “Internet Control Message Protocol (ICMP) looks fine” from “Transmission Control Protocol (TCP) is blackholed.”

ICMP echo with the don't-fragment (DF) bit set (`ping -M do` on Linux) tells you the largest **Internet Protocol (IP) packet** that path will carry. TCP Maximum Segment Size (MSS) and Transport Layer Security (TLS) ClientHello size are different. **Small ICMP can succeed while large TCP dies.**

IPv4: IP size ≈ payload + 28 (20 IP + 8 ICMP).  
IPv6: IP size ≈ payload + 48 (40 IPv6 + 8 ICMPv6) when using `ping -6 -M do -s`.

## Method

Pick a destination that represents the path under test (Virtual Private Server (VPS) public address, overlay address, or a public resolver **through** the tunnel). Binary-search or step down from 1472 until DF ping succeeds. Record the **largest successful payload** and the path (Wide Area Network (WAN) vs `<wg-iface>` vs overlay).

Do this **before** blaming the overlay SSH binary, Chromium, or an exit node.

## Consequences

- You get a number you can compare to tunnel MTU and to TCPMSS.
- You stop treating a working 56-byte ping as proof of a working HTTPS or 3 KB SSH path.

## Procedure

Placeholders: `<cloud-vps>` public address, overlay address, `<wg-iface>`.

1. **P1 — Note interface MTUs.**
   - **Action:** `ip link show` on the client (and on the router if you have it). Record Local Area Network (LAN)/bridge vs `<wg-iface>` vs overlay tun.
   - **Expected:** LAN often 1500; commercial WireGuard often ~1320; overlay tun in the same neighborhood. Exact numbers vary.
   - **On failure:** If you cannot see the tunnel iface, you are not measuring the path you think you are.

2. **P2 — IPv4 DF ladder to the target.**
   - **Action:** From the client:

     ```bash
     ping -c1 -M do -s 1472 <target>   # ~1500 IP — often fails via a tunnel
     ping -c1 -M do -s 1292 <target>   # ~1320 IP
     ping -c1 -M do -s 1172 <target>   # safer under 1320 plus overhead
     ```

     Step by 20–40 bytes around the failure point until you have the largest success.

   - **Expected:** A clear max payload. Failure is `message too long` or 100% loss with DF set; success is a reply.
   - **On failure:** If even 500-byte DF fails, check routing and whether DF is stripped. Try without `-M do` to see if the host is reachable at all.

3. **P3 — Compare paths, not just sizes.**
   - **Action:** Repeat P2 toward (a) the cloud VPS **public** address, (b) the **overlay** address of `<cloud-vps>`, (c) a general internet target **while traffic uses** `<wg-iface>`.
   - **Expected:** Double encapsulation ([OEN-01](../networking/01-overlay-ssh-byte-cliff.md)) shows public-address DF via the tunnel stuck ~100 bytes under tunnel MTU, while clear WAN to the same public address is larger.
   - **On failure:** If all three ladders match, the bottleneck is elsewhere (MSS, not underlay).

4. **P4 — Do not stop at ICMP.**
   - **Action:** After a successful mid-size ping, retry the **TCP** symptom (overlay SSH 3 KB, or a browser vs curl).
   - **Expected:** You now know whether ICMP size predicts TCP. Often it does not: TLS ClientHello or SSH output is larger than the ping you tried.
   - **On failure:** If ping is large and TCP still dies, look at TCPMSS scope (OEN-01 P6) or ICMP-blackholed PMTUD (forthcoming OEN-S02).

## Verify

- You recorded max DF payload for each path with the command and target class (public vs overlay vs through-tunnel).
- LAN MTU was not changed as part of the measurement.
- A tiny ping success was not used as “path MTU is fine.”

## MUST NOT

- MUST NOT treat working small ping/DNS/curl as proof “not MTU.”
- MUST NOT shrink the LAN bridge to the tunnel MTU in order to make this ladder green.
- MUST NOT publish the real addresses you pinged; write `<cloud-vps>` / “VPS public address.”
- MUST NOT skip the TCP retest after ICMP succeeds.

## Related specs

- [OEN-01 Overlay SSH byte cliff](../networking/01-overlay-ssh-byte-cliff.md) (built)
- OEN-02 Chromium TLS vs curl (forthcoming)
- OEN-04 exit-node TCPMSS (forthcoming)
- OEN-S02 clamp-mss-to-pmtu no-op (forthcoming)

## Prior art (Not novel)

Don't-fragment ping ladders are standard path MTU discovery (PMTUD) practice. This note exists so agents **run it on the right addresses** (public vs overlay vs through-tunnel) and then **retest TCP**, which is the step most runbooks omit.
