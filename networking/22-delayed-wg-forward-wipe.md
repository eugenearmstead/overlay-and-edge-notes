---
id: OEN-22
title: "Delayed WireGuard start wipes FORWARD with no restart event"
kind: original
status: active
edition: 1
date_published: 2026-09-08
author: Eugene Armstead
author_url: https://www.armsteadent.com/
canonical: https://eugenearmstead.github.io/overlay-and-edge-notes/networking/22-delayed-wg-forward-wipe.html
keywords:
  - wireguard
  - forward
  - boot
  - watchdog
backs: []
backed_by:
  - OEN-S33
description: "Boot applies LAN-to-WireGuard FORWARD early; firmware starts the client minutes later and rewrites FORWARD without a restart event. Tunnel is up, LAN is dead, counters stay 0."
terms:
  - abbr: OEN
    expansion: Overlay and Edge Notes
  - abbr: SSH
    expansion: Secure Shell
  - abbr: LAN
    expansion: Local Area Network
  - abbr: WAN
    expansion: Wide Area Network
  - abbr: VPN
    expansion: Virtual Private Network
  - abbr: TCP
    expansion: Transmission Control Protocol
  - abbr: MTU
    expansion: Maximum Transmission Unit
  - abbr: ICMP
    expansion: Internet Control Message Protocol
  - abbr: DF
    expansion: don't-fragment (IP flag)
  - abbr: HTTPS
    expansion: Hypertext Transfer Protocol Secure
  - abbr: IP
    expansion: Internet Protocol
  - abbr: IPv4
    expansion: Internet Protocol version 4
  - abbr: IPv6
    expansion: Internet Protocol version 6
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
  - abbr: ACCEPT
    expansion: iptables target that accepts a packet
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
| `<wg-iface>` | Consumer-router WireGuard client iface | Iface |
| `<lan-bridge>` | LAN bridge | Iface; MTU 1500 |
| `<wan-iface>` | WAN iface | Iface |
| `<lan-resolver>` | Intended LAN DNS | Address; never publish |


## Formulas

```text
# Measure <wg-mtu> from: ip link show <wg-iface>
mss4 = <wg-mtu> - 40    # IPv4 TCP (20-byte IP + 20-byte TCP)
mss6 = <wg-mtu> - 60    # IPv6 TCP (40-byte IPv6 + 20-byte TCP)
# IPv4 DF ping: IP size ≈ payload + 28
# IPv6 DF ping: IP size ≈ payload + 48
# Historical 1160 / 1146-byte SSH cliff = wrong-scope clamp, not this recipe.
# LAN bridge MTU MUST stay 1500.
```

See [OEN-01](../networking/01-overlay-ssh-byte-cliff.md) and [OEN-S01](../supporting/s01-pmtud-size-ladder.md).

## Decision

A delayed re-apply plus a periodic watchdog MUST restore LAN↔tunnel FORWARD. The watchdog MUST NOT restart WireGuard.

## Consequences

- LAN internet returns after the late client start.
- Operators stop bouncing the tunnel from cron.
- [OEN-S33](../supporting/s33-router-cron-path-set-e.md) PATH/`set -e` bugs do not silently skip the watchdog.

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

## Related specs

- [OEN-12 Phantom guest-bridge FORWARD](12-consumer-wg-phantom-bridge.md)
- [OEN-S33 Router cron PATH](../supporting/s33-router-cron-path-set-e.md)
- [OEN-16 Commercial WireGuard endpoint rotation](16-commercial-wg-endpoint-rotation.md)

## Prior art (Not novel)

Late-start VPN clients are known. This spec’s claim is FORWARD rewrite with **no** restart event minutes after boot.

