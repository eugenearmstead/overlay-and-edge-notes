---
id: "OEN-S13"
title: "Restart=always on a missing unit hung the workstation"
kind: "supporting"
status: "active"
edition: 2
date_published: "2026-09-08"
author: "Eugene Armstead"
author_url: "https://www.armsteadent.com/"
canonical: "https://eugenearmstead.github.io/overlay-and-edge-notes/supporting/s13-restart-always-missing-unit.html"
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
backs:
  []
backed_by:
  []
description: "Restart=always on a missing ExecStart produced 150k+ failed restarts plus leftover units binding another host’s addresses on a 2-core box."
terms:
  - abbr: API
    expansion: application programming interface
  - abbr: OEN
    expansion: Overlay and Edge Notes
  - abbr: Pi
    expansion: single-board computer (Raspberry Pi class)
  - abbr: systemd
    expansion: Linux service manager
  - abbr: VPS
    expansion: Virtual Private Server
---

# Restart=always on a missing unit hung the workstation

## Context

Always-on jobs belong on an always-on host. A user systemd unit with Restart=always and a vanished ExecStart can peg a workstation. Leftover units may bind another host’s addresses.

## Topology

N/A — deploy

## Bind

Fill this table **before** any live change. Do **not** paste real values back into public notes.

| Placeholder | Operator fills | Class |
|-------------|----------------|-------|
| *(none)* | No packet-path Bind for this trap | Use the git host, origin, or API the operator already has |

## Formulas

Always-on jobs belong on an always-on host, not the agent workstation.

## Method

Audit `systemctl --user` for crash-loop units. MUST NOT use Restart=always on a unit whose binary may be missing. Always-on work belongs on `<lan-pi>` or `<cloud-vps>`.

## Consequences

Workstation load returns to normal. Foreign binds go away.

## Agent stop rule

> MUST emit the `systemctl --user` crash-loop audit after Bind is filled.
> MUST NOT set `Restart=always` on a unit whose binary may be missing.
> MUST NOT apply netfilter from this page.

## Procedure


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

## MUST NOT

- MUST NOT Restart=always a missing binary.
- MUST NOT publish timer unit names that identify the lab.
- MUST NOT publish hostnames, addresses, ULAs, or custom ports.

## Page changelog

- Edition 2 (8 Sep 2026, Mountain Time): Trap-specific Bind and agent stop rule (review cleanup).

## Related specs

- [OEN-S18](s18-do-not-set-exit-on-agent-workstation.md)
- [OEN-18](../networking/18-per-node-changelog-contract.md)

## Prior art (Not novel)

systemd Restart=always is documented. This note is missing ExecStart plus 150k restarts plus foreign binds on a 2-core box.

