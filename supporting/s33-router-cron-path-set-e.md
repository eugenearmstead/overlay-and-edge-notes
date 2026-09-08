---
id: "OEN-S33"
title: "Consumer-router cron PATH omits curl; watchdog log() + set -e exits"
kind: "supporting"
status: "active"
edition: 2
date_published: "2026-09-08"
author: "Eugene Armstead"
author_url: "https://www.armsteadent.com/"
canonical: "https://eugenearmstead.github.io/overlay-and-edge-notes/supporting/s33-router-cron-path-set-e.html"
keywords:
  - "router cron PATH omits curl"
  - "watchdog log() set -e exits"
  - "cron PATH /usr/sbin missing"
  - "silent skip stale status"
  - "ASUSWRT-Merlin cron PATH"
  - "log function return 1"
  - "set -e watchdog every tick"
  - "consumer router cron curl"
  - "WireGuard watchdog skipped"
  - "PATH omits /usr/sbin"
  - "Merlin cru PATH"
  - "watchdog never runs"
backs:
  - OEN-12
  - OEN-16
  - OEN-22
backed_by:
  []
description: "Consumer-router cron PATH may omit /usr/sbin and curl. A log() that returns 1 with set -e exits the watchdog every tick — silent skip, stale status."
terms:
  - abbr: API
    expansion: application programming interface
  - abbr: FORWARD
    expansion: netfilter/iptables forward chain
  - abbr: OEN
    expansion: Overlay and Edge Notes
  - abbr: PATH
    expansion: Unix executable search path
  - abbr: WG
    expansion: WireGuard
---

# Consumer-router cron PATH omits curl; watchdog log() + set -e exits

## Context

Watchdogs for FORWARD re-apply and WG rotation silently never run.

## Topology

```text
consumer-router cron PATH omits /usr/sbin and curl
log() returns 1 + set -e  -->  watchdog exits every tick
MUST NOT restart WG from the watchdog
```

## Bind

Fill this table **before** any live change. Do **not** paste real values back into public notes.

| Placeholder | Operator fills | Class |
|-------------|----------------|-------|
| *(none)* | No packet-path Bind for this trap | Use the git host, origin, or API the operator already has |

## Formulas

Set PATH at top of script. log() MUST return 0.

## Method

Set PATH in the cron/script. log() MUST return 0. MUST NOT restart WG from the watchdog.

## Consequences

Delayed FORWARD re-apply actually runs. Rotator hub watch ticks.

## Agent stop rule

> MUST emit bound cron PATH / `set -e` / log() checks after Bind is filled.
> MUST NOT restart WireGuard from the watchdog on every tick.
> MUST NOT apply netfilter from this page.

## Procedure


### Copy-paste commands (after Bind)

```bash
# After Bind, on the router:
echo "$PATH"
which iptables curl wg
```

1. **P1 — PATH.**
   - **Action:** Cron PATH on this firmware may omit `/usr/sbin`. `which iptables curl wg`. Set PATH at the top of the script.
   - **Expected:** iptables found.
   - **On failure:** Silent “command not found” was the skip.
2. **P2 — log() and set -e.**
   - **Action:** If `log` returns 1, `set -e` exits every tick.
   - **Expected:** log returns 0. Watchdog completes.
   - **On failure:** Do not remove set -e; fix log.
3. **P3 — No WG restart.**
   - **Action:** Re-apply rules / `wg set` only ([OEN-22](../networking/22-delayed-wg-forward-wipe.md)).
   - **Expected:** Tunnel not bounced every tick.
   - **On failure:** Restart wipes FORWARD.

## Expected samples

```text
# silent skip: iptables: not found
```

## Verify

- Watchdog log shows completed ticks.
- PATH includes iptables.
- No WG restart.

## MUST NOT

- MUST NOT restart WireGuard from the watchdog.
- MUST NOT publish the script path as inventory.
- MUST NOT publish hostnames, addresses, ULAs, or custom ports.

## Page changelog

- Edition 2 (8 Sep 2026, Mountain Time): Trap-specific Bind and agent stop rule (review cleanup).

## Related specs

- [OEN-22](../networking/22-delayed-wg-forward-wipe.md)
- [OEN-16](../networking/16-commercial-wg-endpoint-rotation.md)

## Prior art (Not novel)

cron PATH is a classic. This note is firmware PATH plus log() returning 1 under set -e.

