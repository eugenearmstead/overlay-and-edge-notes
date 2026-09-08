---
id: "OEN-22"
title: "Delayed WireGuard start wipes FORWARD with no restart event"
kind: "original"
status: "active"
edition: 2
date_published: "2026-09-08"
author: "Eugene Armstead"
author_url: "https://www.armsteadent.com/"
canonical: "https://eugenearmstead.github.io/overlay-and-edge-notes/networking/22-delayed-wg-forward-wipe.html"
keywords:
  - "delayed WireGuard FORWARD wipe"
  - "no restart_wgc event boot"
  - "tunnel UP LAN dead counters 0"
  - "firmware starts WG minutes later"
  - "service-event never fires"
  - "ASUSWRT-Merlin delayed client"
  - "watchdog re-apply FORWARD"
  - "do not restart WG from watchdog"
  - "boot FORWARD then wipe"
  - "router curl wg LAN no internet"
  - "periodic FORWARD restore"
  - "Merlin Starting client delayed"
backs:
  []
backed_by:
  - OEN-S33
description: "Boot applies LAN-to-WireGuard FORWARD early; firmware starts the client minutes later and rewrites FORWARD without a restart event. Tunnel is up, LAN is dead, counters stay 0."
terms:
  - abbr: ACCEPT
    expansion: iptables target that accepts a packet
  - abbr: FORWARD
    expansion: netfilter/iptables forward chain
  - abbr: HTTPS
    expansion: Hypertext Transfer Protocol Secure
  - abbr: ICMP
    expansion: Internet Control Message Protocol
  - abbr: LAN
    expansion: Local Area Network
  - abbr: nft
    expansion: nftables (Linux packet filter)
  - abbr: OEN
    expansion: Overlay and Edge Notes
  - abbr: PATH
    expansion: Unix executable search path
  - abbr: SSH
    expansion: Secure Shell
  - abbr: TCP
    expansion: Transmission Control Protocol
  - abbr: VPN
    expansion: Virtual Private Network
  - abbr: VPS
    expansion: Virtual Private Server
  - abbr: WG
    expansion: WireGuard
---

# Delayed WireGuard start wipes FORWARD with no restart event

## Context

Distinct from [OEN-12](12-consumer-wg-phantom-bridge.md) (phantom guest-bridge allow). Boot applies Local Area Network (LAN)↔WireGuard rules early. Firmware starts the WireGuard client **minutes later** and rewrites FORWARD. `service-event` never fires (no `restart wgc`). Tunnel is UP. Router `curl --interface <wg-iface>` is OK. LAN is dead. Counters 0.

## Topology

```text
boot: firewall-start adds LAN<->WG FORWARD
minutes later: firmware starts WG client, rewrites FORWARD, no restart event
Tunnel UP, router curl --interface <wg-iface> OK, LAN dead, counters 0
Watchdog: delayed re-apply. MUST NOT restart WG.
```

## Bind

Fill this table **before** any live change. Do **not** paste real values back into public notes.

| Placeholder | Operator fills | Class |
|-------------|----------------|-------|
| `<lan-bridge>` | LAN bridge | Router |
| `<wg-iface>` | Commercial WireGuard iface | Router or VPS client |

## Decision

A delayed re-apply plus a periodic watchdog MUST restore LAN↔tunnel FORWARD. The watchdog MUST NOT restart WireGuard.

## Consequences

- LAN internet returns after the late client start.
- Operators stop bouncing the tunnel from cron.
- [OEN-S33](../supporting/s33-router-cron-path-set-e.md) PATH/`set -e` bugs do not silently skip the watchdog.

## Agent stop rule

> MUST emit bound FORWARD listing before/after delayed WireGuard start after Bind is filled.
> MUST NOT apply iptables/nft until a human filled Bind.
> MUST NOT restart the tunnel from a watchdog on every tick.
> MUST NOT file a public firmware bug from this page.

## Procedure


### Copy-paste commands (after Bind)

```bash
# After Bind, idempotent re-apply (same as OEN-12 ACCEPT pair). Cron PATH: [OEN-S33](../supporting/s33-router-cron-path-set-e.md)
iptables -C FORWARD -i <lan-bridge> -o <wg-iface> -j ACCEPT || iptables -I FORWARD -i <lan-bridge> -o <wg-iface> -j ACCEPT
ip6tables -C FORWARD -i <lan-bridge> -o <wg-iface> -j ACCEPT || ip6tables -I FORWARD -i <lan-bridge> -o <wg-iface> -j ACCEPT
```

1. **P1 — Time the wipe.**
   - **Action:** At boot, note when LAN↔WG FORWARD exists, when the client reports UP, and when FORWARD counters reset to 0 for the LAN-bridge rules.
   - **Expected:** Rules exist early; disappear after “Starting client” without a restart event.
   - **On failure:** If rules never exist, this is [OEN-12](12-consumer-wg-phantom-bridge.md) only.
2. **P2 — Delayed re-apply.**
   - **Action:** Sleep until the client iface is present, then run the same idempotent `iptables -C || -I` as [OEN-12](12-consumer-wg-phantom-bridge.md).
   - **Expected:** LAN client curl 200 after the late start.
   - **On failure:** Do not `restart wgc` from this path.
3. **P3 — Periodic watchdog, no restart.**
   - **Action:** Cron or equivalent re-applies rules if missing. MUST NOT restart WireGuard. Watch PATH and `set -e` ([OEN-S33](../supporting/s33-router-cron-path-set-e.md)).
   - **Expected:** Logs show re-apply ticks, not tunnel restarts. LAN stays up.
   - **On failure:** If the watchdog exits every tick, fix log() returning 1.
4. **P4 — Confirm no service-event.**
   - **Action:** Grep firmware logs: late client start without `restart wgc` / service-event.
   - **Expected:** Wipe happened with no event — this spec, not a missed hook.
   - **On failure:** Do not invent an event handler that never runs.

## Expected samples

```text
# No 'restart wgc' in logs; FORWARD empty after delayed Starting client
```

## Verify

- After a reboot, wait for late client start; LAN HTTPS works without a manual restart.
- Watchdog does not restart WireGuard.
- FORWARD LAN-bridge counters increment.
- cron PATH includes the iptables binary.
- ICMP / small ping success was **not** used as the pass criterion when this spec names TCP, SSH, or HTTPS.
- Bind table was filled by a human before any live `ip` / nft / iptables change.

## MUST NOT

- MUST NOT restart WireGuard from the watchdog.
- MUST NOT publish firmware log dumps that identify the lab.
- MUST NOT conflate this with the phantom guest-bridge allow.
- MUST NOT name the commercial VPN provider.
- MUST NOT apply live network or firewall changes until Bind is filled by a human.
- MUST NOT claim a fix on ICMP ping alone when Verify names TCP, SSH, or HTTPS.
- MUST NOT publish hostnames, addresses, ULAs, or custom ports.

## Page changelog

- Edition 2 (8 Sep 2026, Mountain Time): Trap-specific Bind and agent stop rule (review cleanup).

## Related specs

- [OEN-12 Phantom guest-bridge FORWARD](12-consumer-wg-phantom-bridge.md)
- [OEN-S33 Router cron PATH](../supporting/s33-router-cron-path-set-e.md)
- [OEN-16 Commercial WireGuard endpoint rotation](16-commercial-wg-endpoint-rotation.md)

## Prior art (Not novel)

Late-start VPN clients are known. This spec’s claim is FORWARD rewrite with **no** restart event minutes after boot.

