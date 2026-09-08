---
id: OEN-S22
title: "Identity-Aware Proxy is break-glass; overlay SSH key-exchange can fail on some cloud VMs"
kind: supporting
status: active
edition: 1
date_published: 2026-09-08
author: Eugene Armstead
author_url: https://www.armsteadent.com/
canonical: https://eugenearmstead.github.io/overlay-and-edge-notes/supporting/s22-iap-break-glass-kex.html
keywords:
  - "Identity-Aware Proxy break-glass"
  - "overlay SSH KEX fail GCE"
  - "tailscale ssh key exchange fail"
  - "plain OpenSSH overlay :22"
  - "never gcloud instances reset debug"
  - "IAP not daily door"
  - "Google Compute Engine KEX"
  - "GCP IAP SSH recovery"
  - "overlay OpenSSH not tailscale ssh"
  - "GCE image SSH KEX"
  - "break-glass Identity-Aware Proxy"
  - "do not reset VM to debug"
backs:
  - OEN-17
backed_by: []
description: "Identity-Aware Proxy is recovery. Overlay product ssh CLI may fail key exchange on some Google Compute Engine images — use plain OpenSSH. Never reset the instance as a debug step."
terms:
  - abbr: OEN
    expansion: Overlay and Edge Notes
  - abbr: SSH
    expansion: Secure Shell
  - abbr: OpenSSH
    expansion: OpenBSD Secure Shell
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
  - abbr: GCE
    expansion: Google Compute Engine
  - abbr: IAP
    expansion: Identity-Aware Proxy
  - abbr: VM
    expansion: virtual machine
  - abbr: NIC
    expansion: network interface card
  - abbr: CLI
    expansion: command-line interface
  - abbr: nft
    expansion: nftables (Linux packet filter)
  - abbr: PORT
    expansion: overlay UDP listen port setting
  - abbr: ControlPath
    expansion: OpenSSH multiplexing socket path option
  - abbr: KEX
    expansion: key exchange
  - abbr: Pi
    expansion: single-board computer (Raspberry Pi class)
---

# Identity-Aware Proxy is break-glass; overlay SSH key-exchange can fail on some cloud VMs

## Context

Daily admin is overlay OpenSSH on port 22. IAP when overlay is down. Some GCE images fail overlay `ssh` CLI KEX.

## Topology

```text
Daily: OpenSSH to overlay :22
Break-glass: Identity-Aware Proxy
Some GCE images: overlay ssh CLI KEX fail --> use plain OpenSSH
MUST NOT gcloud compute instances reset as debug
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

IAP unused in the happy path.

## Method

Prefer `ssh user@<exit-overlay>`. IAP unused in the happy path. MUST NOT `gcloud compute instances reset` as debug.

## Consequences

A KEX fail does not become a VM reset.

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
ssh -o ControlPath=none <user>@<exit-node> 'echo openssh-ok'
```

1. **P1 — Plain OpenSSH.**
   - **Action:** If overlay ssh CLI fails KEX, use OpenSSH to overlay :22.
   - **Expected:** Login works.
   - **On failure:** Do not reset the VM.
2. **P2 — IAP only when overlay is down.**
   - **Action:** IAP is documented break-glass.
   - **Expected:** Unused when overlay SSH works.
   - **On failure:** Still no reset.
3. **P3 — Then PORT/mesh.**
   - **Action:** If overlay is down, check PORT=41641 ([OEN-S23](s23-vpc-41641-useless-while-port-0.md)) and [OEN-01](../networking/01-overlay-ssh-byte-cliff.md).
   - **Expected:** Mesh UDP actually hits the VM.
   - **On failure:** Do not debug IAP first when PORT=0.

## Expected samples

```text
# overlay product ssh CLI: kex_exchange_identification error
# OpenSSH: login works
```

## Verify

- Happy path is OpenSSH overlay 22.
- No instance reset in the incident notes.
- ICMP / small ping success was **not** used as the pass criterion when this spec names TCP, SSH, or HTTPS.
- Bind table was filled by a human before any live `ip` / nft / iptables change.

## MUST NOT

- MUST NOT reset the VM as a first debug step.
- MUST NOT publish project/zone/VM names.
- MUST NOT make IAP the daily door.
- MUST NOT apply live network or firewall changes until Bind is filled by a human.
- MUST NOT claim a fix on ICMP ping alone when Verify names TCP, SSH, or HTTPS.
- MUST NOT publish hostnames, addresses, ULAs, or custom ports.

## Related specs

- [OEN-17](../networking/17-gcp-overlay-exit.md)
- [OEN-S23](s23-vpc-41641-useless-while-port-0.md)

## Prior art (Not novel)

IAP and OpenSSH are documented. This note is KEX-fail on some GCE images plus never reset.

