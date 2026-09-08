---
id: OEN-S23
title: "Cloud firewall UDP 41641 is useless while overlay PORT=0"
kind: supporting
status: active
edition: 1
date_published: 2026-09-08
author: Eugene Armstead
author_url: https://www.armsteadent.com/
canonical: https://eugenearmstead.github.io/overlay-and-edge-notes/supporting/s23-vpc-41641-useless-while-port-0.html
keywords:
  - port
  - vpc
  - udp
  - 41641
backs:
  - OEN-17
  - OEN-01
backed_by: []
description: "A VPC allow for UDP 41641 does nothing while the overlay daemon has PORT=0 (ephemeral). Ship PORT, daemon restart, guest firewall, and VPC together. Never leave PORT empty."
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
  - abbr: UDP
    expansion: User Datagram Protocol
  - abbr: MTU
    expansion: Maximum Transmission Unit
  - abbr: ICMP
    expansion: Internet Control Message Protocol
  - abbr: HTTPS
    expansion: Hypertext Transfer Protocol Secure
  - abbr: GCP
    expansion: Google Cloud Platform
  - abbr: VM
    expansion: virtual machine
  - abbr: VPC
    expansion: Virtual Private Cloud
  - abbr: NIC
    expansion: network interface card
  - abbr: nft
    expansion: nftables (Linux packet filter)
  - abbr: PORT
    expansion: overlay UDP listen port setting
  - abbr: ControlPath
    expansion: OpenSSH multiplexing socket path option
  - abbr: Pi
    expansion: single-board computer (Raspberry Pi class)
  - abbr: UFW
    expansion: Uncomplicated Firewall
  - abbr: UNCONN
    expansion: ss(8) unconnected socket state
---

# Cloud firewall UDP 41641 is useless while overlay PORT=0

## Context

Empty `PORT=` can fail daemon start. Opening the cloud firewall while listen is ephemeral is a decoration.

## Topology

```text
VPC allow UDP 41641  +  daemon PORT=0 (ephemeral)  =  decoration
Empty PORT= can fail start
Ship PORT=41641 + restart + guest firewall + VPC together
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

Production listen MUST be 41641, not a random high port.

## Method

PORT MUST be 41641 in production. Restart daemon. Allow UDP 41641 on guest firewall and VPC together.

## Consequences

Mesh UDP actually arrives. Firewall rules match reality.

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
ssh -o ControlPath=none <user>@<exit-node> 'ss -ulnp | grep 41641'
```

1. **P1 — ss the listen port.**
   - **Action:** `ss`/`netstat` UDP. Production MUST show 41641, not a random high port.
   - **Expected:** Fixed 41641.
   - **On failure:** If 0/ephemeral, set PORT and restart.
2. **P2 — VPC + guest together.**
   - **Action:** Cloud firewall UDP 41641 plus guest UFW/iptables. Never only VPC.
   - **Expected:** Both exist.
   - **On failure:** VPC alone with PORT=0 is a no-op.
3. **P3 — Do not leave PORT empty.**
   - **Action:** Empty PORT can fail start. Never empty.
   - **Expected:** Daemon running, 41641 listening.
   - **On failure:** Then large SSH ([OEN-01](../networking/01-overlay-ssh-byte-cliff.md)).

## Expected samples

```text
UNCONN ... 0.0.0.0:41641
```

## Verify

- UDP 41641 listening.
- VPC and guest allow it.
- PORT not empty/0.
- ICMP / small ping success was **not** used as the pass criterion when this spec names TCP, SSH, or HTTPS.
- Bind table was filled by a human before any live `ip` / nft / iptables change.

## MUST NOT

- MUST NOT count on VPC 41641 while PORT=0.
- MUST NOT leave PORT empty.
- MUST NOT publish project ids.
- MUST NOT apply live network or firewall changes until Bind is filled by a human.
- MUST NOT claim a fix on ICMP ping alone when Verify names TCP, SSH, or HTTPS.
- MUST NOT publish hostnames, addresses, ULAs, or custom ports.

## Related specs

- [OEN-17](../networking/17-gcp-overlay-exit.md)
- [OEN-01](../networking/01-overlay-ssh-byte-cliff.md)

## Prior art (Not novel)

Allow UDP 41641 is in every overlay-on-GCP tutorial. This note is PORT=0 making that allow useless.

