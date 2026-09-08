---
id: OEN-23
title: "Cloud-exit accept-dns=true pretty-prints, breaks overlay peer-API DNS"
kind: original
status: active
edition: 1
date_published: 2026-09-08
author: Eugene Armstead
author_url: https://www.armsteadent.com/
canonical: https://eugenearmstead.github.io/overlay-and-edge-notes/networking/23-cloud-exit-accept-dns.html
keywords:
  - exit-node
  - accept-dns
  - peerapi
  - gce
backs: []
backed_by:
  - OEN-19
  - OEN-14
  - OEN-17
description: "On Google Compute Engine-like hosts, accept-dns=true makes tailscale dns query look pretty and breaks the Recursion Desired-off exit DNS path."
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
  - abbr: MTU
    expansion: Maximum Transmission Unit
  - abbr: ICMP
    expansion: Internet Control Message Protocol
  - abbr: HTTP
    expansion: Hypertext Transfer Protocol
  - abbr: HTTPS
    expansion: Hypertext Transfer Protocol Secure
  - abbr: DNS
    expansion: Domain Name System
  - abbr: DoH
    expansion: DNS over HTTPS
  - abbr: GCP
    expansion: Google Cloud Platform
  - abbr: GCE
    expansion: Google Compute Engine
  - abbr: VM
    expansion: virtual machine
  - abbr: NIC
    expansion: network interface card
  - abbr: API
    expansion: application programming interface
  - abbr: PeerAPI
    expansion: overlay peer application-programming interface (exit DNS over HTTPS)
  - abbr: RD
    expansion: Recursion Desired (DNS flag)
  - abbr: nft
    expansion: nftables (Linux packet filter)
  - abbr: ControlPath
    expansion: OpenSSH multiplexing socket path option
  - abbr: JSON
    expansion: JavaScript Object Notation
  - abbr: Pi
    expansion: single-board computer (Raspberry Pi class)
  - abbr: REFUSES
    expansion: DNS response code meaning the server will not answer
  - abbr: Unbound
    expansion: validating recursive DNS resolver
  - abbr: NOERROR
    expansion: DNS response code meaning the query succeeded
---

# Cloud-exit accept-dns=true pretty-prints, breaks overlay peer-API DNS

## Context

On Google Compute Engine (GCE)-like hosts, `tailscale dns query` with `accept-dns=false` often shows metadata `169.254.169.254`. Turning `accept-dns=true` makes the display pretty and **breaks** the overlay peer-API (PeerAPI) Recursion Desired (RD)=0 exit Domain Name System (DNS) path ([OEN-19](19-unbound-refuses-rd0.md), [OEN-14](14-exit-dns-is-peerapi.md), [OEN-17](17-gcp-overlay-exit.md)).

Host `dig` is not the exit-client DNS over HTTPS (DoH) path.

## Topology

```text
[GCE-like <exit-node>]
    accept-dns=false:  dns query may show metadata 169.254.169.254  (pretty-print, ignore)
    accept-dns=true:   display pretty, **breaks** PeerAPI RD=0 path ([OEN-19](19-unbound-refuses-rd0.md))
Host dig ≠ exit-client DoH
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

Do not “fix DNS display” on an exit VM. Metadata resolver is not PeerAPI.

## Decision

Exit virtual machines MUST keep `accept-dns=false`. MUST NOT “fix DNS display” on an exit VM. Prove exit DNS with PeerAPI DoH from a non-exit client.

## Consequences

- Pretty guest DNS is sacrificed; exit-client DNS works.
- Metadata resolver is ignored as a canary.
- Operators stop flipping accept-dns during incidents.

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
ssh -o ControlPath=none <user>@<exit-node> 'tailscale status --json | head -c 200'  # or overlay equivalent; do not paste JSON publicly
# Keep accept-dns=false on the exit VM. Prove DNS from a non-exit client via PeerAPI.
```

1. **P1 — Record accept-dns and dns query.**
   - **Action:** On `<exit-node>`: overlay `status` / prefs for accept-dns. Run `tailscale dns query example.com` (or equivalent).
   - **Expected:** accept-dns is false. Query may show 169.254.169.254. That is guest pretty-print, not PeerAPI.
   - **On failure:** If accept-dns is already true, set false and restart the daemon once.
2. **P2 — Prove PeerAPI from a non-exit client.**
   - **Action:** From `<overlay-peer>`, DoH to PeerAPIURL. `curl -4` / `curl -6` through the exit to example.com.
   - **Expected:** DoH NOERROR; HTTP 200.
   - **On failure:** Do not use guest dig as the gate.
3. **P3 — Do not enable accept-dns to pretty-print.**
   - **Action:** Leave accept-dns false even if dns query looks ugly.
   - **Expected:** PeerAPI path still works after a daemon restart.
   - **On failure:** If someone enabled it, disable; retest RD=0 ([OEN-19](19-unbound-refuses-rd0.md)).
4. **P4 — Leak-test HTTP 502 is not this bug.**
   - **Action:** Some leak-test sites return 502 from Google Cloud ranges. Use example.com as the browse gate ([OEN-17](17-gcp-overlay-exit.md)).
   - **Expected:** example.com 200 through the exit.
   - **On failure:** Do not flip accept-dns because a leak-test site 502’d.

## Expected samples

```text
# Guest pretty-print (not exit DoH)
169.254.169.254
```

## Verify

- accept-dns=false on the exit VM.
- PeerAPI DoH from a non-exit client works.
- Guest dns query may still show metadata — ignored.
- Agent workstation exit unset.
- ICMP / small ping success was **not** used as the pass criterion when this spec names TCP, SSH, or HTTPS.
- Bind table was filled by a human before any live `ip` / nft / iptables change.

## MUST NOT

- MUST NOT set accept-dns=true on an exit VM to pretty-print.
- MUST NOT treat metadata 169.254.169.254 as PeerAPI.
- MUST NOT publish GCP project or VM names.
- MUST NOT use leak-test 502 as proof the exit is down.
- MUST NOT apply live network or firewall changes until Bind is filled by a human.
- MUST NOT claim a fix on ICMP ping alone when Verify names TCP, SSH, or HTTPS.
- MUST NOT publish hostnames, addresses, ULAs, or custom ports.

## Related specs

- [OEN-17 Google Cloud overlay exit](17-gcp-overlay-exit.md)
- [OEN-14 Exit DNS is PeerAPI](14-exit-dns-is-peerapi.md)
- [OEN-19 Unbound REFUSES RD=0](19-unbound-refuses-rd0.md)
- [OEN-S18 Do not set exit on the agent workstation](../supporting/s18-do-not-set-exit-on-agent-workstation.md)

## Prior art (Not novel)

accept-dns is a documented overlay flag. This spec’s claim is pretty-print versus PeerAPI RD=0 on GCE-like exit VMs.

