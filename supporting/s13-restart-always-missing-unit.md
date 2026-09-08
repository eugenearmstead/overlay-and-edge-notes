---
id: OEN-S13
title: "Restart=always on a missing unit hung the workstation"
kind: supporting
status: active
edition: 1
date_published: 2026-09-08
author: Eugene Armstead
author_url: https://www.armsteadent.com/
canonical: https://eugenearmstead.github.io/overlay-and-edge-notes/supporting/s13-restart-always-missing-unit.html
keywords:
  - "Restart=always missing ExecStart"
  - "systemd crash-loop hung workstation"
  - "150k failed restarts"
  - "leftover units bind other host"
  - "systemctl --user crash loop"
  - "always-on jobs always-on host"
  - "Restart=always missing unit"
  - "2-core box restart storm"
  - "user systemd hung"
  - "ExecStart path gone"
  - "audit crash-loop units"
  - "systemd StartLimit"
backs: []
backed_by: []
description: "Restart=always on a missing ExecStart produced 150k+ failed restarts plus leftover units binding another host’s addresses on a 2-core box."
terms:
  - abbr: OEN
    expansion: Overlay and Edge Notes
  - abbr: SSH
    expansion: Secure Shell
  - abbr: VPS
    expansion: Virtual Private Server
  - abbr: LAN
    expansion: Local Area Network
  - abbr: TCP
    expansion: Transmission Control Protocol
  - abbr: ICMP
    expansion: Internet Control Message Protocol
  - abbr: HTTPS
    expansion: Hypertext Transfer Protocol Secure
  - abbr: nft
    expansion: nftables (Linux packet filter)
  - abbr: Pi
    expansion: single-board computer (Raspberry Pi class)
  - abbr: systemd
    expansion: Linux service manager
---

# Restart=always on a missing unit hung the workstation

## Context

Always-on jobs belong on an always-on host. A user systemd unit with Restart=always and a vanished ExecStart can peg a workstation. Leftover units may bind another host’s addresses.

## Topology

```text
systemd --user Restart=always + missing ExecStart
--> 150k+ failed restarts on a 2-core workstation
Leftover units may bind another host's addresses
```

## Bind

Fill this table **before** any live change. Do **not** paste real values back into public notes.

| Placeholder | Operator fills | Class |
|-------------|----------------|-------|
| `<repo-changelog>` | Canonical Markdown file in the private ops repo | Path class, not inventory |
| `<on-device-changelog>` | On-device copy for that node class | Path class |
| `<node>` | Role name (cloud VPS, LAN Pi, router, workstation) | Role, not hostname |


## Formulas

Always-on jobs belong on an always-on host, not the agent workstation.

## Method

Audit `systemctl --user` for crash-loop units. MUST NOT use Restart=always on a unit whose binary may be missing. Always-on work belongs on `<lan-pi>` or `<cloud-vps>`.

## Consequences

Workstation load returns to normal. Foreign binds go away.

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
systemctl --user --failed
systemctl --user list-units --type=service --state=failed,activating
```

1. **P1 — Find crash loops.**
   - **Action:** `systemctl --user --failed` and `status` on looping units. Count NRestarts.
   - **Expected:** A missing ExecStart with huge restart count.
   - **On failure:** Do not keep the unit enabled.
2. **P2 — Stop and disable.**
   - **Action:** Stop/disable the unit. Remove foreign bind leftovers.
   - **Expected:** Load drops. Addresses unbound.
   - **On failure:** Do not Restart=always again without a guard.
3. **P3 — Move always-on work.**
   - **Action:** Timers that must run 24/7 go to an always-on Pi/VPS.
   - **Expected:** Workstation is not the hub.
   - **On failure:** Do not name timer unit filenames that identify the lab in public.

## Expected samples

```text
N failed
# N huge + Restart=always + missing ExecStart
```

## Verify

- No crash-loop user units.
- Always-on jobs not on the interactive workstation.
- ICMP / small ping success was **not** used as the pass criterion when this spec names TCP, SSH, or HTTPS.
- Bind table was filled by a human before any live `ip` / nft / iptables change.

## MUST NOT

- MUST NOT Restart=always a missing binary.
- MUST NOT publish timer unit names that identify the lab.
- MUST NOT apply live network or firewall changes until Bind is filled by a human.
- MUST NOT claim a fix on ICMP ping alone when Verify names TCP, SSH, or HTTPS.
- MUST NOT publish hostnames, addresses, ULAs, or custom ports.

## Related specs

- [OEN-S18](s18-do-not-set-exit-on-agent-workstation.md)
- [OEN-18](../networking/18-per-node-changelog-contract.md)

## Prior art (Not novel)

systemd Restart=always is documented. This note is missing ExecStart plus 150k restarts plus foreign binds on a 2-core box.

