---
id: "OEN-S19"
title: "Push small overlay snapshots; do not copy-pull large JSON"
kind: "supporting"
status: "active"
edition: 2
date_published: "2026-09-08"
author: "Eugene Armstead"
author_url: "https://www.armsteadent.com/"
canonical: "https://eugenearmstead.github.io/overlay-and-edge-notes/supporting/s19-push-small-overlay-snapshots.html"
keywords:
  - "push small overlay snapshots"
  - "do not SCP-pull large JSON"
  - "overlay SSH byte cliff JSON"
  - "fleet snapshot chunks"
  - "Tailscale SSH large JSON hang"
  - "push to hub not pull"
  - "ControlPath=none large scp"
  - "NDJSON small chunks"
  - "health snapshot overlay"
  - "SCP hang 1KB cliff"
  - "Headscale JSON over SSH"
  - "push not pull overlay"
backs:
  - OEN-01
backed_by:
  []
description: "Fleet snapshots: push small chunks to the hub. Do not SCP-pull large JSON over overlay SSH or you hit the byte cliff."
terms:
  - abbr: ControlPath
    expansion: OpenSSH multiplexing socket path option
  - abbr: JSON
    expansion: JavaScript Object Notation
  - abbr: KB
    expansion: kilobyte
  - abbr: LAN
    expansion: Local Area Network
  - abbr: OEN
    expansion: Overlay and Edge Notes
  - abbr: Pi
    expansion: single-board computer (Raspberry Pi class)
  - abbr: SCP
    expansion: secure copy
  - abbr: SSH
    expansion: Secure Shell
---

# Push small overlay snapshots; do not copy-pull large JSON

## Context

Backs [OEN-S03](s03-transfer-matrix-controlpath.md) / [OEN-01](../networking/01-overlay-ssh-byte-cliff.md). Large JSON over userspace overlay SSH hangs.

## Topology

```text
[spokes] push small snapshots --> hub
MUST NOT SCP-pull large JSON over overlay SSH  ([OEN-01](../networking/01-overlay-ssh-byte-cliff.md))
```

## Bind

Fill this table **before** any live change. Do **not** paste real values back into public notes.

| Placeholder | Operator fills | Class |
|-------------|----------------|-------|
| `<user>` | SSH user | Guest account |
| `<lan-pi>` | Always-on LAN Pi | LAN Pi |
| `<small-snapshot>` | Small overlay status snapshot path | File the procedure prints |

## Method

Nodes PUSH small files to `<lan-pi>`. MUST NOT pull multi-megabyte JSON over overlay SSH as the daily collector.

## Consequences

Collectors finish. SSH sessions do not freeze at the cliff.

## Agent stop rule

> MUST emit bound small-snapshot push commands after Bind is filled.
> MUST NOT copy-pull multi-megabyte JSON over overlay SSH when [OEN-01](../networking/01-overlay-ssh-byte-cliff.md) still cliffs.
> MUST NOT apply netfilter from this page.

## Procedure


### Copy-paste commands (after Bind)

```bash
ssh -o ControlPath=none <user>@<lan-pi> 'wc -c <small-snapshot>'
# If a pull of megabyte JSON hangs, this spec + OEN-01 / OEN-S03
```

1. **P1 — Size the payload.**
   - **Action:** If the JSON is hundreds of KB+, it is in the cliff zone on a bad path.
   - **Expected:** Switch to push-small or kernel SSH after path fix.
   - **On failure:** Do not raise timeout as the fix.
2. **P2 — Push to the hub.**
   - **Action:** Each node writes a small chunk and pushes to the always-on Pi.
   - **Expected:** Hub concatenates. No large pull.
   - **On failure:** Workstation is not the hub ([OEN-S13](s13-restart-always-missing-unit.md)).
3. **P3 — ControlPath=none when auditing.**
   - **Action:** Same as OEN-S03.
   - **Expected:** Mux not blamed.
   - **On failure:** Fix path still required for interactive large SSH.

## Expected samples

```text
# small chunk finishes; large JSON pull hangs at ~1 KB
```

## Verify

- Collector uses push-small.
- No SCP-pull of huge JSON over overlay SSH.

## MUST NOT

- MUST NOT SCP-pull large JSON over overlay SSH as the design.
- MUST NOT use the workstation as the hub.
- MUST NOT publish hostnames, addresses, ULAs, or custom ports.

## Page changelog

- Edition 2 (8 Sep 2026, Mountain Time): Trap-specific Bind and agent stop rule (review cleanup).

## Related specs

- [OEN-01](../networking/01-overlay-ssh-byte-cliff.md)
- [OEN-S03](s03-transfer-matrix-controlpath.md)

