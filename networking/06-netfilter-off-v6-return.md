---
id: "OEN-06"
title: "Netfilter-off IPv6 return-path blackhole"
kind: "original"
status: "active"
edition: 2
date_published: "2026-09-08"
author: "Eugene Armstead"
author_url: "https://www.armsteadent.com/"
canonical: "https://eugenearmstead.github.io/overlay-and-edge-notes/networking/06-netfilter-off-v6-return.html"
keywords:
  - "NetfilterMode=off IPv6 blackhole"
  - "nft prerouting mark FIB"
  - "ip6tables MARK MASQUERADE"
  - "overlay ULA /48 table 52"
  - "FORWARD tunnel overlay 0 packets"
  - "IPv6 return path blackhole"
  - "iptables-nft mark before fib"
  - "exit node IPv6 SNAT"
  - "Tailscale netfilter off"
  - "conntrack split nft ip6tables"
  - "ip -6 route get iif tunnel"
  - "Headscale ULA return"
backs:
  []
backed_by:
  - OEN-S27
description: "With overlay netfilter off, an nft prerouting mark does not win the first IPv6 route lookup. Use one ip6tables path and install the overlay unique-local /48 on table 52 and main."
terms:
  - abbr: ControlPath
    expansion: OpenSSH multiplexing socket path option
  - abbr: DNS
    expansion: Domain Name System
  - abbr: FIB
    expansion: forwarding information base
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
  - abbr: MARK
    expansion: netfilter packet mark
  - abbr: MASQUERADE
    expansion: iptables masquerade (source NAT)
  - abbr: NAT
    expansion: network address translation
  - abbr: nft
    expansion: nftables (Linux packet filter)
  - abbr: NIC
    expansion: network interface card
  - abbr: OEN
    expansion: Overlay and Edge Notes
  - abbr: Pi
    expansion: single-board computer (Raspberry Pi class)
  - abbr: POSTROUTING
    expansion: netfilter postrouting chain
  - abbr: PREROUTING
    expansion: netfilter prerouting chain
  - abbr: SNAT
    expansion: source network address translation
  - abbr: SSH
    expansion: Secure Shell
  - abbr: TCP
    expansion: Transmission Control Protocol
  - abbr: ULA
    expansion: unique-local address (IPv6)
  - abbr: VM
    expansion: virtual machine
  - abbr: VPS
    expansion: Virtual Private Server
  - abbr: WAN
    expansion: Wide Area Network
---

# Netfilter-off IPv6 return-path blackhole

## Context

On a cloud Virtual Private Server (VPS) `<exit-node>` with overlay **NetfilterMode=off**, IPv6 exit can egress while return dies. Source network address translation (SNAT) / MASQUERADE counters increment; `FORWARD` from the commercial tunnel toward the overlay stays 0. `ip -6 route get <overlay-ula> iif <tunnel>` points at the **public NIC**, not back into overlay.

nft prerouting MARK on the overlay iface did **not** apply before the first forwarding information base (FIB) lookup when the backend was iptables-nft. Unmarked IPv6 went out the VPS public NIC. Splitting nft mark plus a separate ip6tables MASQUERADE broke conntrack return.

IPv4 often already has /32 overlays on table 52 and main. The IPv6 unique-local address (ULA) **/48** was missing with netfilter off.

## Topology

```text
[exit client] --v6--> [<exit-node> overlay]
    mark in PREROUTING (iptables-nft)  --X-->  first FIB lookup still uses WAN NIC  (TRAP)
    ip -6 route get <overlay-ula> iif <tunnel>  shows <wan-iface>   (proof)
    FIX: overlay ULA /48 on table 52 AND main; one ip6tables MASQUERADE path
```

## Bind

Fill this table **before** any live change. Do **not** paste real values back into public notes.

| Placeholder | Operator fills | Class |
|-------------|----------------|-------|
| `<user>` | SSH user | Guest account |
| `<exit-node>` | Overlay exit node | Cloud VM or LAN Pi |
| `<overlay-ula>` | Overlay unique-local prefix class | ULA /48; never publish |
| `<wg-iface>` | Commercial WireGuard iface | Router or VPS client |
| `<wan-iface>` | WAN / public NIC | Router or VPS |
| `<gcp-nic>` | Public NIC on a Google Cloud guest | Iface; omit on non-GCP exits |
| `<tunnel>` | Commercial tunnel iface on the exit | Iface |
| `<overlay-peer>` | Soak client (not the agent workstation) | LAN Pi or phone |

## Formulas

Do not publish a real ULA. Use `<overlay-ula>` as a prefix class (`/48`). Measure, do not invent table numbers if this guest uses another policy table — list `ip -6 rule` first.

## Decision

Use **one** ip6tables path: mangle PREROUTING MARK plus source-based MASQUERADE on the tunnel. Install the overlay ULA `/48` on **table 52 and main**.

MUST NOT split nft + ip6tables MASQUERADE. MUST NOT paste a real node ULA in public text — write `<overlay-ula>` / “overlay ULA /48”.

## Consequences

- Exit-client IPv6 HTTPS returns.
- FORWARD tunnel→overlay counters increment.
- Conntrack stays on one family of tools.

## Agent stop rule

> MUST emit a bound runbook (`ip -6 rule`, nft/iptables variants, v4 and v6) after Bind is filled.
> MUST NOT apply `ip rule`, nft, iptables, or sysctl until a human filled Bind.
> MUST NOT claim the trap is fixed because ICMP ping succeeded — Verify is exit-client HTTPS both families.
> MUST NOT file an overlay-product bug from this page.

## Procedure


### Copy-paste commands (after Bind)

```bash
ssh -o ControlPath=none <user>@<exit-node> 'ip -6 rule; ip -6 route show table 52; ip -6 route show table main | head'
ip -6 route get <overlay-ula> iif <wg-iface>
# Want: via overlay, not dev <wan-iface> / <gcp-nic>

ip6tables -t mangle -S PREROUTING
ip6tables -t nat -S POSTROUTING
nft list ruleset | grep -i masquerade || true
```

MUST NOT split nft MASQUERADE and ip6tables MASQUERADE. MUST NOT add a second `-o <gcp-nic>` MASQUERADE ([OEN-17](17-gcp-overlay-exit.md)).

1. **P1 — Capture the blackhole signature.**
   - **Action:** On `<exit-node>`, attempt exit-client `curl -6`. Watch ip6tables SNAT/MASQUERADE counters vs FORWARD `<tunnel>→overlay`. `ip -6 route get <overlay-ula> iif <tunnel>`.
   - **Expected:** SNAT increments; FORWARD overlay is 0; route get shows the public NIC.
   - **On failure:** If FORWARD already carries return, this spec does not apply.
2. **P2 — One ip6tables path.**
   - **Action:** Remove extra nft MASQUERADE on `<gcp-nic>` or the VPS NIC. Keep mangle PREROUTING MARK and MASQUERADE on the **tunnel** in ip6tables only ([OEN-S27](../supporting/s27-iptables-nft-mark-before-fib.md)).
   - **Expected:** No duplicate masquerade. One tool family.
   - **On failure:** Do not add more NAT to “help.”
3. **P3 — Install overlay ULA /48 on table 52 and main.**
   - **Action:** `ip -6 route` in table 52 and main. Add the overlay ULA `/48` via the overlay iface on **both** if missing.
   - **Expected:** `ip -6 route get <overlay-ula> iif <tunnel>` now enters overlay, not the public NIC.
   - **On failure:** Restarting overlay alone does not install the prefix — add the route.
4. **P4 — Soak IPv6 from a LAN Pi.**
   - **Action:** On `<overlay-peer>`, select `<exit-node>`, `curl -6 https://example.com`, then clear the exit.
   - **Expected:** HTTP 200. Egress is the cloud, not the home tunnel.
   - **On failure:** If v4 works and v6 leaks home on Wi-Fi, see [OEN-20](20-lan-ula-happy-eyeballs-leak.md) / [OEN-S26](../supporting/s26-wifi-vs-cellular-underlay.md).

## Expected samples

```text
# Trap: mark counters up, route still WAN
<overlay-ula> from :: via <link-local> dev <wan-iface> src <gua>

# After /48 on table 52 and main
<overlay-ula> from :: dev <overlay-tun> src <overlay-v6>
```

## Verify

- FORWARD tunnel→overlay increments on v6 return.
- ULA /48 exists on table 52 and main.
- No split nft+ip6tables MASQUERADE.
- example.com 200 over IPv6 through the exit from a non-workstation client.
- ICMP / small ping success was **not** used as the pass criterion when this spec names TCP, SSH, or HTTPS.
- Bind table was filled by a human before any live `ip` / nft / iptables change.

## MUST NOT

- MUST NOT publish real overlay ULA node addresses.
- MUST NOT split nft mark and ip6tables MASQUERADE.
- MUST NOT add a second IPv6 MASQUERADE on the public NIC ([OEN-17](17-gcp-overlay-exit.md)).
- MUST NOT test from the agent workstation ([OEN-S18](../supporting/s18-do-not-set-exit-on-agent-workstation.md)).
- MUST NOT apply live network or firewall changes until Bind is filled by a human.
- MUST NOT claim a fix on ICMP ping alone when Verify names TCP, SSH, or HTTPS.
- MUST NOT publish hostnames, addresses, ULAs, or custom ports.

## Page changelog

- Edition 2 (8 Sep 2026, Mountain Time): Trap-specific Bind and agent stop rule (review cleanup).

## Related specs

- [OEN-17 Google Cloud overlay exit](17-gcp-overlay-exit.md)
- [OEN-S27 iptables-nft MARK before FIB](../supporting/s27-iptables-nft-mark-before-fib.md)
- [OEN-S32 DNS leak-test vs data plane](../supporting/s32-dns-leak-test-not-v6-dataplane.md)
- [OEN-13 Overlay vs underlay vs unique-local](13-overlay-underlay-ula-layers.md)

## Prior art (Not novel)

Policy routing and table 52 appear in overlay exit docs. This spec’s claim is netfilter-off + nft mark missing the first FIB lookup + missing v6 /48 + split MASQUERADE as one failure cluster.

