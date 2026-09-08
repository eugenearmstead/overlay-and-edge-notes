---
id: OEN-01
title: Overlay SSH stalls at a byte cliff
kind: original
status: active
edition: 1
date_published: 2026-09-07
author: Eugene Armstead
author_url: https://www.armsteadent.com/
canonical: https://eugenearmstead.github.io/overlay-and-edge-notes/networking/01-overlay-ssh-byte-cliff.html
keywords:
  - path-mtu
  - overlay-ssh
  - double-encapsulation
  - tcpmss
backs: []
backed_by:
  - OEN-S01
description: Overlay SSH accepts login then hangs above about 1 KB when mesh underlay double-encapsulates through commercial WireGuard or when MSS is clamped on the wrong path.
terms:
  - abbr: OEN
    expansion: Overlay and Edge Notes
  - abbr: SSH
    expansion: Secure Shell
  - abbr: OpenSSH
    expansion: OpenBSD Secure Shell
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
  - abbr: MSS
    expansion: Maximum Segment Size
  - abbr: TCPMSS
    expansion: iptables/nft target that sets TCP Maximum Segment Size
  - abbr: MTU
    expansion: Maximum Transmission Unit
  - abbr: ICMP
    expansion: Internet Control Message Protocol
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
  - abbr: WG
    expansion: WireGuard
  - abbr: WireGuard
    expansion: UDP-based VPN protocol
  - abbr: DNS
    expansion: Domain Name System
  - abbr: ControlPath
    expansion: OpenSSH multiplexing socket path option
  - abbr: FORWARD
    expansion: netfilter/iptables forward chain
  - abbr: WSL2
    expansion: Windows Subsystem for Linux 2
  - abbr: Pi
    expansion: single-board computer (Raspberry Pi class)
---

# Overlay SSH stalls at a byte cliff

## Context

Overlay Secure Shell (SSH) to a **cloud Virtual Private Server (VPS)** can accept a session and run tiny commands, then stall on anything that prints more than about one kilobyte (KB). The same client talking to a **Local Area Network (LAN) Pi** on the same overlay often transfers 3 KB or more without hanging.

A historically sharp cliff looked like this: about **1146 bytes** of server output succeeded, a few bytes more produced a hang with no further progress. That number is not magic. It matched a **global** `TCPMSS --set-mss 1160` on the wrong direction (Wide Area Network (WAN) toward the overlay return path). Userspace overlay SSH is less forgiving than kernel OpenSSH on the same host when path Maximum Transmission Unit (MTU) is wrong.

Three local causes, in the order they were proved:

1. **Double encapsulation.** The mesh underlay to the cloud VPS public addresses rides the same **commercial WireGuard** that carries general internet traffic. Inner overlay packets already sized for the tunnel MTU do not fit in the outer tunnel. Don't-fragment (DF) pings toward the VPS public address stuck roughly **100 bytes under** the commercial tunnel MTU, while a clear-WAN ping to the same public address reached a much larger size.
2. **Wrong-scope Maximum Segment Size (MSS).** A clamp meant for exit-node forwarding was installed globally, or on WAN→overlay return. Admin overlay SSH then died at the MSS-minus-headers cliff.
3. **Shrinking the LAN bridge to the Virtual Private Network (VPN) MTU** “to fix browsing.” That hides Chromium Transport Layer Security (TLS) symptoms and **breaks** overlay mesh underlay and large SSH. Keep the LAN bridge at **1500**. Clamp MSS only on LAN↔VPN forward.

Dead SSH multiplexing sockets are a **symptom**. They are not the path-MTU fix.

## Decision

Operators MUST treat this as a **path** problem before an overlay-SSH product bug.

- Destination policy MUST send traffic **to the cloud VPS public addresses** out the **clear WAN**, while general internet MAY stay on commercial WireGuard.
- The LAN bridge MUST stay **1500**. MSS clamping MUST be **only** on LAN↔VPN forward, with an **explicit** `--set-mss` (not `--clamp-mss-to-pmtu`, which is a no-op when Internet Control Message Protocol (ICMP) path MTU discovery (PMTUD) is blackholed). See [OEN-S01](../supporting/s01-pmtud-size-ladder.md).
- Operators MUST NOT clamp overlay **return** (WAN→overlay) and MUST NOT install a global FORWARD MSS that hits admin sessions.
- Audits MUST use `-o ControlPath=none`.

## Consequences

- Overlay SSH large output starts working on the cloud VPS once underlay is clear-WAN and MSS is scoped.
- LAN clients keep a 1500 bridge, so overlay mesh underlay is not poisoned.
- Browser HTTPS over the VPN still needs an explicit LAN↔VPN MSS (a different trap). Do not “fix browsing” by shrinking the LAN.
- Keyed kernel SSH on a custom admin port is **not** the daily workaround. Fix the path.

## Procedure

Preconditions: you can log in with overlay SSH to `<cloud-vps>` and to a `<lan-pi>` from the same client. Placeholders only.

1. **P1 — Disable SSH multiplexing for the audit.**
   - **Action:** Add `-o ControlPath=none` to every overlay SSH command in this procedure.
   - **Expected:** A new TCP session, not a reused mux.
   - **On failure:** Stop. Heal or ignore mux sockets; they are not the MTU fix. Continue only with `ControlPath=none`.

2. **P2 — Prove small commands work and large commands hang on the cloud VPS.**
   - **Action:** Overlay SSH to `<cloud-vps>` and run a tiny command (`hostname` or `echo ok`). Then run a command that prints more than ~2 KB (for example `top -bn1` piped to `wc -c`).
   - **Expected:** Tiny command returns. Large output stalls or `wc -c` never finishes.
   - **On failure:** If large output already works, this spec does not apply. If tiny commands fail, this is not a byte cliff (auth, routing, or daemon).

3. **P3 — Compare with a LAN Pi on the same client.**
   - **Action:** Repeat P2 against `<lan-pi>`.
   - **Expected:** The Pi accepts 3 KB+ on the same client.
   - **On failure:** If the Pi also cliffs, look at the **client** path (LAN↔VPN MSS, client MTU) before blaming the VPS.

4. **P4 — Measure don't-fragment size to the VPS public address vs overlay address.**
   - **Action:** Run the size ladder in [OEN-S01](../supporting/s01-pmtud-size-ladder.md) toward the VPS **public** address and toward the overlay address of `<cloud-vps>`.
   - **Expected:** If mesh underlay is double-encapsulated, DF to the public address tops out about 100 bytes under the commercial tunnel MTU. Clear WAN to the same public address is larger.
   - **On failure:** If public-address DF already reaches near WAN MTU, skip to P6 (MSS scope).

5. **P5 — Install destination policy so VPS public addresses use clear WAN.**
   - **Action:** On the consumer router (or the host that selects commercial WireGuard vs WAN), add policy routing so packets **destined to** the cloud VPS public v4 and v6 addresses use the main/WAN table, not `<wg-iface>`.
   - **Expected:** `ip route get <vps-public>` from a LAN source shows the WAN path, not `<wg-iface>`. General internet `ip route get` of a public resolver MAY still show `<wg-iface>`.
   - **On failure:** Recheck policy preference order. Do not shrink the LAN bridge MTU.

6. **P6 — Strip global / overlay-return MSS; keep exit-path clamp only.**
   - **Action:** List FORWARD / mangle TCPMSS rules. Delete any global `--set-mss` and any WAN→overlay return clamp. Keep MSS only on the **exit** forward path (overlay→WAN) if this host is also an `<exit-node>`.
   - **Expected:** Admin overlay SSH is not subject to an MSS of ~1160 on the return path.
   - **On failure:** Re-audit after exit-node scripts redeploy; bad clamps come back.

7. **P7 — Keep LAN 1500; explicit `--set-mss` only on LAN↔VPN forward.**
   - **Action:** Confirm the LAN bridge MTU is 1500. On LAN↔`<wg-iface>` FORWARD (v4 and v6), use `TCPMSS --set-mss` with an explicit value under the tunnel payload, not `--clamp-mss-to-pmtu`.
   - **Expected:** `ip link` shows LAN 1500 and `<wg-iface>` at the tunnel MTU. TCPMSS rules exist only on that forward pair (plus optional scoped exit path).
   - **On failure:** If someone set LAN MTU to the VPN MTU, restore 1500. Overlay large SSH will not stay healthy on a shrunken LAN.

## Verify

- Overlay SSH to `<cloud-vps>` with `ControlPath=none` prints 3 KB+ (`top -bn1 | wc -c` finishes).
- The same check still passes on `<lan-pi>`.
- DF ping to the VPS public address is no longer stuck ~100 bytes under the tunnel MTU.
- LAN bridge MTU is 1500.
- No TCPMSS rule matches WAN→overlay return.

## MUST NOT

- MUST NOT file an overlay-SSH upstream bug until P4–P7 are evidenced.
- MUST NOT treat a custom kernel SSH admin port, or a cloud break-glass SSH product, as the daily fix.
- MUST NOT shrink the LAN bridge to the commercial WireGuard MTU to “fix browsing.”
- MUST NOT use `--clamp-mss-to-pmtu` as the LAN↔VPN fix when ICMP is dropped.
- MUST NOT clamp overlay return or install a global FORWARD MSS.
- MUST NOT publish hostnames, public IPs, overlay addresses, or custom SSH ports in a repro.

## Related specs

- [OEN-S01 Don't-fragment ping size ladder (path MTU discovery)](../supporting/s01-pmtud-size-ladder.md) (built)
- OEN-02 Chromium TLS vs curl (forthcoming)
- OEN-S02 clamp-mss-to-pmtu no-op (forthcoming)
- OEN-S03 transfer matrix + `ControlPath=none` (forthcoming)

## Prior art (Not novel)

Generic WireGuard MTU notes and WSL2 `eth0` 1280 vs overlay 1280 are already public. This spec’s claim is the **combo**: double encapsulation of mesh underlay through the same commercial tunnel as general internet, plus “do not shrink the LAN,” plus explicit `--set-mss` vs clamp-to-pmtu, plus userspace overlay SSH vs kernel SSH as one playbook.
