---
id: "OEN-S35"
title: "Make-before-break commercial WireGuard cutover on a cloud VPS"
kind: "supporting"
status: "active"
edition: 1
date_published: "2026-09-10"
author: "Eugene Armstead"
author_url: "https://www.armsteadent.com/"
canonical: "https://eugenearmstead.github.io/overlay-and-edge-notes/supporting/s35-make-before-break-wg-cutover.html"
keywords:
  - "make-before-break WireGuard"
  - "Table off spare iface"
  - "WireGuard dual default route"
  - "empty Peer section cutover"
  - "WireGuard dual-up leftover"
  - "orphan spare iface"
  - "skip warm session quota"
  - "cold wg set health hop"
  - "two consecutive tunnel probes"
  - "warm lead WireGuard"
  - "do not wg-quick every hop"
  - "cloud VPS WireGuard cutover"
backs:
  - OEN-16
backed_by:
  []
description: "A scheduled hop on one WireGuard iface is a cold cut; spare Table=off dual-up can leave two defaults or an empty [Peer] if cutover waits a full hop interval."
terms:
  - abbr: OEN
    expansion: Overlay and Edge Notes
  - abbr: WG
    expansion: WireGuard
  - abbr: VPS
    expansion: Virtual Private Server
  - abbr: ULA
    expansion: unique-local address (IPv6)
  - abbr: VPN
    expansion: Virtual Private Network
  - abbr: IPv6
    expansion: Internet Protocol version 6
  - abbr: WAN
    expansion: Wide Area Network
  - abbr: GUA
    expansion: global unicast address (IPv6)
  - abbr: LAN
    expansion: Local Area Network
  - abbr: HTTPS
    expansion: Hypertext Transfer Protocol Secure
  - abbr: JSON
    expansion: JavaScript Object Notation
  - abbr: PersistentKeepalive
    expansion: WireGuard peer option that sends periodic keepalive packets
  - abbr: FORWARD
    expansion: netfilter/iptables forward chain
---

# Make-before-break commercial WireGuard cutover on a cloud VPS

## Context

Method behind [OEN-16](../networking/16-commercial-wg-endpoint-rotation.md) for a **cloud Virtual Private Server (VPS)** Internet Protocol version 6 (IPv6) WireGuard (WG) client. A scheduled hop that only runs `wg set` on the production iface is a **cold cut**: handshake and egress drop until the new peer is up.

A **spare** iface with `Table = off` plus policy routing can come up during a **warm lead** (tens of minutes before the next scheduled hop), pass **two consecutive** tunnel probes, drain, then take over. Health and handshake hops from OEN-16 stay a **cold** `wg set` (procedure with placeholders; Bind-then-stop). Skip the warm path when the commercial provider’s **session quota** is nearly full. Do not publish the numeric quota. Do not treat the dual-up window as Virtual Private Network (VPN) down.

This spec does not apply to the consumer-router client in OEN-16. Hub watch stays on the always-on hub host in OEN-16.

## Topology

```text
[<cloud-vps> commercial WG]
  <wg-prod>   production tunnel (current endpoint)
  <wg-spare>  Table = off + policy routing — NOT a default in main
  <wan-iface> WAN for provider health (OEN-16 P2)

Warm lead: spare up, two consecutive tunnel probes, drain, then take over
MUST NOT: spare 0.0.0.0/0 in main; empty [Peer]; dual-up for a full hop interval
```

## Bind

Fill this table **before** any live change. Do **not** paste real values back into public notes.

| Placeholder | Operator fills | Class |
|-------------|----------------|-------|
| `<cloud-vps>` | Cloud VPS running the commercial WG client | Cloud VPS |
| `<wg-prod>` | Production tunnel iface | VPS |
| `<wg-spare>` | Spare tunnel iface (`Table = off`) | VPS |
| `<wan-iface>` | WAN iface on that VPS | Same host |
| `<tunnel-ula>` | Tunnel unique-local used to bind a probe | ULA class; never publish |

## Formulas

Qualitative only. No path-size family on this page.

- Warm lead: tens of minutes before the next **scheduled** hop from [OEN-16](../networking/16-commercial-wg-endpoint-rotation.md).
- Cutover: two consecutive tunnel probes, then a brief drain, then take over.
- Dual-up outside that lead: cut over or tear the spare. MUST NOT wait a full hop interval.

## Method

Bring the spare up with `Table = off` so it does not install `0.0.0.0/0` in **main**. Probe the spare twice. Drain. Promote. Persist a full `[Peer]` section. Health/handshake hops stay cold `wg set` when warm is skipped.

## Consequences

- Scheduled hops do not drop the production tunnel for the whole handshake.
- A keepalive-only dump cannot replace `[Peer]`.
- Dual-up is a short local window, not an all-evening second default.
- Operators do not treat “old iface still up while the spare is probing” as “VPN down.”

## Agent stop rule

> MUST emit a bound inspect-and-cutover runbook after Bind is filled.  
> MUST NOT run `wg-quick`, `ip rule`, `wg set`, or iface rename until a human filled Bind.  
> MUST NOT `wg-quick down` / `wg-quick up` the production iface on every successful hop if `wg set` is enough ([OEN-22](../networking/22-delayed-wg-forward-wipe.md)).  
> MUST NOT wait a full hop interval while both ifaces are up.

## Procedure

Placeholders: `<cloud-vps>`, `<wg-prod>`, `<wg-spare>`, `<wan-iface>`, `<tunnel-ula>`.

### Copy-paste commands (after Bind)

Inspect only until a human filled Bind and asked to apply:

```bash
wg show <wg-prod>
wg show <wg-spare>
```

1. **P1 — Spare is `Table = off`, not a second default.**
   - **Action:** Read the spare config on `<cloud-vps>`. Confirm `Table = off` and that **main** has no `0.0.0.0/0` via `<wg-spare>`. Policy routing for the spare MUST stay off the main default.
   - **Expected:** Production default unchanged. Spare has no default in main.
   - **On failure:** Do not bring the spare up. Dual default in main is this trap.

2. **P2 — Persist `[Peer]`; never a keepalive-only dump.**
   - **Action:** Before cutover, confirm the on-disk production config still has a `[Peer]` section with `Endpoint`, keys, and `PersistentKeepalive`. A cutover that writes `wg showconf` output with only PersistentKeepalive MUST NOT replace the file.
   - **Expected:** `[Peer]` present after cutover.
   - **On failure:** Restore the previous config. Do not hop again until `[Peer]` is whole.

3. **P3 — Warm lead: two consecutive probes, then drain.**
   - **Action:** During the warm lead (tens of minutes), bring `<wg-spare>` up to the **next** leftover endpoint from OEN-16 (never current name + global unicast address (GUA)). Probe the spare twice in a row (example: Hypertext Transfer Protocol Secure (HTTPS) via `<tunnel-ula>` on the spare, or equivalent tunnel bind). After two consecutive passes, drain briefly, then take over (rename or swap so `<wg-prod>` is the live iface).
   - **Expected:** Spare probes pass twice. Production takes over. Old iface down after drain.
   - **On failure:** Tear the spare. Do not leave dual-up. Do not wait for the next hop interval.

4. **P4 — Dual-up outside the warm lead.**
   - **Action:** If both ifaces are up outside the lead: cut over if two probes already passed; if production is already on the spare name, drain and down the old iface then finish rename; else tear the spare.
   - **Expected:** At most one production tunnel in main. Dual-up does not last until the next hop interval.
   - **On failure:** An all-evening dual-up was this skip. Cut over or tear now — do not wait.

5. **P5 — Orphan spare (production iface gone, rename never finished).**
   - **Action:** If `<wg-prod>` is gone and `<wg-spare>` is the live tunnel, finish the rename, persist `[Peer]`, and do **not** reset the verified-hop clock. Never hop to the same name + GUA.
   - **Expected:** One production iface name. Verified hop clock unchanged.
   - **On failure:** Do not treat the orphan as a failed hop that redraws current.

6. **P6 — “Old iface still up” is not “VPN down.”**
   - **Action:** While the spare is probing, `<wg-prod>` SHOULD still be up. Hub watch and status JSON from OEN-16 MUST NOT treat that window as a dead tunnel.
   - **Expected:** Production traffic still uses `<wg-prod>` until cutover.
   - **On failure:** A hop or restart during probe is the wrong fix.

7. **P7 — Skip warm near session quota; health hops stay cold.**
   - **Action:** If the commercial provider’s session quota is **nearly full**, skip the spare. Health and handshake hops stay a **cold** `wg set` as in OEN-16 P4 (placeholders; Bind-then-stop). MUST NOT publish the numeric quota.
   - **Expected:** Warm path only when quota has room. Immediate OEN-16 hops do not wait for a warm lead.
   - **On failure:** A second session that the provider rejects is this skip. Stay on cold `wg set`.

8. **P8 — Do not bounce production with `wg-quick` on a successful hop.**
   - **Action:** After a successful cold `wg set` or a finished cutover, MUST NOT `wg-quick down` / `wg-quick up` `<wg-prod>` if `wg set` (or the cutover rename) already applied the peer. A full restart can wipe FORWARD ([OEN-22](../networking/22-delayed-wg-forward-wipe.md)).
   - **Expected:** Tunnel stays up. FORWARD counters still increment.
   - **On failure:** Delayed Local Area Network (LAN) death after a “successful” hop is OEN-22, not a reason to hop again.

## Expected samples

```text
# inspect after Bind
interface: <wg-prod>
# spare config (human-read)
Table = off
# after cutover
[Peer]
Endpoint = [2001:db8::1]:<port>
PersistentKeepalive = 25
```

## Verify

- Spare never installed `0.0.0.0/0` in main.
- On-disk config still has `[Peer]` after cutover (not PersistentKeepalive alone).
- Dual-up did not last a full hop interval.
- Orphan spare was renamed; verified-hop clock was not reset.
- “Old iface up while spare probing” was not treated as VPN down.
- Production iface was not `wg-quick` bounced on a successful hop.
- HTTPS (or equivalent) tunnel probes on the spare — not a small ping — were the cutover gate.

## MUST NOT

- MUST NOT put the spare in the main table with `0.0.0.0/0`.
- MUST NOT overwrite config so `[Peer]` is missing.
- MUST NOT leave dual-up until the next hop interval.
- MUST NOT treat “old iface still up while the spare is probing” as “VPN down.”
- MUST NOT publish the provider session-quota count.
- MUST NOT `wg-quick down` / `wg-quick up` the production iface on every successful hop if `wg set` is enough.
- MUST NOT apply `ip rule`, `wg set`, or `wg-quick` from unbound placeholders.
- MUST NOT publish commercial VPN brand names, server nicknames, addresses, ULAs, or custom ports.

## Page changelog

- Edition 1 (10 Sep 2026, Mountain Time): Make-before-break spare iface on a cloud VPS.

## Related specs

- [OEN-16 Commercial WireGuard endpoint rotation](../networking/16-commercial-wg-endpoint-rotation.md)
- [OEN-22 Delayed WG FORWARD wipe](../networking/22-delayed-wg-forward-wipe.md)

## Prior art (Not novel)

[WireGuard routing](https://www.wireguard.com/) documents `Table = off` and AllowedIPs. This note is the commercial-hop failure modes: double default, empty `[Peer]`, dual-up that waited a hop interval, and skipping warm when session quota is nearly full.
