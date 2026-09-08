---
id: OEN-04
title: "Exit-node TCP maximum-segment-size clamp after ts-forward never runs"
kind: original
status: active
edition: 1
date_published: 2026-09-08
author: Eugene Armstead
author_url: https://www.armsteadent.com/
canonical: https://eugenearmstead.github.io/overlay-and-edge-notes/networking/04-exit-tcpmss-after-ts-forward.html
keywords:
  - exit-node
  - tcpmss
  - ts-forward
backs: []
backed_by:
  - OEN-S01
  - OEN-S32
description: "TCPMSS rules in FORWARD after jump ts-forward never see exit SYNs; insert the clamp at the top of ts-forward and re-apply after the overlay daemon rewrites chains."
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
  - abbr: TCPMSS
    expansion: iptables/nft target that sets TCP Maximum Segment Size
  - abbr: MTU
    expansion: Maximum Transmission Unit
  - abbr: ICMP
    expansion: Internet Control Message Protocol
  - abbr: DF
    expansion: don't-fragment (IP flag)
  - abbr: HTTP
    expansion: Hypertext Transfer Protocol
  - abbr: HTTPS
    expansion: Hypertext Transfer Protocol Secure
  - abbr: IP
    expansion: Internet Protocol
  - abbr: IPv4
    expansion: Internet Protocol version 4
  - abbr: IPv6
    expansion: Internet Protocol version 6
  - abbr: DNS
    expansion: Domain Name System
  - abbr: GCP
    expansion: Google Cloud Platform
  - abbr: VM
    expansion: virtual machine
  - abbr: NIC
    expansion: network interface card
  - abbr: nft
    expansion: nftables (Linux packet filter)
  - abbr: FORWARD
    expansion: netfilter/iptables forward chain
  - abbr: Pi
    expansion: single-board computer (Raspberry Pi class)
  - abbr: SYN
    expansion: TCP synchronize packet
  - abbr: RST
    expansion: TCP reset flag
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
| `<exit-node>` | Overlay exit node | Cloud VM or LAN Pi used as exit |
| `<overlay-peer>` | Soak client (**not** the agent workstation) | LAN Pi |
| `<user>` | SSH user | Guest |
| `<overlay-tun>` | Overlay tun on the exit | Iface |
| `<gcp-nic>` | Public NIC on a Google Cloud guest | Iface; omit on non-GCP exits |
| `<wan-iface>` | WAN / public NIC | Iface |
| `<mss4>` / `<mss6>` | Computed from underlay or overlay tun MTU | Formulas |


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

Operators MUST insert TCPMSS at the **top of `ts-forward`** (v4 and v6), plus a belt-and-suspenders rule **before** the jump. They MUST re-apply after `tailscaled` (or equivalent) settles.

DNS leak-test green is **not** IPv6 data-plane green ([OEN-S32](../supporting/s32-dns-leak-test-not-v6-dataplane.md)).

## Consequences

- Exit-client HTTP(S) starts completing on Wi-Fi and cellular.
- Counters on the ts-forward TCPMSS rules increment.
- A later daemon restart can wipe the rules; the re-apply path matters.

## Agent stop rule

> A coding agent MUST emit a **bound runbook** (placeholders replaced from Bind).
> MUST NOT apply live `ip rule`, nft, iptables, ip6tables, sysctl, `wg set`, daemon restart, or deploy until a **human** filled Bind.
> MUST NOT claim a fix on ICMP ping alone when Verify names TCP, SSH, or HTTPS.
> MUST NOT file an upstream bug from this page.
> MUST NOT publish real addresses, hostnames, or custom ports.

## Procedure

Placeholders only until Bind is filled: `<cloud-vps>`, `<lan-pi>`, `<overlay-peer>`, `<exit-node>`, `<wg-iface>`, `<gcp-nic>`, plus the Bind extras on this page.

### Copy-paste commands (after Bind)

Human-filled Bind. Re-apply after the overlay daemon settles (it rewrites chains).

```bash
mss4=$((<wg-mtu> - 40)); mss6=$((<wg-mtu> - 60))
# If the clamp is for overlay tun MTU, measure that iface instead.

iptables -L ts-forward -n -v --line-numbers
ip6tables -L ts-forward -n -v --line-numbers
iptables -L FORWARD -n -v --line-numbers | head
iptables -S FORWARD | grep -i tcpmss || true

# Insert at TOP of ts-forward (IPv4 + IPv6)
iptables -I ts-forward 1 -p tcp --tcp-flags SYN,RST SYN -j TCPMSS --set-mss "$mss4"
ip6tables -I ts-forward 1 -p tcp --tcp-flags SYN,RST SYN -j TCPMSS --set-mss "$mss6"
# Belt: before the jump in FORWARD
iptables -I FORWARD 1 -p tcp --tcp-flags SYN,RST SYN -j TCPMSS --set-mss "$mss4"
ip6tables -I FORWARD 1 -p tcp --tcp-flags SYN,RST SYN -j TCPMSS --set-mss "$mss6"

nft list chain ip filter ts-forward 2>/dev/null || true
```

Then `curl -4` and `curl -6 --max-time 8 https://example.com` from `<overlay-peer>` **with the exit selected**. DNS leak-test green is not enough ([OEN-S32](../supporting/s32-dns-leak-test-not-v6-dataplane.md)).

1. **P1 — Prove the FORWARD-after-jump clamp is dead.**
   - **Action:** List FORWARD and `ts-forward` (iptables and ip6tables, or nft). Note TCPMSS packet counters after an exit-client TCP attempt.
   - **Expected:** FORWARD TCPMSS after the jump stays 0. Exit SYNs are not clamped.
   - **On failure:** If counters already increment in ts-forward, this spec does not apply.
2. **P2 — Insert TCPMSS at the top of ts-forward.**
   - **Action:** On `<exit-node>`, insert `TCPMSS --clamp-mss-to-pmtu` **or** explicit `--set-mss` at the **head** of `ts-forward` for v4 and v6. Prefer explicit `--set-mss` when ICMP is dropped ([OEN-S02](../supporting/s02-clamp-mss-to-pmtu-noop.md)).
   - **Expected:** A new first rule exists in both families.
   - **On failure:** Do not only append to FORWARD.
3. **P3 — Belt-and-suspenders before the jump.**
   - **Action:** Insert a matching TCPMSS rule in FORWARD **immediately before** `jump ts-forward`.
   - **Expected:** Both the chain-head and the pre-jump rules exist.
   - **On failure:** Keep them scoped to exit forwarding, not overlay-admin return ([OEN-01](01-overlay-ssh-byte-cliff.md)).
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
- MUST NOT clamp overlay-admin return in the same global rule.
- MUST NOT treat DNS leak-test green as IPv6 HTTP green.
- MUST NOT select this exit on the agent workstation to reproduce.
- MUST NOT apply live network or firewall changes until Bind is filled by a human.
- MUST NOT claim a fix on ICMP ping alone when Verify names TCP, SSH, or HTTPS.
- MUST NOT publish hostnames, addresses, ULAs, or custom ports.

## Related specs

- [OEN-01 Overlay SSH byte cliff](01-overlay-ssh-byte-cliff.md)
- [OEN-06 Netfilter-off IPv6 return-path](06-netfilter-off-v6-return.md)
- [OEN-S02 clamp-mss-to-pmtu no-op](../supporting/s02-clamp-mss-to-pmtu-noop.md)
- [OEN-S32 DNS leak-test vs IPv6 data plane](../supporting/s32-dns-leak-test-not-v6-dataplane.md)
- [OEN-S18 Do not set exit on the agent workstation](../supporting/s18-do-not-set-exit-on-agent-workstation.md)

## Prior art (Not novel)

Tailscale #11002 discusses nft jump/accept before clamp. This spec’s claim is the Pi-exit recipe: top of ts-forward, pre-jump copy, re-apply after rewrite, DNS≠data plane.

