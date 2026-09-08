---
id: OEN-S33
title: "Consumer-router cron PATH omits curl; watchdog log() + set -e exits"
kind: supporting
status: active
edition: 1
date_published: 2026-09-08
author: Eugene Armstead
author_url: https://www.armsteadent.com/
canonical: https://eugenearmstead.github.io/overlay-and-edge-notes/supporting/s33-router-cron-path-set-e.html
keywords:
  - cron
  - path
  - watchdog
backs:
  - OEN-12
  - OEN-16
  - OEN-22
backed_by: []
description: "Consumer-router cron PATH may omit /usr/sbin and curl. A log() that returns 1 with set -e exits the watchdog every tick — silent skip, stale status."
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
  - abbr: HTTPS
    expansion: Hypertext Transfer Protocol Secure
  - abbr: WG
    expansion: WireGuard
  - abbr: WireGuard
    expansion: UDP-based VPN protocol
  - abbr: DNS
    expansion: Domain Name System
  - abbr: nft
    expansion: nftables (Linux packet filter)
  - abbr: FORWARD
    expansion: netfilter/iptables forward chain
  - abbr: PATH
    expansion: Unix executable search path
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
| `<wg-iface>` | Consumer-router WireGuard client iface | Iface |
| `<lan-bridge>` | LAN bridge | Iface; MTU 1500 |
| `<wan-iface>` | WAN iface | Iface |
| `<lan-resolver>` | Intended LAN DNS | Address; never publish |


## Formulas

Set PATH at top of script. log() MUST return 0.

## Method

Set PATH in the cron/script. log() MUST return 0. MUST NOT restart WG from the watchdog.

## Consequences

Delayed FORWARD re-apply actually runs. Rotator hub watch ticks.

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
- ICMP / small ping success was **not** used as the pass criterion when this spec names TCP, SSH, or HTTPS.
- Bind table was filled by a human before any live `ip` / nft / iptables change.

## MUST NOT

- MUST NOT restart WireGuard from the watchdog.
- MUST NOT publish the script path as inventory.
- MUST NOT apply live network or firewall changes until Bind is filled by a human.
- MUST NOT claim a fix on ICMP ping alone when Verify names TCP, SSH, or HTTPS.
- MUST NOT publish hostnames, addresses, ULAs, or custom ports.

## Related specs

- [OEN-22](../networking/22-delayed-wg-forward-wipe.md)
- [OEN-16](../networking/16-commercial-wg-endpoint-rotation.md)

## Prior art (Not novel)

cron PATH is a classic. This note is firmware PATH plus log() returning 1 under set -e.

