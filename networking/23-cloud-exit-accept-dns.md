---
id: "OEN-23"
title: "Cloud-exit accept-dns=true pretty-prints, breaks overlay peer-API DNS"
kind: "original"
status: "active"
edition: 2
date_published: "2026-09-08"
author: "Eugene Armstead"
author_url: "https://www.armsteadent.com/"
canonical: "https://eugenearmstead.github.io/overlay-and-edge-notes/networking/23-cloud-exit-accept-dns.html"
keywords:
  - "accept-dns=true breaks PeerAPI"
  - "tailscale dns query pretty print"
  - "GCE accept-dns metadata 169.254"
  - "do not fix DNS display on exit"
  - "accept-dns=false metadata resolver"
  - "host dig vs exit DoH path"
  - "cloud exit accept-dns"
  - "PeerAPI RD=0 after accept-dns"
  - "Google Compute Engine Tailscale DNS"
  - "169.254.169.254 not PeerAPI"
  - "Headscale exit accept-dns"
  - "pretty dns query broken exit"
backs:
  []
backed_by:
  - OEN-19
  - OEN-14
  - OEN-17
description: "On Google Compute Engine-like hosts, accept-dns=true makes tailscale dns query look pretty and breaks the Recursion Desired-off exit DNS path."
terms:
  - abbr: API
    expansion: application programming interface
  - abbr: CLI
    expansion: command-line interface
  - abbr: ControlPath
    expansion: OpenSSH multiplexing socket path option
  - abbr: DNS
    expansion: Domain Name System
  - abbr: DoH
    expansion: DNS over HTTPS
  - abbr: GCE
    expansion: Google Compute Engine
  - abbr: GCP
    expansion: Google Cloud Platform
  - abbr: HTTP
    expansion: Hypertext Transfer Protocol
  - abbr: HTTPS
    expansion: Hypertext Transfer Protocol Secure
  - abbr: JSON
    expansion: JavaScript Object Notation
  - abbr: LAN
    expansion: Local Area Network
  - abbr: NOERROR
    expansion: DNS response code meaning the query succeeded
  - abbr: OEN
    expansion: Overlay and Edge Notes
  - abbr: PeerAPI
    expansion: overlay peer application-programming interface (exit DNS over HTTPS)
  - abbr: Pi
    expansion: single-board computer (Raspberry Pi class)
  - abbr: RD
    expansion: Recursion Desired (DNS flag)
  - abbr: REFUSES
    expansion: DNS response code meaning the server will not answer
  - abbr: SSH
    expansion: Secure Shell
  - abbr: Unbound
    expansion: validating recursive DNS resolver
  - abbr: VM
    expansion: virtual machine
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
| `<overlay-impl>` | Overlay implementation class | `tailscale-compatible` or other — stop and translate CLI |
| `<user>` | SSH user | Guest account |
| `<exit-node>` | Overlay exit node | Cloud VM or LAN Pi |
| `<overlay-peer>` | Soak client (not the agent workstation) | LAN Pi or phone |

## Formulas

Do not “fix DNS display” on an exit VM. Metadata resolver is not PeerAPI.

## Decision

Exit virtual machines MUST keep `accept-dns=false`. MUST NOT “fix DNS display” on an exit VM. Prove exit DNS with PeerAPI DoH from a non-exit client.

## Consequences

- Pretty guest DNS is sacrificed; exit-client DNS works.
- Metadata resolver is ignored as a canary.
- Operators stop flipping accept-dns during incidents.

## Agent stop rule

> MUST emit bound `accept-dns` / `tailscale dns query` commands only after `<overlay-impl>` is `tailscale-compatible`.
> MUST NOT set `accept-dns=true` on an exit VM to pretty-print.
> MUST NOT apply netfilter from this page.

## Procedure

This spec does not apply if `<overlay-impl>` is not tailscale-compatible.

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

## MUST NOT

- MUST NOT set accept-dns=true on an exit VM to pretty-print.
- MUST NOT treat metadata 169.254.169.254 as PeerAPI.
- MUST NOT publish GCP project or VM names.
- MUST NOT use leak-test 502 as proof the exit is down.
- MUST NOT publish hostnames, addresses, ULAs, or custom ports.

## Page changelog

- Edition 2 (8 Sep 2026, Mountain Time): Trap-specific Bind and agent stop rule (review cleanup).

## Related specs

- [OEN-17 Google Cloud overlay exit](17-gcp-overlay-exit.md)
- [OEN-14 Exit DNS is PeerAPI](14-exit-dns-is-peerapi.md)
- [OEN-19 Unbound REFUSES RD=0](19-unbound-refuses-rd0.md)
- [OEN-S18 Do not set exit on the agent workstation](../supporting/s18-do-not-set-exit-on-agent-workstation.md)

