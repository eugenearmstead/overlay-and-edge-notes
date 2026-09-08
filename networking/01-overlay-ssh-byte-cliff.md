---
id: OEN-01
title: Overlay SSH stalls at a byte cliff
kind: original
status: active
edition: 2
date_published: 2026-09-07
author: Eugene Armstead
author_url: https://www.armsteadent.com/
canonical: https://eugenearmstead.github.io/overlay-and-edge-notes/networking/01-overlay-ssh-byte-cliff.html
keywords:
  - "overlay SSH hang 1KB"
  - "Tailscale SSH stall"
  - "SSH hangs after login"
  - "overlay SSH byte cliff"
  - "path MTU"
  - "TCPMSS"
  - "double encapsulation"
  - "don't-fragment ping"
  - "WireGuard MTU"
  - "ControlPath=none"
  - "clamp-mss-to-pmtu"
  - "userspace Tailscale SSH"
  - "MSS clamp wrong path"
  - "LAN MTU 1500"
  - "Headscale SSH hang"
backs: []
backed_by:
  - OEN-S01
  - OEN-S02
  - OEN-S03
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
  - abbr: HTTP
    expansion: Hypertext Transfer Protocol
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
  - abbr: UDP
    expansion: User Datagram Protocol
  - abbr: SYN
    expansion: TCP synchronize packet
  - abbr: nft
    expansion: nftables (Linux packet filter)
  - abbr: nftables
    expansion: Linux packet-filter framework
  - abbr: RST
    expansion: TCP reset flag
  - abbr: Chromium
    expansion: open-source browser engine
  - abbr: ICMPv6
    expansion: Internet Control Message Protocol version 6
  - abbr: MB
    expansion: megabyte
---

# Overlay SSH stalls at a byte cliff

## Context

Overlay Secure Shell (SSH) to a **cloud Virtual Private Server (VPS)** can accept a session and run tiny commands, then stall on anything that prints more than about one kilobyte (KB). The same client talking to a **Local Area Network (LAN) Pi** on the same overlay often transfers 3 KB or more without hanging.

A historically sharp cliff looked like this: about **1146 bytes** of server output succeeded, a few bytes more produced a hang with no further progress. That number is **not** a recommended Maximum Segment Size (MSS). It matched a **global** `TCPMSS --set-mss 1160` on the **wrong direction** (Wide Area Network (WAN) toward the overlay return path). Compute MSS from the tunnel Maximum Transmission Unit (MTU) using the formulas below. Userspace overlay SSH is less forgiving than kernel OpenSSH on the same host when path MTU is wrong.

Three local causes, in the order they were proved:

1. **Double encapsulation.** The mesh underlay to the cloud VPS public addresses rides the same **commercial WireGuard** that carries general internet traffic. Inner overlay packets already sized for the tunnel MTU do not fit in the outer tunnel. Don't-fragment (DF) pings toward the VPS public address stuck roughly **100 bytes under** the commercial tunnel MTU, while a clear-WAN ping to the same public address reached a much larger size.
2. **Wrong-scope MSS.** A clamp meant for exit-node forwarding was installed globally, or on WAN→overlay return. Admin overlay SSH then died at the MSS-minus-headers cliff.
3. **Shrinking the LAN bridge to the Virtual Private Network (VPN) MTU** “to fix browsing.” That hides Chromium Transport Layer Security (TLS) symptoms and **breaks** overlay mesh underlay and large SSH. Keep the LAN bridge at **1500**. Clamp MSS only on LAN↔VPN forward.

Dead SSH multiplexing sockets are a **symptom**. They are not the path-MTU fix.

## Topology

Generic nodes only. Operator fills names in **Bind**.

```text
[workstation]
    |  overlay SSH (userspace), -o ControlPath=none
    |  underlay: either <wan-iface> (wanted for VPS public)
    |            or <wg-iface> (double-encap trap)
    v
[consumer router]
    +-- <lan-bridge>   MTU 1500  (MUST stay 1500)
    +-- <wg-iface>     commercial WireGuard  (measure MTU; often ~1320)
    +-- <wan-iface>    clear WAN
    +-- policy: dest <vps-public-v4> / <vps-public-v6>  -->  table main / WAN
    |
    |  mesh UDP to VPS public addresses
    v
[<cloud-vps>]
    +-- <overlay-tun>
    +-- overlay SSH server (userspace)

[<lan-pi>]   same client, same overlay SSH — control path (3 KB+ SHOULD work)
```

## Bind

Fill this table **before** any `ip rule`, nft, or iptables change. Do **not** paste real values back into public notes.

| Placeholder | Operator fills | Host class | Address / iface class |
|-------------|----------------|------------|------------------------|
| `<cloud-vps>` | Overlay SSH destination used in `ssh` | Cloud VPS | Overlay hostname or overlay address the operator already uses |
| `<lan-pi>` | Overlay SSH destination | Always-on LAN Pi | Overlay, same overlay as the VPS |
| `<user>` | SSH user on the VPS / Pi | Guest account | Username only |
| `<wg-iface>` | `ip -o link` name of commercial WireGuard | Consumer router (or VPS client) | Interface name |
| `<wan-iface>` | WAN interface | Consumer router | Interface name |
| `<lan-bridge>` | LAN bridge | Consumer router | Interface name |
| `<overlay-tun>` | Overlay tunnel iface on the VPS | Cloud VPS | Interface name |
| `<vps-public-v4>` | Public IPv4 of the cloud VPS | — | WAN unicast; **never publish** |
| `<vps-public-v6>` | Public IPv6 of the cloud VPS | — | WAN unicast; **never publish** |
| `<overlay-v4>` | Overlay IPv4 of `<cloud-vps>` | — | Overlay; **never publish** |
| `<overlay-v6>` | Overlay IPv6 of `<cloud-vps>` | — | Overlay; **never publish** |
| `<wg-mtu>` | `ip link show <wg-iface>` MTU | Router | Integer from the box |
| `<mss4>` | `wg-mtu - 40` | — | IPv4 TCP MSS (see Formulas) |
| `<mss6>` | `wg-mtu - 60` | — | IPv6 TCP MSS |

## Formulas

Measure `<wg-mtu>` from the live interface. Do not assume 1320. Do not use 1160 as the recipe.

```text
# IPv4 TCP MSS = tunnel MTU minus 20-byte IPv4 header minus 20-byte TCP header
mss4 = <wg-mtu> - 40

# IPv6 TCP MSS = tunnel MTU minus 40-byte IPv6 header minus 20-byte TCP header
mss6 = <wg-mtu> - 60

# Don't-fragment ping payload vs IP packet size ([OEN-S01](../supporting/s01-pmtud-size-ladder.md))
# IPv4: IP size ≈ payload + 28   (20 IP + 8 ICMP)
# IPv6: IP size ≈ payload + 48   (40 IPv6 + 8 ICMPv6)

# Historical 1146-byte overlay SSH cliff (evidence of WRONG SCOPE, not the fix):
#   global or WAN→overlay-return  --set-mss 1160
#   ≈ 1160 minus TCP/IP overhead in the userspace SSH path
# LAN↔VPN explicit MSS uses <mss4>/<mss6> (or a slightly smaller explicit value
# if TCP options eat payload). Example when <wg-mtu> is 1320: mss4=1280, mss6=1260.
```

## Decision

Operators MUST treat this as a **path** problem before an overlay-SSH product bug.

- Destination policy MUST send traffic **to the cloud VPS public addresses** out the **clear WAN**, while general internet MAY stay on commercial WireGuard.
- The LAN bridge MUST stay **1500**. MSS clamping MUST be **only** on LAN↔VPN forward, with an **explicit** `--set-mss <mss4>` / `<mss6>` (not `--clamp-mss-to-pmtu`, which is a no-op when Internet Control Message Protocol (ICMP) path MTU discovery (PMTUD) is blackholed). See [OEN-S02](../supporting/s02-clamp-mss-to-pmtu-noop.md).
- Operators MUST NOT clamp overlay **return** (WAN→overlay) and MUST NOT install a global FORWARD MSS that hits admin sessions.
- Audits MUST use `-o ControlPath=none`. See [OEN-S03](../supporting/s03-transfer-matrix-controlpath.md).

## Consequences

- Overlay SSH large output starts working on the cloud VPS once underlay is clear-WAN and MSS is scoped.
- LAN clients keep a 1500 bridge, so overlay mesh underlay is not poisoned.
- Browser HTTPS over the VPN still needs an explicit LAN↔VPN MSS ([OEN-02](02-chromium-tls-pmtu.md)). Do not “fix browsing” by shrinking the LAN.
- Keyed kernel SSH on a custom admin port is **not** the daily workaround. Fix the path.

## Agent stop rule

> A coding agent MUST emit a **bound runbook** (this Procedure with every placeholder replaced from Bind).  
> MUST NOT apply `ip rule`, `nft`, `iptables`, `ip6tables`, or sysctl until a **human** filled Bind and approved the bound commands.  
> MUST NOT claim the trap is fixed because ICMP ping succeeded. Verify is overlay SSH printing 3 KB+ with `ControlPath=none`.  
> MUST NOT file an overlay-SSH upstream bug from this page.

## Procedure

Preconditions: overlay SSH login to `<cloud-vps>` and `<lan-pi>` already works for tiny commands. Placeholders only until Bind is filled.

1. **P1 — Disable SSH multiplexing for the audit.**
   - **Action:** Add `-o ControlPath=none` to every overlay SSH command.

     ```bash
     ssh -o ControlPath=none <user>@<cloud-vps> 'echo ok'
     ssh -o ControlPath=none <user>@<lan-pi> 'echo ok'
     ```

   - **Expected:** A new Transmission Control Protocol (TCP) session, not a reused mux. Sample: a single line `ok` then a prompt.
   - **On failure:** Stop. Heal or ignore mux sockets; they are not the MTU fix. Continue only with `ControlPath=none`.

2. **P2 — Prove small commands work and large commands hang on the cloud VPS.**
   - **Action:** Tiny then large (do not cancel the large command for 30 seconds):

     ```bash
     ssh -o ControlPath=none <user>@<cloud-vps> 'echo ok'
     ssh -o ControlPath=none <user>@<cloud-vps> 'dd if=/dev/zero bs=1024 count=3 status=none | wc -c'
     ```

     Optional size matrix: [OEN-S03](../supporting/s03-transfer-matrix-controlpath.md) (`1 KB` vs about `1 MB`).
   - **Expected:** Tiny returns `ok`. Large `wc -c` **never prints** (session hung) if this spec applies. After the fix, `wc -c` prints `3072`.
   - **On failure:** If large output already works, this spec does not apply. If tiny commands fail, this is not a byte cliff (auth, routing, or daemon).

3. **P3 — Compare with a LAN Pi on the same client.**
   - **Action:** Repeat the large command against `<lan-pi>`.

     ```bash
     ssh -o ControlPath=none <user>@<lan-pi> 'dd if=/dev/zero bs=1024 count=3 status=none | wc -c'
     ```

   - **Expected:** The Pi prints `3072` on the same client.
   - **On failure:** If the Pi also cliffs, look at the **client** path (LAN↔VPN MSS, client MTU) before blaming the VPS.

4. **P4 — Measure don't-fragment size to the VPS public address vs overlay address.**
   - **Action:** Run the IPv4 **and** IPv6 ladders in [OEN-S01](../supporting/s01-pmtud-size-ladder.md) toward `<vps-public-v4>` / `<vps-public-v6>` and toward `<overlay-v4>` / `<overlay-v6>`.
   - **Expected:** If mesh underlay is double-encapsulated, DF to the public address tops out about 100 bytes under `<wg-mtu>`. Clear WAN to the same public address is larger. Sample fail: `ping: local error: message too long, mtu=<wg-mtu>`. Sample success: `1 packets transmitted, 1 received`.
   - **On failure:** If public-address DF already reaches near WAN MTU, skip to P6 (MSS scope).

5. **P5 — Install destination policy so VPS public addresses use clear WAN.**
   - **Action:** On the consumer router (or the host that selects commercial WireGuard vs WAN), add policy so packets **destined to** the cloud VPS public addresses use table `main` / WAN, not `<wg-iface>`. **Human MUST have filled Bind.** Preferences `10005` / `10006` are examples; pick unused prefs.

     ```bash
     # IPv4 + IPv6 destination exceptions (example prefs; list first)
     ip rule show
     ip -6 rule show
     ip rule add pref 10005 to <vps-public-v4> table main
     ip -6 rule add pref 10006 to <vps-public-v6> table main

     # Confirm from a LAN source (replace <lan-client-v4> from Bind notes)
     ip route get <vps-public-v4> from <lan-client-v4> iif <lan-bridge>
     ip -6 route get <vps-public-v6> from <lan-client-v6> iif <lan-bridge>
     ip route get 1.1.1.1 from <lan-client-v4> iif <lan-bridge>
     ```

   - **Expected:** `ip route get` to the VPS public addresses shows `<wan-iface>` / table main, **not** `<wg-iface>`. General internet `ip route get 1.1.1.1` MAY still show `<wg-iface>`.
   - **On failure:** Recheck policy preference order (`ip rule` lower pref wins). Do not shrink the LAN bridge MTU.

6. **P6 — Strip global / overlay-return MSS; keep exit-path clamp only.**
   - **Action:** List FORWARD / mangle TCPMSS. Delete any **global** `--set-mss` and any WAN→`<overlay-tun>` return clamp. Keep MSS only on the **exit** forward path (`<overlay-tun>`→WAN) if this host is also an `<exit-node>`.

     ```bash
     # iptables
     iptables -L FORWARD -n -v --line-numbers
     iptables -t mangle -L FORWARD -n -v --line-numbers
     ip6tables -L FORWARD -n -v --line-numbers
     iptables -S FORWARD | grep -i tcpmss || true
     ip6tables -S FORWARD | grep -i tcpmss || true

     # nft (if the host uses nftables)
     nft list ruleset | grep -i -A2 mss || true
     ```

     Delete by line number only after identifying a **global** or WAN→overlay-return rule. Sample of a **bad** rule (wrong scope): `TCPMSS set 1160` matching WAN ingress toward `<overlay-tun>`.
   - **Expected:** Admin overlay SSH is not subject to an MSS of ~1160 on the return path.
   - **On failure:** Re-audit after exit-node scripts redeploy; bad clamps come back. Changelog that node ([OEN-18](18-per-node-changelog-contract.md)).

7. **P7 — Keep LAN 1500; explicit `--set-mss` only on LAN↔VPN forward.**
   - **Action:** Confirm the LAN bridge MTU is 1500. On LAN↔`<wg-iface>` FORWARD (v4 and v6), use explicit TCPMSS. Do **not** use `--clamp-mss-to-pmtu`.

     ```bash
     ip link show <lan-bridge>
     ip link show <wg-iface>
     # expect: <lan-bridge> mtu 1500 ; <wg-iface> mtu <wg-mtu>

     mss4=$((<wg-mtu> - 40))
     mss6=$((<wg-mtu> - 60))

     # iptables (idempotent insert)
     iptables -C FORWARD -i <lan-bridge> -o <wg-iface> -p tcp --tcp-flags SYN,RST SYN \
       -j TCPMSS --set-mss "$mss4" \
       || iptables -I FORWARD -i <lan-bridge> -o <wg-iface> -p tcp --tcp-flags SYN,RST SYN \
       -j TCPMSS --set-mss "$mss4"
     iptables -C FORWARD -i <wg-iface> -o <lan-bridge> -p tcp --tcp-flags SYN,RST SYN \
       -j TCPMSS --set-mss "$mss4" \
       || iptables -I FORWARD -i <wg-iface> -o <lan-bridge> -p tcp --tcp-flags SYN,RST SYN \
       -j TCPMSS --set-mss "$mss4"
     ip6tables -C FORWARD -i <lan-bridge> -o <wg-iface> -p tcp --tcp-flags SYN,RST SYN \
       -j TCPMSS --set-mss "$mss6" \
       || ip6tables -I FORWARD -i <lan-bridge> -o <wg-iface> -p tcp --tcp-flags SYN,RST SYN \
       -j TCPMSS --set-mss "$mss6"
     ip6tables -C FORWARD -i <wg-iface> -o <lan-bridge> -p tcp --tcp-flags SYN,RST SYN \
       -j TCPMSS --set-mss "$mss6" \
       || ip6tables -I FORWARD -i <wg-iface> -o <lan-bridge> -p tcp --tcp-flags SYN,RST SYN \
       -j TCPMSS --set-mss "$mss6"

     # nft equivalent (adjust table/chain to the host; do not nft flush — [OEN-S16](../supporting/s16-never-nft-flush.md))
     nft add rule inet filter forward iifname "<lan-bridge>" oifname "<wg-iface>" \
       tcp flags syn / syn,rst tcp option maxseg size set $mss4
     nft add rule inet filter forward iifname "<lan-bridge>" oifname "<wg-iface>" \
       ip6 nexthdr tcp tcp flags syn / syn,rst tcp option maxseg size set $mss6
     ```

     If nft `inet` cannot mix v4/v6 maxseg in one rule on this kernel, use separate `ip filter` / `ip6 filter` tables with the same match.
   - **Expected:** `ip link` shows LAN 1500 and `<wg-iface>` at `<wg-mtu>`. TCPMSS exists only on that forward pair (plus optional scoped exit path). Overlay SSH P2 now prints `3072`.
   - **On failure:** If someone set LAN MTU to the VPN MTU, restore 1500. Overlay large SSH will not stay healthy on a shrunken LAN.

## Expected samples

Scrubbed. Replace sizes with what Bind measured.

```text
# P2 tiny (good)
ok

# P2 large BEFORE path fix (hang): wc -c never prints; SSH session stuck until killed
# P2 large AFTER path fix
3072

# P4 DF fail (IPv4, payload too big for path)
ping: local error: message too long, mtu=1320

# P4 DF success
PING <target> (<target>) 1292(1320) bytes of data.
1300 bytes from <target>: icmp_seq=1 ttl=54 time=18.2 ms

# P5 wanted: VPS public uses WAN, not WireGuard
<vps-public-v4> from <lan-client-v4> iif <lan-bridge> dev <wan-iface> src <lan-nat-v4> uid 0
1.1.1.1 from <lan-client-v4> iif <lan-bridge> dev <wg-iface> src <tunnel-v4> uid 0
```

## Verify

- Overlay SSH to `<cloud-vps>` with `ControlPath=none` prints 3 KB+ (`dd … count=3 | wc -c` finishes with `3072`).
- The same check still passes on `<lan-pi>`.
- DF ping to the VPS public address is no longer stuck ~100 bytes under `<wg-mtu>` ([OEN-S01](../supporting/s01-pmtud-size-ladder.md)).
- LAN bridge MTU is 1500.
- No TCPMSS rule matches WAN→overlay return.
- ICMP success was **not** used as the pass criterion.

## MUST NOT

- MUST NOT file an overlay-SSH upstream bug until P4–P7 are evidenced.
- MUST NOT treat a custom kernel SSH admin port, or a cloud break-glass SSH product, as the daily fix.
- MUST NOT shrink the LAN bridge to the commercial WireGuard MTU to “fix browsing.”
- MUST NOT use `--clamp-mss-to-pmtu` as the LAN↔VPN fix when ICMP is dropped ([OEN-S02](../supporting/s02-clamp-mss-to-pmtu-noop.md)).
- MUST NOT clamp overlay return or install a global FORWARD MSS.
- MUST NOT apply P5–P7 until Bind is filled by a human.
- MUST NOT claim a fix on ICMP ping alone.
- MUST NOT publish hostnames, public IPs, overlay addresses, or custom SSH ports in a repro.

## Related specs

- [OEN-S01 Don't-fragment ping size ladder (path MTU discovery)](../supporting/s01-pmtud-size-ladder.md)
- [OEN-02 Chromium TLS fails while curl returns 200](02-chromium-tls-pmtu.md)
- [OEN-S02 clamp-mss-to-pmtu is a no-op when ICMP is dropped](../supporting/s02-clamp-mss-to-pmtu-noop.md)
- [OEN-S03 1 KB vs 1 MB transfer matrix + ControlPath=none](../supporting/s03-transfer-matrix-controlpath.md)
- [OEN-04 Exit-node TCP maximum-segment-size clamp after ts-forward never runs](04-exit-tcpmss-after-ts-forward.md)
- [OEN-16 Commercial WireGuard endpoint rotation](16-commercial-wg-endpoint-rotation.md)
- [OEN-18 Per-node changelog contract](18-per-node-changelog-contract.md)

## Prior art (Not novel)

Generic WireGuard MTU notes and WSL2 `eth0` 1280 vs overlay 1280 are already public. This spec’s claim is the **combo**: double encapsulation of mesh underlay through the same commercial tunnel as general internet, plus “do not shrink the LAN,” plus explicit `--set-mss` vs clamp-to-pmtu, plus userspace overlay SSH vs kernel SSH as one playbook, with bindable commands a remote agent can execute after a human fills Bind.
