---
id: "OEN-04"
title: "Exit-node TCP maximum-segment-size clamp after ts-forward never runs"
kind: "original"
status: "active"
edition: 3
date_published: "2026-09-08"
author: "Eugene Armstead"
author_url: "https://www.armsteadent.com/"
canonical: "https://eugenearmstead.github.io/overlay-and-edge-notes/networking/04-exit-tcpmss-after-ts-forward.html"
keywords:
  - "ts-forward TCPMSS 0 packets"
  - "TCPMSS after jump ts-forward"
  - "exit-node TCPMSS never runs"
  - "Tailscale ts-forward clamp"
  - "DNS_PROBE_POSSIBLE cellular"
  - "exit SYN never clamped"
  - "TCPMSS top of ts-forward"
  - "ipleak DNS ok HTTP timeout"
  - "Headscale exit MSS"
  - "nft jump before clamp"
  - "path MTU exit node"
  - "don't-fragment ping"
backs:
  []
backed_by:
  - OEN-S01
  - OEN-S32
description: "TCPMSS rules in FORWARD after jump ts-forward never see exit SYNs; insert the clamp at the top of ts-forward and re-apply after the overlay daemon rewrites chains."
terms:
  - abbr: CLI
    expansion: command-line interface
  - abbr: DNS
    expansion: Domain Name System
  - abbr: FORWARD
    expansion: netfilter/iptables forward chain
  - abbr: GCP
    expansion: Google Cloud Platform
  - abbr: HTTP
    expansion: Hypertext Transfer Protocol
  - abbr: HTTPS
    expansion: Hypertext Transfer Protocol Secure
  - abbr: ICMP
    expansion: Internet Control Message Protocol
  - abbr: IPv4
    expansion: Internet Protocol version 4
  - abbr: IPv6
    expansion: Internet Protocol version 6
  - abbr: LAN
    expansion: Local Area Network
  - abbr: MTU
    expansion: Maximum Transmission Unit
  - abbr: nft
    expansion: nftables (Linux packet filter)
  - abbr: NIC
    expansion: network interface card
  - abbr: OEN
    expansion: Overlay and Edge Notes
  - abbr: Pi
    expansion: single-board computer (Raspberry Pi class)
  - abbr: RST
    expansion: TCP reset flag
  - abbr: SSH
    expansion: Secure Shell
  - abbr: SYN
    expansion: TCP synchronize packet
  - abbr: TCP
    expansion: Transmission Control Protocol
  - abbr: TCPMSS
    expansion: iptables/nft target that sets TCP Maximum Segment Size
  - abbr: VM
    expansion: virtual machine
  - abbr: WAN
    expansion: Wide Area Network
  - abbr: MSS
    expansion: MSS
  - abbr: WG
    expansion: WireGuard
---

# Exit-node TCP maximum-segment-size clamp after ts-forward never runs

## Context

An `<exit-node>` can look “almost up”: leak-test Domain Name System (DNS) is green, Wi-Fi pages hang, cellular shows `DNS_PROBE_*`. Packet counters on a Transmission Control Protocol Maximum Segment Size (TCPMSS) rule in `FORWARD` **after** `jump ts-forward` stay **0**. Exit synchronize (SYN) packets never clamp.

The overlay daemon owns `ts-forward` (IPv4 and IPv6) and rewrites it when it settles. A clamp that lives only in generic `FORWARD` after the jump never runs. Public issue Tailscale #11002 describes related nft jump/accept-before-clamp behavior. This note is a field recipe, not an upstream filing.

## Topology

```text
[phone / <overlay-peer>] --exit--> [<exit-node>]
    overlay SYN  -->  chain ts-forward (daemon-owned)
                   \  FORWARD TCPMSS *after* jump   <-- counters stay 0 (TRAP)
                    +  TCPMSS inserted at TOP of ts-forward  (FIX)
```

## Bind


Fill this table **before** any live change. Do **not** paste real values back into public notes.

| Placeholder | Operator fills | Class |
|-------------|----------------|-------|
| `<overlay-impl>` | Overlay implementation class | `tailscale-compatible` or other — stop and translate CLI |
| `<exit-node>` | Overlay exit node | Cloud VM or LAN Pi used as exit |
| `<overlay-peer>` | Soak client (**not** the agent workstation) | LAN Pi |
| `<user>` | SSH user | Guest |
| `<overlay-tun>` | Overlay tun on the exit | Iface |
| `<overlay-tun-mtu>` | `ip link show <overlay-tun>` MTU | Integer from the box |
| `<wg-mtu>` | Commercial WireGuard MTU if the underlay is WG | Integer; omit if no WG underlay |
| `<overlay-underlay-overhead>` | Extra bytes overlay adds on the WG path | Integer the operator measures |
| `<gcp-nic>` | Public NIC on a Google Cloud guest | Iface; omit on non-GCP exits |
| `<wan-iface>` | WAN / public NIC | Iface |
| `<mss4>` | `mss4_overlay_over_wg` (or `mss4_wg` if no overlay-over-WG) | Formulas |
| `<mss6>` | `mss6_wg` analogue: `<wg-mtu> - 60` or overlay-tun family | Formulas |

## Formulas

```text
mss4_wg = <wg-mtu> - 40
mss6_wg = <wg-mtu> - 60
mss4_overlay_over_wg = min(<overlay-tun-mtu>, <wg-mtu> - <overlay-underlay-overhead>) - 40
# P2–P3 on this page use mss4_overlay_over_wg (exit SYN on overlay→WAN).
# Do not use a global FORWARD clamp; that is the OEN-01 cliff.
# LAN bridge MTU MUST stay 1500.
```

See [OEN-01](01-overlay-ssh-byte-cliff.md) and [OEN-S01](../supporting/s01-pmtud-size-ladder.md).

## Decision

Operators MUST insert TCPMSS at the **top of `ts-forward`** (v4 and v6) using **explicit `--set-mss`** from **mss4_overlay_over_wg**. A FORWARD copy, if used, MUST be iface-scoped (`-i <overlay-tun> -o <wan-iface>` and reverse), never unscoped `FORWARD 1`. They MUST re-apply after `tailscaled` (or equivalent) settles.

DNS leak-test green is **not** IPv6 data-plane green ([OEN-S32](../supporting/s32-dns-leak-test-not-v6-dataplane.md)).

## Consequences

- Exit-client HTTP(S) starts completing on Wi-Fi and cellular.
- Counters on the ts-forward TCPMSS rules increment.
- A later daemon restart can wipe the rules; the re-apply path matters.

## Agent stop rule

> MUST emit bound `iptables`/`ip6tables` (or nft) inserts for **ts-forward** after `<overlay-impl>` is `tailscale-compatible` and Bind is filled.
> MUST NOT insert unscoped `FORWARD 1` TCPMSS (that is the [OEN-01](01-overlay-ssh-byte-cliff.md) cliff).
> MUST NOT lead with `--clamp-mss-to-pmtu` ([OEN-S02](../supporting/s02-clamp-mss-to-pmtu-noop.md)).
> MUST NOT claim ICMP ping as the exit HTTPS fix.
> MUST NOT file an overlay-product bug from this page.

## Procedure

This spec does not apply if `<overlay-impl>` is not tailscale-compatible.

### Copy-paste commands (after Bind)

Human-filled Bind. Re-apply after the overlay daemon settles (it rewrites chains). P2 uses **mss4_overlay_over_wg**.

```bash
# mss4 is mss4_overlay_over_wg from Bind (not an unscoped FORWARD clamp)
mss4=<mss4>
mss6=<mss6>

iptables -L ts-forward -n -v --line-numbers
ip6tables -L ts-forward -n -v --line-numbers
iptables -L FORWARD -n -v --line-numbers | head
iptables -S FORWARD | grep -i tcpmss || true

# Insert at TOP of ts-forward (IPv4 + IPv6) — explicit --set-mss
iptables -I ts-forward 1 -p tcp --tcp-flags SYN,RST SYN -j TCPMSS --set-mss "$mss4"
ip6tables -I ts-forward 1 -p tcp --tcp-flags SYN,RST SYN -j TCPMSS --set-mss "$mss6"
# Optional FORWARD copy: iface-scoped only (never unscoped FORWARD 1)
iptables -I FORWARD 1 -i <overlay-tun> -o <wan-iface> -p tcp --tcp-flags SYN,RST SYN -j TCPMSS --set-mss "$mss4"
iptables -I FORWARD 1 -i <wan-iface> -o <overlay-tun> -p tcp --tcp-flags SYN,RST SYN -j TCPMSS --set-mss "$mss4"
ip6tables -I FORWARD 1 -i <overlay-tun> -o <wan-iface> -p tcp --tcp-flags SYN,RST SYN -j TCPMSS --set-mss "$mss6"
ip6tables -I FORWARD 1 -i <wan-iface> -o <overlay-tun> -p tcp --tcp-flags SYN,RST SYN -j TCPMSS --set-mss "$mss6"

nft list chain ip filter ts-forward 2>/dev/null || true
```

Then `curl -4` and `curl -6 --max-time 8 https://example.com` from `<overlay-peer>` **with the exit selected**. DNS leak-test green is not enough ([OEN-S32](../supporting/s32-dns-leak-test-not-v6-dataplane.md)).

1. **P1 — Prove the FORWARD-after-jump clamp is dead.**
   - **Action:** List FORWARD and `ts-forward` (iptables and ip6tables, or nft). Note TCPMSS packet counters after an exit-client TCP attempt.
   - **Expected:** FORWARD TCPMSS after the jump stays 0. Exit SYNs are not clamped.
   - **On failure:** If counters already increment in ts-forward, this spec does not apply.
2. **P2 — Insert TCPMSS at the top of ts-forward.**
   - **Action:** On `<exit-node>`, insert explicit `TCPMSS --set-mss` (mss4_overlay_over_wg / mss6 family) at the **head** of `ts-forward` for v4 and v6. MUST NOT lead with `--clamp-mss-to-pmtu` ([OEN-S02](../supporting/s02-clamp-mss-to-pmtu-noop.md)).
   - **Expected:** A new first rule exists in both families.
   - **On failure:** Do not only append to FORWARD.
3. **P3 — Optional iface-scoped FORWARD copy.**
   - **Action:** If a FORWARD copy is required, insert TCPMSS with `-i <overlay-tun> -o <wan-iface>` and the reverse. MUST NOT use unscoped `-I FORWARD 1` matching every SYN.
   - **Expected:** FORWARD rules are iface-scoped. Overlay-admin return is not clamped ([OEN-01](01-overlay-ssh-byte-cliff.md)).
   - **On failure:** Delete any global FORWARD TCPMSS and return to ts-forward-only.
4. **P4 — Re-apply after the daemon settles; soak from a non-workstation.**
   - **Action:** Restart or wait for the overlay daemon to finish rewriting chains, then re-apply P2–P3. Soak from `<overlay-peer>` (LAN Pi), not the agent workstation ([OEN-S18](../supporting/s18-do-not-set-exit-on-agent-workstation.md)). `curl -4` and `curl -6` to `https://example.com`.
   - **Expected:** HTTP 200 both families. TCPMSS counters in ts-forward increment.
   - **On failure:** If v4 works and v6 times out, see [OEN-06](06-netfilter-off-v6-return.md) and [OEN-S32](../supporting/s32-dns-leak-test-not-v6-dataplane.md).

## Expected samples

```text
# Bad: TCPMSS in FORWARD pkts=0 after jump
TCPMSS     all  --  *  *  ...  TCPMSS set 1280   pkts:0

# Good: ts-forward TCPMSS counters increment on a SYN from an exit client
```

## Verify

- ts-forward TCPMSS counters increment during an exit TCP handshake.
- Exit-client curl -4 and curl -6 to example.com return 200.
- Rules still present after a daemon settle/restart cycle (or a documented re-apply unit).
- Agent workstation exit remains unset.
- ICMP / small ping success was **not** used as the pass criterion when this spec names TCP, SSH, or HTTPS.
- Bind table was filled by a human before any live `ip` / nft / iptables change.

## MUST NOT

- MUST NOT file an overlay-product bug until ts-forward counters are evidenced.
- MUST NOT insert unscoped `FORWARD 1` TCPMSS.
- MUST NOT lead with `--clamp-mss-to-pmtu`.
- MUST NOT treat DNS leak-test green as IPv6 HTTP green.
- MUST NOT select this exit on the agent workstation to reproduce.
- MUST NOT apply live network or firewall changes until Bind is filled by a human.
- MUST NOT claim a fix on ICMP ping alone when Verify names TCP, SSH, or HTTPS.
- MUST NOT publish hostnames, addresses, ULAs, or custom ports.

## Page changelog

- Edition 3 (8 Sep 2026, Mountain Time): ts-forward-only clamp; iface-scoped FORWARD copy; two MSS families.

## Related specs

- [OEN-01 Overlay SSH byte cliff](01-overlay-ssh-byte-cliff.md)
- [OEN-06 Netfilter-off IPv6 return-path](06-netfilter-off-v6-return.md)
- [OEN-S02 clamp-mss-to-pmtu no-op](../supporting/s02-clamp-mss-to-pmtu-noop.md)
- [OEN-S32 DNS leak-test vs IPv6 data plane](../supporting/s32-dns-leak-test-not-v6-dataplane.md)
- [OEN-S18 Do not set exit on the agent workstation](../supporting/s18-do-not-set-exit-on-agent-workstation.md)

## Prior art (Not novel)

[Tailscale #11002](https://github.com/tailscale/tailscale/issues/11002) discusses nft jump/accept before clamp. This spec’s claim is the exit recipe: top of ts-forward, iface-scoped FORWARD copy only, re-apply after rewrite.

