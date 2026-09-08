---
id: OEN-02
title: "Chromium TLS fails while curl returns 200"
kind: original
status: active
edition: 1
date_published: 2026-09-08
author: Eugene Armstead
author_url: https://www.armsteadent.com/
canonical: https://eugenearmstead.github.io/overlay-and-edge-notes/networking/02-chromium-tls-pmtu.html
keywords:
  - "curl 200 chrome ERR_CONNECTION_CLOSED"
  - "ERR_CONNECTION_CLOSED"
  - "Chromium TLS handshake fail"
  - "curl works browser fails"
  - "ClientHello too large"
  - "path MTU blackhole"
  - "Brave HTTPS closed"
  - "post-quantum ClientHello"
  - "WireGuard MTU"
  - "don't-fragment ping"
  - "TCPMSS"
  - "ICMP fragmentation needed"
  - "ERR_TIMED_OUT HTTPS"
  - "PMTUD blackhole"
backs: []
backed_by:
  - OEN-S01
  - OEN-S02
description: "Chromium HTTPS can close during handshake while curl still returns 200 because the browser ClientHello is larger than curl and path MTU discovery is blackholed."
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
  - abbr: VPN
    expansion: Virtual Private Network
  - abbr: KB
    expansion: kilobyte
  - abbr: TCP
    expansion: Transmission Control Protocol
  - abbr: UDP
    expansion: User Datagram Protocol
  - abbr: MSS
    expansion: Maximum Segment Size
  - abbr: TCPMSS
    expansion: iptables/nft target that sets TCP Maximum Segment Size
  - abbr: MTU
    expansion: Maximum Transmission Unit
  - abbr: ICMP
    expansion: Internet Control Message Protocol
  - abbr: PMTU
    expansion: path Maximum Transmission Unit
  - abbr: PMTUD
    expansion: path MTU discovery
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
  - abbr: nft
    expansion: nftables (Linux packet filter)
  - abbr: FORWARD
    expansion: netfilter/iptables forward chain
  - abbr: ClientHello
    expansion: TLS handshake message sent by the client
  - abbr: URL
    expansion: Uniform Resource Locator
  - abbr: Pi
    expansion: single-board computer (Raspberry Pi class)
  - abbr: QUIC
    expansion: Quick UDP Internet Connections
  - abbr: SYN
    expansion: TCP synchronize packet
  - abbr: Chromium
    expansion: open-source browser engine
  - abbr: Inter
    expansion: variable sans-serif font family
  - abbr: RST
    expansion: TCP reset flag
---

# Chromium TLS fails while curl returns 200

## Context

A Local Area Network (LAN) client can load a site with `curl` (Hypertext Transfer Protocol Secure (HTTPS) 200) while Brave or Chrome reports `ERR_CONNECTION_CLOSED` or a Transport Layer Security (TLS) handshake that never finishes. Internet Control Message Protocol (ICMP) ping and Domain Name System (DNS) may still look healthy.

Chromium post-quantum ClientHello messages (often about 1.5–1.9 kilobytes) are much larger than a typical curl/OpenSSL hello (about 0.5 KB). When the path Maximum Transmission Unit (MTU) is the commercial WireGuard tunnel (~1320) and ICMP path MTU discovery (PMTUD) is blackholed, those large Transmission Control Protocol (TCP) segments die while small curl still works.

This is **not** proof of a Chromium or overlay-product bug. Overlay with **no exit node selected** does not carry general web traffic. A **second** trap looks identical in the browser: consumer-router Virtual Private Network (VPN) DNS hijack ([OEN-03](03-router-vpn-dns-hijack.md)). Check DNS hijack **before** Maximum Segment Size (MSS).

## Topology

```text
[LAN client]  MTU 1500 (MUST stay)
    -->  <lan-bridge> 1500
    -->  <wg-iface>  <wg-mtu>  commercial WireGuard
    -->  internet HTTPS  (ICMP PMTUD often blackholed)

Overlay with **no exit selected** is NOT the general-web path.
A second trap that looks identical in the browser: DNS hijack ([OEN-03](03-router-vpn-dns-hijack.md)).
```

## Bind

Fill this table **before** any live change. Do **not** paste real values back into public notes.

| Placeholder | Operator fills | Class |
|-------------|----------------|-------|
| `<cloud-vps>` | Overlay SSH target | Cloud VPS |
| `<lan-pi>` | Overlay SSH target | LAN Pi |
| `<user>` | SSH user | Guest account |
| `<wg-iface>` | Commercial WireGuard iface | Router or VPS client |
| `<wan-iface>` | WAN iface | Router |
| `<lan-bridge>` | LAN bridge | Router (MTU 1500) |
| `<overlay-tun>` | Overlay tun iface | Node under test |
| `<wg-mtu>` | MTU integer from `ip link` | Measured |
| `<mss4>` / `<mss6>` | Computed MSS | Formulas |
| `<vps-public-v4>` / `<vps-public-v6>` | VPS public addresses | WAN; never publish |
| `<overlay-v4>` / `<overlay-v6>` | Overlay addresses | Overlay; never publish |


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

Operators MUST NOT treat working curl as “not MTU.” After DNS hijack is ruled out, curl-200 plus Chromium-fail MUST be treated as a path-MTU / MSS problem.

- The LAN bridge MUST stay **1500**. MSS clamping MUST be **only** on LAN↔VPN forward with an **explicit** `--set-mss` (not `--clamp-mss-to-pmtu`). See [OEN-S02](../supporting/s02-clamp-mss-to-pmtu-noop.md).
- Operators MUST NOT shrink the LAN bridge to the tunnel MTU “to fix browsing.” That hides Chromium symptoms and **breaks** overlay mesh underlay ([OEN-01](01-overlay-ssh-byte-cliff.md)).
- QUIC is a separate User Datagram Protocol (UDP) issue. Diagnose TCP size first.

## Consequences

- Chromium HTTPS starts completing once LAN↔VPN MSS is explicit and LAN stays 1500.
- Overlay large Secure Shell (SSH) stays healthy because the LAN was not shrunk.
- If Chromium still times out with overlay **off**, the next spec is DNS hijack, not another MSS pass.

## Agent stop rule

> A coding agent MUST emit a **bound runbook** (placeholders replaced from Bind).
> MUST NOT apply live `ip rule`, nft, iptables, ip6tables, sysctl, `wg set`, daemon restart, or deploy until a **human** filled Bind.
> MUST NOT claim a fix on ICMP ping alone when Verify names TCP, SSH, or HTTPS.
> MUST NOT file an upstream bug from this page.
> MUST NOT publish real addresses, hostnames, or custom ports.

## Procedure

Placeholders only until Bind is filled: `<cloud-vps>`, `<lan-pi>`, `<overlay-peer>`, `<exit-node>`, `<wg-iface>`, `<gcp-nic>`, plus the Bind extras on this page.

### Copy-paste commands (after Bind)

Copy-paste after Bind (IPv4 and IPv6). Do not clamp until DNS is honest ([OEN-03](03-router-vpn-dns-hijack.md)).

```bash
ip link show <lan-bridge>
ip link show <wg-iface>
# DF ladders: [OEN-S01](../supporting/s01-pmtud-size-ladder.md)
ping -c1 -W2 -M do -s 1472 <https-v4>
ping -6 -c1 -W2 -M do -s 1452 <https-v6>
curl -4 -sS -o /dev/null -w '%{http_code}\n' --connect-timeout 8 https://<https-host>
# Then open the same URL in Chromium. curl 200 is NOT a PMTU pass.

mss4=$((<wg-mtu> - 40)); mss6=$((<wg-mtu> - 60))
iptables -C FORWARD -i <lan-bridge> -o <wg-iface> -p tcp --tcp-flags SYN,RST SYN -j TCPMSS --set-mss "$mss4" \
  || iptables -I FORWARD -i <lan-bridge> -o <wg-iface> -p tcp --tcp-flags SYN,RST SYN -j TCPMSS --set-mss "$mss4"
ip6tables -C FORWARD -i <lan-bridge> -o <wg-iface> -p tcp --tcp-flags SYN,RST SYN -j TCPMSS --set-mss "$mss6" \
  || ip6tables -I FORWARD -i <lan-bridge> -o <wg-iface> -p tcp --tcp-flags SYN,RST SYN -j TCPMSS --set-mss "$mss6"
nft list ruleset | grep -i mss || true
```

1. **P1 — Rule out overlay exit and DNS hijack.**
   - **Action:** Confirm no exit node is selected for general web. Resolve the failing name with LAN DNS and with DNS over HTTPS. If LAN DNS hangs or returns sinkhole answers, stop and follow [OEN-03](03-router-vpn-dns-hijack.md) / [OEN-S24](../supporting/s24-lan-dns-sinkhole-0-0-0-0.md).
   - **Expected:** LAN DNS answers real addresses. Overlay is not the web path.
   - **On failure:** Do not clamp MSS until DNS is honest.
2. **P2 — Compare interface MTUs.**
   - **Action:** `ip link show` on the client (and the router if you have it). Record LAN/bridge vs `<wg-iface>`.
   - **Expected:** LAN often 1500; commercial WireGuard often ~1320.
   - **On failure:** If LAN was already set to the tunnel MTU, restore 1500 before continuing.
3. **P3 — Don't-fragment ladder through the VPN path.**
   - **Action:** Run [OEN-S01](../supporting/s01-pmtud-size-ladder.md) toward a public HTTPS target **while traffic uses** `<wg-iface>`.
   - **Expected:** A clear max payload under the tunnel MTU, with small ping succeeding.
   - **On failure:** If even mid-size DF fails, check routing; if DF already reaches ~1500, skip to P5.
4. **P4 — Same URL: curl vs Chromium.**
   - **Action:** `curl -4 -sS -o /dev/null -w '%{http_code}\n' --connect-timeout 8 https://<target>` then open the same URL in Chromium/Brave.
   - **Expected:** curl 200; browser handshake closed or `ERR_CONNECTION_CLOSED`.
   - **On failure:** If both fail, this is not the curl-vs-browser split (auth, DNS, or blocking).
5. **P5 — Explicit MSS on LAN↔VPN only.**
   - **Action:** On LAN↔`<wg-iface>` FORWARD (IPv4 and IPv6), install `TCPMSS --set-mss` with an explicit value under the tunnel payload. Do **not** use `--clamp-mss-to-pmtu`. Do **not** change LAN MTU.
   - **Expected:** Chromium handshake completes. `ip link` still shows LAN 1500.
   - **On failure:** Re-check after firmware/VPN scripts redeploy; clamps get wiped.

## Expected samples

```text
# curl 200 while Chromium ERR_CONNECTION_CLOSED — this spec, after DNS is honest
200

# DF fail
ping: local error: message too long, mtu=1320
```

## Verify

- curl and Chromium both complete HTTPS to the same URL.
- LAN bridge MTU is 1500.
- TCPMSS exists only on LAN↔VPN forward (plus any scoped exit path).
- Overlay SSH 3 KB+ still works ([OEN-01](01-overlay-ssh-byte-cliff.md)).
- ICMP / small ping success was **not** used as the pass criterion when this spec names TCP, SSH, or HTTPS.
- Bind table was filled by a human before any live `ip` / nft / iptables change.

## MUST NOT

- MUST NOT file a Chromium or overlay-product bug until P1–P5 are evidenced.
- MUST NOT shrink the LAN bridge to the commercial WireGuard MTU.
- MUST NOT treat working curl/ping/DNS as proof “not MTU.”
- MUST NOT skip the DNS-hijack check.
- MUST NOT publish hostnames or addresses from the ladder.
- MUST NOT apply live network or firewall changes until Bind is filled by a human.
- MUST NOT claim a fix on ICMP ping alone when Verify names TCP, SSH, or HTTPS.
- MUST NOT publish hostnames, addresses, ULAs, or custom ports.

## Related specs

- [OEN-01 Overlay SSH byte cliff](01-overlay-ssh-byte-cliff.md)
- [OEN-03 Router VPN DNS hijack](03-router-vpn-dns-hijack.md)
- [OEN-S01 Don't-fragment ping size ladder](../supporting/s01-pmtud-size-ladder.md)
- [OEN-S02 clamp-mss-to-pmtu is a no-op](../supporting/s02-clamp-mss-to-pmtu-noop.md)

## Prior art (Not novel)

Chromium ClientHello size versus curl is partly documented. This spec’s claim is the combo: do not trust curl, do not shrink the LAN, check DNS hijack first, and use explicit `--set-mss`.

