---
id: OEN-21
title: "Shared commercial-VPN network address translation: CrowdSec bans the whole house"
kind: original
status: active
edition: 1
date_published: 2026-09-08
author: Eugene Armstead
author_url: https://www.armsteadent.com/
canonical: https://eugenearmstead.github.io/overlay-and-edge-notes/networking/21-shared-vpn-nat-crowdsec-ban.html
keywords:
  - crowdsec
  - nat
  - vpn
  - shared-egress
backs: []
backed_by:
  - OEN-16
description: "Many LAN and overlay clients share one commercial VPN egress IP. CrowdSec banning that address takes down coordination and SSH for everyone while overlay direct UDP often still works."
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
  - abbr: TCP
    expansion: Transmission Control Protocol
  - abbr: UDP
    expansion: User Datagram Protocol
  - abbr: MSS
    expansion: Maximum Segment Size
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
  - abbr: WireGuard
    expansion: UDP-based VPN protocol
  - abbr: NAT
    expansion: network address translation
  - abbr: API
    expansion: application programming interface
  - abbr: CAPI
    expansion: CrowdSec Central API
  - abbr: nft
    expansion: nftables (Linux packet filter)
  - abbr: ControlPath
    expansion: OpenSSH multiplexing socket path option
  - abbr: Pi
    expansion: single-board computer (Raspberry Pi class)
  - abbr: CrowdSec
    expansion: open-source IDS/IPS with a Central API
---

# Shared commercial-VPN network address translation: CrowdSec bans the whole house

## Context

Many Local Area Network (LAN) and overlay clients share one commercial Virtual Private Network (VPN) egress. CrowdSec (sshd / Caddy) bans that **single public IP**. Coordination, login Hypertext Transfer Protocol Secure (HTTPS), and Secure Shell (SSH) to the Virtual Private Server (VPS) look dead for everyone. Overlay **direct User Datagram Protocol (UDP)** often still works.

Distinct from [OEN-07](07-crowdsec-capi-403.md) (Central API 403 from health probes). MUST NOT document trusted-egress push architecture, root forced-command, or token payload.

## Topology

```text
[many LAN / overlay clients] --NAT--> one commercial-VPN egress IP
CrowdSec (sshd/Caddy) bans that IP  -->  coordination/login/SSH look dead for everyone
Overlay **direct UDP** often still works
Distinct from CAPI 403 ([OEN-07](07-crowdsec-capi-403.md))
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

Treat rotating VPN egress (v4+v6) as trusted; refresh after hop ([OEN-16](16-commercial-wg-endpoint-rotation.md)). No token payloads in public notes.

## Decision

Treat rotating VPN egress (IPv4 and IPv6) as **trusted** for CrowdSec on the coordination/login host. Refresh the allow after an endpoint hop ([OEN-16](16-commercial-wg-endpoint-rotation.md)). Restart the bouncer after unban.

Generic recipe only: allowlist the current egress, not a private push bus.

## Consequences

- House traffic survives a hop without a mass ban.
- Overlay UDP staying up is no longer mistaken for “the VPS is fine.”
- Unban plus bouncer restart actually takes effect.

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
# From a client: overlay SSH tiny vs WAN SSH
ssh -o ControlPath=none <user>@<cloud-vps> 'echo overlay-ok'
# If overlay UDP works and WAN HTTPS to login is banned, check CrowdSec decisions for the VPN egress class — not a host outage.
```

1. **P1 — Split overlay UDP vs TCP login.**
   - **Action:** From a LAN client: overlay SSH or ping to `<cloud-vps>` overlay address versus HTTPS login / SSH to the public name.
   - **Expected:** Overlay UDP/mesh works; public HTTPS/SSH times out or CrowdSec-denies.
   - **On failure:** If overlay is also dead, this is not a shared-NAT ban (path or daemon).
2. **P2 — Confirm one egress, many clients.**
   - **Action:** From two LAN hosts, `curl -4` / `curl -6` “what is my IP” through the tunnel. Compare with the address CrowdSec banned (decisions list).
   - **Expected:** Same public v4/v6 as the ban. Multiple clients share it.
   - **On failure:** Do not paste the IP in public notes.
3. **P3 — Trust rotating VPN egress; unban; restart bouncer.**
   - **Action:** Add the current tunnel egress (v4 and v6) to the trusted set used by CrowdSec. Delete the ban. Restart the bouncer. After [OEN-16](16-commercial-wg-endpoint-rotation.md) hops, refresh the set.
   - **Expected:** Login HTTPS and SSH recover for the house.
   - **On failure:** If it fails after hop, the allowlist is stale — refresh, do not add more bans.
4. **P4 — Do not confuse with CAPI 403.**
   - **Action:** If `cscli capi status` is 403, that is [OEN-07](07-crowdsec-capi-403.md), not this house ban.
   - **Expected:** CAPI healthy or separately diagnosed.
   - **On failure:** Do not loop cscli to “check the ban.”

## Expected samples

```text
# Overlay SSH ok; browser to login times out; CrowdSec decision lists the shared egress
```

## Verify

- Public login works from a LAN client after unban + bouncer restart.
- Overlay UDP still worked during the ban (or this was a different outage).
- Trusted set includes current v4 and v6 egress.
- No secrets or push architecture in the public write-up.
- ICMP / small ping success was **not** used as the pass criterion when this spec names TCP, SSH, or HTTPS.
- Bind table was filled by a human before any live `ip` / nft / iptables change.

## MUST NOT

- MUST NOT publish the banned public IP or overlay addresses.
- MUST NOT document trusted-egress push, root forced-command, or token payload.
- MUST NOT name the commercial VPN provider.
- MUST NOT loop cscli capi status while diagnosing a ban.
- MUST NOT apply live network or firewall changes until Bind is filled by a human.
- MUST NOT claim a fix on ICMP ping alone when Verify names TCP, SSH, or HTTPS.
- MUST NOT publish hostnames, addresses, ULAs, or custom ports.

## Related specs

- [OEN-07 CrowdSec CAPI 403](07-crowdsec-capi-403.md)
- [OEN-16 Commercial WireGuard endpoint rotation](16-commercial-wg-endpoint-rotation.md)
- [OEN-01 Overlay SSH byte cliff](01-overlay-ssh-byte-cliff.md)

## Prior art (Not novel)

CrowdSec bans by source IP are documented. This spec’s claim is shared commercial-VPN NAT as a whole-house outage while overlay UDP still works.

