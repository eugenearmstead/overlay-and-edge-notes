---
id: OEN-20
title: "LAN unique-local + remote exit: IPv4 takes the exit, IPv6 leaks"
kind: original
status: active
edition: 1
date_published: 2026-09-08
author: Eugene Armstead
author_url: https://www.armsteadent.com/
canonical: https://eugenearmstead.github.io/overlay-and-edge-notes/networking/20-lan-ula-happy-eyeballs-leak.html
keywords:
  - "LAN ULA Happy-Eyeballs leak"
  - "IPv4 takes exit IPv6 leaks"
  - "Allow LAN Access ULA default"
  - "browser prefers v6 LAN VPN"
  - "cellular no ULA fully on exit"
  - "remote exit half-broken"
  - "table 52 missing ::/0"
  - "ip -6 route get via LAN NIC"
  - "Tailscale exit Happy Eyeballs"
  - "home LAN ULA vs selected exit"
  - "curl -4 exit curl -6 leak"
  - "Wi-Fi vs cellular exit matrix"
backs: []
backed_by:
  - OEN-S26
description: "On home Wi-Fi a remote exit can carry IPv4 while browsers prefer IPv6 via the LAN unique-local default into the commercial VPN. Cellular without that unique-local looks fully on the exit."
terms:
  - abbr: OEN
    expansion: Overlay and Edge Notes
  - abbr: SSH
    expansion: Secure Shell
  - abbr: LAN
    expansion: Local Area Network
  - abbr: WAN
    expansion: Wide Area Network
  - abbr: VPN
    expansion: Virtual Private Network
  - abbr: TCP
    expansion: Transmission Control Protocol
  - abbr: MTU
    expansion: Maximum Transmission Unit
  - abbr: ICMP
    expansion: Internet Control Message Protocol
  - abbr: HTTPS
    expansion: Hypertext Transfer Protocol Secure
  - abbr: IP
    expansion: Internet Protocol
  - abbr: IPv4
    expansion: Internet Protocol version 4
  - abbr: IPv6
    expansion: Internet Protocol version 6
  - abbr: NAT
    expansion: network address translation
  - abbr: ULA
    expansion: unique-local address (IPv6)
  - abbr: GCP
    expansion: Google Cloud Platform
  - abbr: VM
    expansion: virtual machine
  - abbr: NIC
    expansion: network interface card
  - abbr: nft
    expansion: nftables (Linux packet filter)
  - abbr: MASQUERADE
    expansion: iptables masquerade (source NAT)
  - abbr: Pi
    expansion: single-board computer (Raspberry Pi class)
  - abbr: Happy-Eyeballs
    expansion: dual-stack connection racing (RFC 8305)
---

# LAN unique-local + remote exit: IPv4 takes the exit, IPv6 leaks

## Context

A client on the home Local Area Network (LAN) has a LAN unique-local address (ULA) and an IPv6 default via the router (commercial VPN underlay). Select a **remote** `<exit-node>`: `curl -4` shows the exit; browsers prefer IPv6 (Happy-Eyeballs) → LAN VPN egress. Cellular (no LAN ULA) looks fully on the exit. It looks like “the cloud exit is half-broken.”

Distinct from [OEN-13](13-overlay-underlay-ula-layers.md) (naming the four layers), [OEN-17](17-gcp-overlay-exit.md) (cloud plumbing), and [OEN-S26](../supporting/s26-wifi-vs-cellular-underlay.md) (Wi-Fi vs cellular **underlay** to the same exit without a selected-exit ULA default). This is **Allow LAN Access / ULA default vs selected exit**.

## Topology

```text
[home LAN client] has LAN ULA + v6 default via router (commercial underlay)
Select remote <exit-node>:
    curl -4  -->  exit egress     (good)
    browser Happy-Eyeballs v6 --> LAN VPN egress  (LEAK)
Cellular (no LAN ULA) looks fully on the exit
Distinct from [OEN-S26](../supporting/s26-wifi-vs-cellular-underlay.md)
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

Allow LAN Access / ULA default vs selected exit. Table 52 missing `::/0` is a common proof.

## Decision

Operators MUST verify `ip -6 route get <public-v6>` via the LAN NIC and whether table 52 is missing `::/0` while an exit is selected. MUST compare Wi-Fi vs cellular. MUST NOT keep changing Google Cloud MTU for this signature.

## Consequences

- Operators stop tearing down a working cloud exit.
- IPv6 leak is understood as LAN ULA + Happy-Eyeballs.
- Cellular remains the clean dual-stack check.

## Agent stop rule

> A coding agent MUST emit a **bound runbook** (placeholders replaced from Bind).
> MUST NOT apply live `ip rule`, nft, iptables, ip6tables, sysctl, `wg set`, daemon restart, or deploy until a **human** filled Bind.
> MUST NOT claim a fix on ICMP ping alone when Verify names TCP, SSH, or HTTPS.
> MUST NOT file an upstream bug from this page.
> MUST NOT publish real addresses, hostnames, or custom ports.

## Procedure

Placeholders only until Bind is filled: `<cloud-vps>`, `<lan-pi>`, `<overlay-peer>`, `<exit-node>`, `<wg-iface>`, `<gcp-nic>`, plus the Bind extras on this page.

### Copy-paste commands (after Bind)

```bash
# On the LAN client (not the agent workstation if that would hairpin)
ip -6 route get 2001:4860:4860::8888
curl -4 --max-time 8 https://example.com
curl -6 --max-time 8 https://example.com
```

MUST NOT keep changing GCP MTU for this split ([OEN-17](17-gcp-overlay-exit.md)).

1. **P1 — Dual-stack fetch on Wi-Fi with exit selected.**
   - **Action:** On a LAN client (not the agent workstation): select `<exit-node>`. `curl -4` and `curl -6` to a “what is my IP” over HTTPS. Then a browser to the same family-sensitive site.
   - **Expected:** v4 shows the exit; v6 shows home-tunnel or LAN VPN egress. Browser follows v6.
   - **On failure:** If both show the exit, this spec does not apply.
2. **P2 — Route get for a public IPv6.**
   - **Action:** `ip -6 route get <public-v6>`. Note the LAN NIC vs overlay. Check table 52 for `::/0`.
   - **Expected:** v6 default still via LAN/router; table 52 missing `::/0` for the selected exit.
   - **On failure:** Do not treat this as GCP MASQUERADE until this check is done.
3. **P3 — Cellular A/B.**
   - **Action:** Same exit, same client class, cellular underlay (no LAN ULA). Repeat curl -4/-6.
   - **Expected:** Both families show the exit (or fail together for another reason).
   - **On failure:** If cellular also splits, look at [OEN-S26](../supporting/s26-wifi-vs-cellular-underlay.md) / [OEN-06](06-netfilter-off-v6-return.md).
4. **P4 — Clear the exit; confirm LAN v6 is the home path.**
   - **Action:** Clear exit-node. v6 via LAN VPN is expected at home. Document Allow LAN Access behavior privately; do not paste routes.
   - **Expected:** Without exit, v6 is home. With exit, v4 is cloud, v6 may still be home.
   - **On failure:** Do not disable IPv6 globally as the daily fix without operator consent.

## Expected samples

```text
# v6 still via LAN router, not overlay exit
2001:4860:4860::8888 from <lan-ula> via <router-lla> dev <lan-iface>
```

## Verify

- Wi-Fi + exit: curl -4 exit, curl -6 home (this trap).
- Cellular + exit: both families exit, or a different spec applies.
- table 52 ::/0 absence is recorded.
- Agent workstation was not used as the soak client.
- ICMP / small ping success was **not** used as the pass criterion when this spec names TCP, SSH, or HTTPS.
- Bind table was filled by a human before any live `ip` / nft / iptables change.

## MUST NOT

- MUST NOT publish LAN ULA or public v6 test addresses that identify the lab.
- MUST NOT blame Google Cloud NAT first for a Wi-Fi-only v6 leak.
- MUST NOT disable IPv6 as an undocumented default.
- MUST NOT set exit on the agent workstation to reproduce.
- MUST NOT apply live network or firewall changes until Bind is filled by a human.
- MUST NOT claim a fix on ICMP ping alone when Verify names TCP, SSH, or HTTPS.
- MUST NOT publish hostnames, addresses, ULAs, or custom ports.

## Related specs

- [OEN-13 Overlay vs underlay vs unique-local](13-overlay-underlay-ula-layers.md)
- [OEN-17 Google Cloud overlay exit](17-gcp-overlay-exit.md)
- [OEN-S26 Wi-Fi vs cellular underlay](../supporting/s26-wifi-vs-cellular-underlay.md)
- [OEN-S18 Do not set exit on the agent workstation](../supporting/s18-do-not-set-exit-on-agent-workstation.md)

## Prior art (Not novel)

Happy-Eyeballs v6 preference is documented. This spec’s claim is LAN ULA default versus a selected remote exit as a false “cloud exit is half-broken.”

