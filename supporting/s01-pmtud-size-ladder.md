---
id: OEN-S01
title: Don't-fragment ping size ladder (path MTU discovery)
kind: supporting
status: active
edition: 2
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
description: Measure path MTU with don't-fragment ping size ladders on IPv4 and IPv6. Small ICMP can succeed while large TCP still dies.
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
  - abbr: ICMPv6
    expansion: Internet Control Message Protocol version 6
  - abbr: TEST-NET-3
    expansion: RFC 5737 documentation IPv4 prefix 203.0.113.0/24
  - abbr: RFC
    expansion: Request for Comments
  - abbr: AAAA
    expansion: DNS IPv6 address record
  - abbr: Chromium
    expansion: open-source browser engine
  - abbr: ControlPath
    expansion: OpenSSH multiplexing socket path option
  - abbr: nft
    expansion: nftables (Linux packet filter)
---

# Don't-fragment ping size ladder (path MTU discovery)

## Context

This is a **method**, not an original trap. It is how [OEN-01](../networking/01-overlay-ssh-byte-cliff.md) proved overlay Secure Shell (SSH) cliffs, and how [OEN-02](../networking/02-chromium-tls-pmtu.md) / [OEN-04](../networking/04-exit-tcpmss-after-ts-forward.md) separate “Internet Control Message Protocol (ICMP) looks fine” from “Transmission Control Protocol (TCP) is blackholed.”

ICMP echo with the don't-fragment (DF) bit set (`ping -M do` on Linux IPv4; `ping -6 -M do` on IPv6) tells you the largest **Internet Protocol (IP) packet** that path will carry. TCP Maximum Segment Size (MSS) and Transport Layer Security (TLS) ClientHello size are different. **Small ICMP can succeed while large TCP dies.** A 56-byte ping MUST NOT be recorded as “path MTU is fine.”

## Topology

Measure **three classes of target** from the same client. Do not mix the numbers.

```text
[client]
    |
    +-- path A: clear WAN --> <vps-public-v4> / <vps-public-v6>
    +-- path B: overlay --> <overlay-v4> / <overlay-v6>   (of <cloud-vps>)
    +-- path C: through <wg-iface> --> a public HTTPS target (general internet)

[consumer router]
    +-- <lan-bridge>  MTU 1500
    +-- <wg-iface>    commercial WireGuard (measure <wg-mtu>)
    +-- <wan-iface>
```

## Bind

| Placeholder | Operator fills | Class |
|-------------|----------------|-------|
| `<wg-iface>` | Commercial WireGuard iface | Router or client |
| `<wg-mtu>` | MTU from `ip link show <wg-iface>` | Integer |
| `<lan-bridge>` | LAN bridge | Router |
| `<vps-public-v4>` / `<vps-public-v6>` | Cloud VPS public addresses | WAN; never publish |
| `<overlay-v4>` / `<overlay-v6>` | Overlay addresses of `<cloud-vps>` | Overlay; never publish |
| `<https-v4>` / `<https-v6>` | A public HTTPS origin used only as a ping/TCP target | Public; example.com is fine |

## Formulas

```text
# IPv4: IP size ≈ ICMP payload + 28   (20-byte IPv4 + 8-byte ICMP)
# IPv6: IP size ≈ ICMPv6 payload + 48 (40-byte IPv6 + 8-byte ICMPv6)

# Linux ping -s is PAYLOAD, not IP size.
# To probe a 1500-byte IPv4 packet:  ping -M do -s 1472
# To probe a 1500-byte IPv6 packet:  ping -6 -M do -s 1452

# Compare max successful IP size to <wg-mtu> and to TCP MSS:
#   mss4 = <wg-mtu> - 40
#   mss6 = <wg-mtu> - 60
# See [OEN-01](../networking/01-overlay-ssh-byte-cliff.md). Historical 1160 is not this formula.
```

## Method

Pick a destination that represents the path under test (VPS public address, overlay address, or a public resolver **through** the tunnel). Binary-search or step down from a LAN-sized payload until DF ping succeeds. Record the **largest successful payload**, the **implied IP size**, and the path (WAN vs `<wg-iface>` vs overlay).

Do this **before** blaming the overlay SSH binary, Chromium, or an exit node. Then **retest TCP**.

## Consequences

- You get a number you can compare to tunnel MTU and to TCPMSS.
- You stop treating a working 56-byte ping as proof of a working HTTPS or 3 KB SSH path.

## Agent stop rule

> MUST emit a bound ladder (IPv4 and IPv6 commands with targets filled).  
> MUST NOT change LAN MTU, iptables, or nft to “make the ladder green.”  
> MUST NOT stop after ICMP success — retest the TCP symptom the original spec names.  
> MUST NOT publish the real addresses pinged.

## Procedure

1. **P1 — Note interface MTUs.**
   - **Action:**

     ```bash
     ip -o link show
     ip link show <lan-bridge>
     ip link show <wg-iface>
     ```

   - **Expected:** LAN often 1500; commercial WireGuard often ~1320; overlay tun in the same neighborhood. Record `<wg-mtu>` as an integer.
   - **On failure:** If you cannot see the tunnel iface, you are not measuring the path you think you are.

2. **P2 — IPv4 DF ladder to the target.**
   - **Action:** From the client (replace `<target>` with one bound address). `-M do` is don't-fragment.

     ```bash
     ping -c1 -W2 -M do -s 1472 <target>   # ~1500 IPv4 IP — often fails via a tunnel
     ping -c1 -W2 -M do -s 1292 <target>   # ~1320 IPv4 IP
     ping -c1 -W2 -M do -s 1172 <target>   # safer under 1320 plus extra overhead
     ping -c1 -W2 -M do -s 56 <target>     # tiny — MUST NOT be the only sample
     ```

     Step by 20–40 bytes around the failure point until you have the largest success. Implied IPv4 IP size ≈ payload + 28.
   - **Expected:** A clear max payload. Failure is `message too long` or 100% loss with DF set; success is a reply.
   - **On failure:** If even 500-byte DF fails, check routing and whether DF is stripped. Try without `-M do` to see if the host is reachable at all.

3. **P3 — IPv6 DF ladder to the target.**
   - **Action:** Same idea with ICMPv6. Payload 1452 ≈ 1500 IPv6 IP.

     ```bash
     ping -6 -c1 -W2 -M do -s 1452 <target>
     ping -6 -c1 -W2 -M do -s 1272 <target>   # ~1320 IPv6 IP
     ping -6 -c1 -W2 -M do -s 1152 <target>
     ping -6 -c1 -W2 -M do -s 56 <target>
     ```

     Implied IPv6 IP size ≈ payload + 48. If the target has no AAAA, skip IPv6 for **that** target and say so; do not invent v6 success.
   - **Expected:** A max payload for IPv6, or a documented skip (no AAAA / no v6 route).
   - **On failure:** `ping: unknown host` or `Network is unreachable` means this ladder does not apply to that family — record it; do not call it a PMTUD cliff.

4. **P4 — Compare paths, not just sizes.**
   - **Action:** Repeat P2 and P3 toward (a) `<vps-public-v4>` / `<vps-public-v6>`, (b) `<overlay-v4>` / `<overlay-v6>`, (c) `<https-v4>` **while traffic uses** `<wg-iface>`.
   - **Expected:** Double encapsulation ([OEN-01](../networking/01-overlay-ssh-byte-cliff.md)) shows public-address DF via the tunnel stuck ~100 bytes under `<wg-mtu>`, while clear WAN to the same public address is larger.
   - **On failure:** If all three ladders match, the bottleneck is elsewhere (MSS, not underlay).

5. **P5 — Do not stop at ICMP.**
   - **Action:** After a successful mid-size ping, retry the **TCP** symptom (overlay SSH 3 KB with `ControlPath=none`, or curl vs Chromium).
   - **Expected:** You now know whether ICMP size predicts TCP. Often it does not: TLS ClientHello or SSH output is larger than the ping you tried.
   - **On failure:** If ping is large and TCP still dies, look at TCPMSS scope ([OEN-01](../networking/01-overlay-ssh-byte-cliff.md) P6) or ICMP-blackholed PMTUD ([OEN-S02](s02-clamp-mss-to-pmtu-noop.md)).

## Expected samples

```text
# IPv4 DF fail (payload too large)
PING 203.0.113.10 (203.0.113.10) 1472(1500) bytes of data.
ping: local error: message too long, mtu=1320

# IPv4 DF success (example payload 1292 → ~1320 IP)
PING 203.0.113.10 (203.0.113.10) 1292(1320) bytes of data.
1300 bytes from 203.0.113.10: icmp_seq=1 ttl=54 time=17.4 ms
--- 203.0.113.10 ping statistics ---
1 packets transmitted, 1 received, 0% packet loss

# IPv6 DF fail
ping: local error: message too long, mtu=1320

# Tiny ping success — NOT a path-MTU pass
64 bytes from 203.0.113.10: icmp_seq=1 ttl=54 time=16.1 ms
```

Documentation samples use `TEST-NET-3` `203.0.113.10` (RFC 5737). Operators MUST ping their bound targets, never publish those targets.

## Verify

- You recorded max DF payload **and** implied IP size for IPv4 and (if present) IPv6, for each path class (public vs overlay vs through-tunnel).
- LAN MTU was not changed as part of the measurement.
- A tiny ping success was not used as “path MTU is fine.”
- The calling spec’s TCP/SSH/HTTPS check was re-run.

## MUST NOT

- MUST NOT treat working small ping/DNS/curl as proof “not MTU.”
- MUST NOT shrink the LAN bridge to the tunnel MTU in order to make this ladder green.
- MUST NOT publish the real addresses you pinged; write `<cloud-vps>` / “VPS public address.”
- MUST NOT skip the TCP retest after ICMP succeeds.
- MUST NOT skip IPv6 when the path under test is dual-stack.

## Related specs

- [OEN-01 Overlay SSH byte cliff](../networking/01-overlay-ssh-byte-cliff.md)
- [OEN-02 Chromium TLS vs curl](../networking/02-chromium-tls-pmtu.md)
- [OEN-04 Exit-node TCPMSS](../networking/04-exit-tcpmss-after-ts-forward.md)
- [OEN-S02 clamp-mss-to-pmtu no-op](s02-clamp-mss-to-pmtu-noop.md)

## Prior art (Not novel)

Don't-fragment ping ladders are standard path MTU discovery (PMTUD) practice. This note exists so agents **run IPv4 and IPv6 on the right addresses** (public vs overlay vs through-tunnel) and then **retest TCP**, which is the step most runbooks omit.
