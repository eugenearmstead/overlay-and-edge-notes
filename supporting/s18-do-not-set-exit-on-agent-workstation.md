---
id: "OEN-S18"
title: "Do not set exit-node on the agent workstation"
kind: "supporting"
status: "active"
edition: 2
date_published: "2026-09-08"
author: "Eugene Armstead"
author_url: "https://www.armsteadent.com/"
canonical: "https://eugenearmstead.github.io/overlay-and-edge-notes/supporting/s18-do-not-set-exit-on-agent-workstation.html"
keywords:
  - "do not set exit-node on agent workstation"
  - "tailscale set --exit-node workstation"
  - "overlay SSH first nmap after fail"
  - "Cursor workstation exit-node"
  - "do not test GCP exit from agent"
  - "hairpin LAN via workstation exit"
  - "operator must ask exit-node"
  - "Tailscale exit on workstation"
  - "debug from overlay SSH"
  - "nmap after failed connect"
  - "S18 workstation exit"
  - "agent must not select exit"
backs:
  - OEN-17
  - OEN-04
  - OEN-20
backed_by:
  []
description: "Do not tailscale set --exit-node on the agent workstation unless the operator asks. Overlay SSH first. nmap only after a failed connect."
terms:
  - abbr: DNS
    expansion: Domain Name System
  - abbr: LAN
    expansion: Local Area Network
  - abbr: OEN
    expansion: Overlay and Edge Notes
  - abbr: Pi
    expansion: single-board computer (Raspberry Pi class)
  - abbr: SSH
    expansion: Secure Shell
  - abbr: VM
    expansion: virtual machine
  - abbr: VPS
    expansion: Virtual Private Server
---

# Do not set exit-node on the agent workstation

## Context

Selecting an exit on the Cursor/agent host can strand the session (hairpin, DNS, or a bad cloud exit). Overlay SSH to nodes does not require an exit.

## Topology

```text
[agent workstation] --set exit-node-->  loses general internet when exit is wrong
Soak exits on <lan-pi> / <overlay-peer>
Overlay SSH first; nmap only after a failed connect
```

## Bind

Fill this table **before** any live change. Do **not** paste real values back into public notes.

| Placeholder | Operator fills | Class |
|-------------|----------------|-------|
| `<overlay-peer>` | Soak client (not the agent workstation) | LAN Pi or phone |
| `<exit-node>` | Overlay exit node | Cloud VM or LAN Pi |
| `<lan-pi>` | Always-on LAN Pi | LAN Pi |
| `<cloud-vps>` | Cloud VPS under test | Cloud VPS |

## Formulas

MUST NOT select <exit-node> on the agent/Cursor workstation unless the operator asks.

## Method

MUST NOT set exit-node on the agent workstation unless the operator explicitly asks. Soak exits from `<overlay-peer>` / a phone.

## Consequences

Agent sessions keep internet. Exit tests still happen on a Pi.

## Agent stop rule

> MUST NOT `tailscale set --exit-node` on the agent workstation unless the operator asks.
> This spec does not apply if `<overlay-impl>` is not tailscale-compatible.
> MUST soak exits from `<overlay-peer>` or a phone.
> MUST NOT apply netfilter from this page.

## Procedure


### Copy-paste commands (after Bind)

```bash
# On the workstation: confirm exit unset
# On <overlay-peer>: select <exit-node> briefly, curl, then clear
```

1. **P1 — Check prefs.**
   - **Action:** On the workstation: overlay exit is unset.
   - **Expected:** No exit-node.
   - **On failure:** If set, clear it unless the operator asked.
2. **P2 — Connect overlay SSH first.**
   - **Action:** SSH to `<lan-pi>` / `<cloud-vps>` overlay. nmap only after a failed connect.
   - **Expected:** SSH works without an exit.
   - **On failure:** Do not debug the exit by enabling it here.
3. **P3 — Soak elsewhere.**
   - **Action:** Exit soak on `<overlay-peer>` ([OEN-17](../networking/17-gcp-overlay-exit.md)).
   - **Expected:** Workstation remains unset.
   - **On failure:** Hairpin is [OEN-S21](s21-cloud-exit-hairpin-lan.md).

## Expected samples

```text
# workstation: ExitNode: (none)
```

## Verify

- Workstation exit unset.
- Exit soak documented on a Pi or phone.

## MUST NOT

- MUST NOT set exit on the agent workstation to reproduce.
- MUST NOT nmap before the first connect when using connect wrappers.
- MUST NOT publish hostnames, addresses, ULAs, or custom ports.

## Page changelog

- Edition 2 (8 Sep 2026, Mountain Time): Trap-specific Bind and agent stop rule (review cleanup).

## Related specs

- [OEN-17](../networking/17-gcp-overlay-exit.md)
- [OEN-S21](s21-cloud-exit-hairpin-lan.md)

## Prior art (Not novel)

Exit nodes are documented. This note is “not on the agent workstation” as a hard MUST NOT.

