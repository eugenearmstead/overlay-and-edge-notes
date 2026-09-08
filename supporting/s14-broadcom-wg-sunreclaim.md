---
id: "OEN-S14"
title: "Broadcom in-kernel WireGuard SUnreclaim (flow-cache/runner A/B fail)"
kind: "supporting"
status: "active"
edition: 2
date_published: "2026-09-08"
author: "Eugene Armstead"
author_url: "https://www.armsteadent.com/"
canonical: "https://eugenearmstead.github.io/overlay-and-edge-notes/supporting/s14-broadcom-wg-sunreclaim.html"
keywords:
  - "Broadcom in-kernel WireGuard SUnreclaim"
  - "skbuff SUnreclaim leak"
  - "drop_caches does not free SUnreclaim"
  - "flow-cache off runner off fail"
  - "ASUSWRT-Merlin WireGuard memory"
  - "6-8 MB/h SUnreclaim"
  - "in-kernel WG leak"
  - "scheduled reboot workaround"
  - "skip tables IPv4 IPv6 underlay"
  - "consumer router SUnreclaim"
  - "Merlin flow-cache A/B"
  - "WireGuard kernel slab leak"
backs:
  - OEN-12
backed_by:
  []
description: "In-kernel WireGuard on a Broadcom consumer router leaked about 6–8 MB/h of SUnreclaim. drop_caches did not free it. Flow-cache off and runner off A/Bs were negative."
terms:
  - abbr: API
    expansion: application programming interface
  - abbr: FC
    expansion: flow-cache (Broadcom hardware forwarding cache)
  - abbr: IPv4
    expansion: Internet Protocol version 4
  - abbr: IPv6
    expansion: Internet Protocol version 6
  - abbr: MB
    expansion: megabyte
  - abbr: OEN
    expansion: Overlay and Edge Notes
  - abbr: VPN
    expansion: Virtual Private Network
  - abbr: WG
    expansion: WireGuard
---

# Broadcom in-kernel WireGuard SUnreclaim (flow-cache/runner A/B fail)

## Context

Scheduled reboot is an ops workaround, not a root-cause fix. Skip tables that list IPv4 ports while the tunnel underlay is IPv6 do not help. Scrubbed measurements only.

## Topology

```text
Broadcom in-kernel WireGuard  -->  SUnreclaim / skbuff slope ~6-8 MB/h
drop_caches does not free it
flow-cache off / runner off A/B were negative
Scheduled reboot is ops workaround, not root cause
```

## Bind

Fill this table **before** any live change. Do **not** paste real values back into public notes.

| Placeholder | Operator fills | Class |
|-------------|----------------|-------|
| *(none)* | No packet-path Bind for this trap | Use the git host, origin, or API the operator already has |

## Formulas

Skip tables that list IPv4 ports while underlay is IPv6 do not help. Scrubbed measurements only.

## Method

Record the slope. Do not claim flow-cache or runner off as the fix after negative A/B. MUST NOT file a public firmware thread this round.

## Consequences

Operators plan reboot windows honestly. They stop toggling FC/runner as if it were proven.

## Agent stop rule

> MUST record scrubbed SUnreclaim slope only — no hostnames or iface names that identify a lab.
> MUST NOT claim flow-cache or runner A/B as the fix after a negative test.
> MUST NOT file a public firmware thread from this page.

## Procedure


### Copy-paste commands (after Bind)

```bash
# On the router after Bind:
grep -E 'SUnreclaim|MemFree' /proc/meminfo
```

1. **P1 — Measure SUnreclaim slope.**
   - **Action:** Sample /proc/meminfo SUnreclaim over hours while the in-kernel WG client is up.
   - **Expected:** ~6–8 MB/h class slope (order of magnitude).
   - **On failure:** If slope is zero, this spec does not apply.
2. **P2 — drop_caches does not free it.**
   - **Action:** `echo 3 > /proc/sys/vm/drop_caches` (know this is disruptive). SUnreclaim stays.
   - **Expected:** Not page cache.
   - **On failure:** Do not loop drop_caches.
3. **P3 — Negative A/B.**
   - **Action:** Flow-cache off and runner off did not stop the slope. IPv4 skip tables with IPv6 underlay did not help.
   - **Expected:** Do not keep those as “the fix.”
   - **On failure:** Reboot remains an ops workaround.

## Expected samples

```text
SUnreclaim:   climbing across hours
```

## Verify

- Slope documented without hostnames.
- FC/runner not claimed as fix.

## MUST NOT

- MUST NOT open a public firmware thread from this note.
- MUST NOT publish serials or full syslog.
- MUST NOT name the commercial VPN.
- MUST NOT publish hostnames, addresses, ULAs, or custom ports.

## Page changelog

- Edition 2 (8 Sep 2026, Mountain Time): Trap-specific Bind and agent stop rule (review cleanup).

## Related specs

- [OEN-12](../networking/12-consumer-wg-phantom-bridge.md)

## Prior art (Not novel)

skbuff leaks are discussed in firmware circles. This note is the measured slope plus failed A/Bs without a public thread.

