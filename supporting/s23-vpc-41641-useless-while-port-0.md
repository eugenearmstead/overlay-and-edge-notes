---
id: "OEN-S23"
title: "Cloud firewall UDP 41641 is useless while overlay PORT=0"
kind: "supporting"
status: "active"
edition: 2
date_published: "2026-09-08"
author: "Eugene Armstead"
author_url: "https://www.armsteadent.com/"
canonical: "https://eugenearmstead.github.io/overlay-and-edge-notes/supporting/s23-vpc-41641-useless-while-port-0.html"
keywords:
  - "VPC UDP 41641 useless PORT=0"
  - "overlay PORT must be 41641"
  - "never leave PORT empty"
  - "cloud firewall 41641 no-op"
  - "Tailscale PORT=0 ephemeral"
  - "ship PORT daemon UFW VPC together"
  - "GCE allow 41641 still down"
  - "overlay listen port 0"
  - "Headscale UDP 41641"
  - "empty PORT daemon fail"
  - "fixed overlay UDP port"
  - "VPC rule while PORT=0"
backs:
  - OEN-17
  - OEN-01
backed_by:
  []
description: "A VPC allow for UDP 41641 does nothing while the overlay daemon has PORT=0 (ephemeral). Ship PORT, daemon restart, guest firewall, and VPC together. Never leave PORT empty."
terms:
  - abbr: ControlPath
    expansion: OpenSSH multiplexing socket path option
  - abbr: GCP
    expansion: Google Cloud Platform
  - abbr: LAN
    expansion: Local Area Network
  - abbr: OEN
    expansion: Overlay and Edge Notes
  - abbr: Pi
    expansion: single-board computer (Raspberry Pi class)
  - abbr: PORT
    expansion: overlay UDP listen port setting
  - abbr: SSH
    expansion: Secure Shell
  - abbr: UDP
    expansion: User Datagram Protocol
  - abbr: UFW
    expansion: Uncomplicated Firewall
  - abbr: UNCONN
    expansion: ss(8) unconnected socket state
  - abbr: VM
    expansion: virtual machine
  - abbr: VPC
    expansion: Virtual Private Cloud
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
| `<user>` | SSH user | Guest account |
| `<exit-node>` | Overlay exit node | Cloud VM or LAN Pi |

## Formulas

Production listen MUST be 41641, not a random high port.

## Method

PORT MUST be 41641 in production. Restart daemon. Allow UDP 41641 on guest firewall and VPC together.

## Consequences

Mesh UDP actually arrives. Firewall rules match reality.

## Agent stop rule

> MUST emit bound overlay listen-port vs cloud-firewall checks after Bind is filled.
> MUST NOT treat UDP 41641 allow as sufficient while overlay PORT=0.
> MUST NOT publish project or VM names.

## Procedure


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

## MUST NOT

- MUST NOT count on VPC 41641 while PORT=0.
- MUST NOT leave PORT empty.
- MUST NOT publish project ids.
- MUST NOT publish hostnames, addresses, ULAs, or custom ports.

## Page changelog

- Edition 2 (8 Sep 2026, Mountain Time): Trap-specific Bind and agent stop rule (review cleanup).

## Related specs

- [OEN-17](../networking/17-gcp-overlay-exit.md)
- [OEN-01](../networking/01-overlay-ssh-byte-cliff.md)

## Prior art (Not novel)

Allow UDP 41641 is in every overlay-on-GCP tutorial. This note is PORT=0 making that allow useless.

