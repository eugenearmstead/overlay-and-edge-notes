---
id: OEN-16
title: Commercial WireGuard endpoint rotation (IPv6, shuffle bag, hub watch)
kind: original
status: active
edition: 2
date_published: 2026-09-07
author: Eugene Armstead
author_url: https://www.armsteadent.com/
canonical: https://eugenearmstead.github.io/overlay-and-edge-notes/networking/16-commercial-wg-endpoint-rotation.html
keywords:
  - "WireGuard endpoint rotation"
  - "IPv6-only WireGuard endpoint"
  - "WireGuard shuffle bag"
  - "PersistentKeepalive 25"
  - "curl -6 WAN health check"
  - "WireGuard handshake stale"
  - "commercial WireGuard rotator"
  - "tunnel ULA egress verify"
  - "hub watch LAN Pi"
  - "Endpoint IPv6 port not FQDN"
  - "WireGuard hop cooldown"
  - "ISP down vs VPN down"
  - "allowlisted IPv6 endpoints"
backs: []
backed_by: []
description: "IPv6-only WireGuard rotation fails when health checks ride the tunnel: use WAN curl -6, ULA egress verify, a shuffle bag, and a hub watch."
terms:
  - abbr: OEN
    expansion: Overlay and Edge Notes
  - abbr: WG
    expansion: WireGuard
  - abbr: WireGuard
    expansion: UDP-based VPN protocol
  - abbr: IPv6
    expansion: Internet Protocol version 6
  - abbr: IPv4
    expansion: Internet Protocol version 4
  - abbr: IP
    expansion: Internet Protocol
  - abbr: FQDN
    expansion: fully qualified domain name
  - abbr: DNS
    expansion: Domain Name System
  - abbr: VPN
    expansion: Virtual Private Network
  - abbr: ISP
    expansion: Internet Service Provider
  - abbr: WAN
    expansion: Wide Area Network
  - abbr: ULA
    expansion: unique-local address (IPv6)
  - abbr: GUA
    expansion: global unicast address (IPv6)
  - abbr: NAT
    expansion: network address translation
  - abbr: JSON
    expansion: JavaScript Object Notation
  - abbr: SSH
    expansion: Secure Shell
  - abbr: HTTPS
    expansion: Hypertext Transfer Protocol Secure
  - abbr: HTTP
    expansion: Hypertext Transfer Protocol
  - abbr: UDP
    expansion: User Datagram Protocol
  - abbr: LAN
    expansion: Local Area Network
  - abbr: VPS
    expansion: Virtual Private Server
  - abbr: Pi
    expansion: single-board computer (Raspberry Pi class)
  - abbr: PersistentKeepalive
    expansion: WireGuard peer option that sends periodic keepalive packets
  - abbr: FORWARD
    expansion: netfilter/iptables forward chain
  - abbr: URL
    expansion: Uniform Resource Locator
  - abbr: PATH
    expansion: Unix executable search path
  - abbr: CrowdSec
    expansion: open-source IDS/IPS with a Central API
---

# Commercial WireGuard endpoint rotation (IPv6, shuffle bag, hub watch)

## Context

Public WireGuard rotators already exist: hop when the handshake goes stale, or hop on a schedule. What still gets operators stuck is a **commercial** tunnel whose published endpoint is **Internet Protocol version 6 (IPv6)-only**, whose “Virtual Private Network (VPN) is down” signal is confused with “Internet Service Provider (ISP) is down,” and whose hop lands on a peer that does not actually egress IPv6.

This note is the unpublished combo:

- `Endpoint` is `[IPv6]:port` only. Never a fully qualified domain name (FQDN) (Domain Name System (DNS) during a hop is another failure domain). Never Internet Protocol version 4 (IPv4) when the product’s working path is v6.
- Health of the **provider control plane** is probed with `curl -6` **bound to the Wide Area Network (WAN) interface**, not through `<wg-iface>`. Otherwise ISP death looks like VPN death, and you hop forever.
- After a hop, **egress verify** binds the **tunnel unique-local address (ULA)** (or the tunnel address the peer assigned) and MUST match **that endpoint’s site prefix**. A handshake without matching egress is a false UP.
- Eligible peers live in a **shuffle bag**. One region is the **boot-default**. Peers that fail an IPv6 preflight are **dropped** from the bag, not retried in a tight loop.
- Hop when handshake age exceeds a stale threshold, or when a hop interval elapses, then apply a **cooldown** so a bad peer is not redrawn immediately.
- `PersistentKeepalive = 25` on the client so network address translation (NAT) mappings stay warm.
- The **same idea** runs on a **consumer router VPN client** and on a **cloud Virtual Private Server (VPS)** client. An **always-on Local Area Network (LAN) Pi** watches freshness of both rotators and remediates if status goes stale. The watch MUST NOT run on the interactive workstation (mistaken deploy target).

Do not name the commercial provider. Do not name server nicknames. Public wording: allowlisted IPv6 endpoints, boot-default region, hub watch on an always-on Pi.

## Topology

```text
[<cloud-vps> WG client]  Endpoint = [IPv6]:port only
[<consumer router WG client>]  same contract
[<lan-pi> hub watch]  freshness of both rotators — NOT the workstation

Health: curl -6 --interface <wan-iface>     (ISP vs VPN split)
Egress: curl -6 --interface <tunnel-ula>    MUST match that endpoint's site prefix
```

## Bind

| Placeholder | Operator fills | Class |
|-------------|----------------|-------|
| `<cloud-vps>` | VPS running a commercial WG client | Cloud VPS |
| `<lan-pi>` | Always-on hub watch | LAN Pi |
| `<wg-iface>` | Tunnel iface | Router or VPS |
| `<wan-iface>` | WAN iface | Same host as the client |
| `<user>` | SSH user | Guest |
| `<endpoint-gua>` | Allowlisted peer IPv6 | GUA; never publish |
| `<tunnel-ula>` | Tunnel address used to bind egress verify | ULA class; never publish |

## Formulas

Handshake stale / hop interval / cooldown are operator-tuned. `PersistentKeepalive = 25` is the usual NAT keepalive. Endpoint MUST be an IPv6 **literal**, never FQDN.

## Decision

A commercial WireGuard client that must stay up across endpoint failure MUST implement all of:

1. IPv6 literal endpoints from an allowlist.
2. WAN-bound v6 health, tunnel-bound egress verify, site-prefix match.
3. Shuffle bag + boot-default + drop-on-preflight-fail + stale handshake + hop interval + cooldown.
4. Hub watch on `<lan-pi>`, not on the agent workstation.

Example timers operators MAY use: handshake stale after a few minutes; hop on the order of an hour; cooldown of tens of minutes. Tune to the provider. Keepalive 25 seconds is the usual WireGuard NAT value.

## Consequences

- Hops continue when the ISP is healthy even if a particular endpoint dies.
- ISP IPv6 loss does not burn the shuffle bag.
- A peer that handshakes but egresses the wrong prefix is rejected.
- The LAN Pi notices a silent rotator (no fresh status) and can tick it. The workstation is not a watchdog host.

## Agent stop rule

> MUST emit bound `curl --interface` and `wg set` commands.  
> MUST NOT hop or restart WireGuard until Bind is filled.  
> MUST NOT restart the WG interface from a watchdog on every tick ([OEN-22](22-delayed-wg-forward-wipe.md)).

## Procedure

Placeholders: `<cloud-vps>`, `<lan-pi>`, `<wg-iface>`, WAN interface on that host.

1. **P1 — Confirm Endpoint is an IPv6 literal.**
   - **Action:** Read the live WireGuard config on `<cloud-vps>` and on the consumer router client. Check `Endpoint`.
   - **Expected:** `[IPv6]:port` only. No hostname. No IPv4 literal if the working product path is v6.
   - **On failure:** Rewrite the peer to an allowlisted IPv6 global unicast address (GUA) and restart the client once. Do not leave FQDN in production.

2. **P2 — Health-check the provider over WAN IPv6, not the tunnel.**
   - **Action:** `curl -6 --interface <wan-iface> --max-time 20 https://<isp-v6-canary>` (or any WAN-only v6 canary you control). Do **not** bind `<wg-iface>`.

     ```bash
     curl -6 --interface <wan-iface> --max-time 20 -sS -o /dev/null -w '%{http_code}\n' https://<isp-v6-canary>
     curl -6 --interface <wg-iface> --max-time 20 -sS -o /dev/null -w '%{http_code}\n' https://<isp-v6-canary>
     ```
   - **Expected:** Success means the ISP v6 path is up. Failure means do not hop; fix WAN first.
   - **On failure:** Stop rotation. Investigate WAN IPv6. Hopping cannot repair an ISP outage.

3. **P3 — Build the eligible shuffle bag.**
   - **Action:** For each allowlisted endpoint, run a v6 preflight (WAN `curl -6` to that GUA or a documented health field). Drop peers that fail. Keep a boot-default region even if the bag is otherwise empty.
   - **Expected:** Bag contains only endpoints that passed preflight. Boot-default is identified.
   - **On failure:** If every peer fails preflight, leave the current endpoint; do not flap.

4. **P4 — Hop with cooldown.**
   - **Action:** If handshake age is past stale, or hop interval elapsed, draw the next name from the shuffled bag (skip current). Set endpoint with `wg set` or the firmware equivalent. Record cooldown on the peer you left.
   - **Expected:** New endpoint is live. Old peer is not redrawn until cooldown expires.
   - **On failure:** Restore previous GUA. Do not loop `--force` without a bag.

5. **P5 — Verify egress on the tunnel address.**
   - **Action:** `curl -6 --interface <tunnel-ula> --max-time 15 https://<what-is-my-ip>` over HTTPS. Compare the returned IPv6 with the **site prefix** documented for that endpoint.

     ```bash
     curl -6 --interface <tunnel-ula> --max-time 15 -sS https://<what-is-my-ip>
     wg show <wg-iface>
     ```
   - **Expected:** Prefix matches the peer you just selected.
   - **On failure:** Treat as failed hop. Restore previous endpoint. Drop or cooldown the bad peer.

6. **P6 — Set PersistentKeepalive.**
   - **Action:** Ensure the client peer has `PersistentKeepalive = 25`.
   - **Expected:** `wg show` reports persistent keepalive 25.
   - **On failure:** Add it and sync the interface. NAT mappings otherwise idle out and look like a dead endpoint.

7. **P7 — Hub watch on the LAN Pi only.**
   - **Action:** On `<lan-pi>`, poll rotator status freshness (age of the last successful rotate JSON or equivalent). If stale beyond your threshold (example: ten minutes), remotely tick the rotator on `<cloud-vps>` and on the consumer router. Do **not** install this watch on the interactive workstation.
   - **Expected:** Stale rotators get one remediation tick. Logs show Pi as the watcher.
   - **On failure:** Check overlay SSH to those hosts (see [OEN-01](01-overlay-ssh-byte-cliff.md)) before blaming the rotator.

## Verify

- `Endpoint` remains `[IPv6]:port` after reboot (`--boot` path lands on the boot-default region, then reshuffles).
- WAN-bound `curl -6` can fail independently of tunnel-bound `curl -6`.
- A forced hop returns an egress IPv6 whose prefix matches the selected endpoint.
- Failed preflight peers are absent from the next bag.
- Watch runs on `<lan-pi>`. The workstation has no always-on rotate timer.

## MUST NOT

- MUST NOT publish commercial VPN **brand names** or **server nicknames**.
- MUST NOT put FQDN or IPv4 in `Endpoint` when the working path is IPv6-only.
- MUST NOT health-check through `<wg-iface>` and treat failure as “time to hop.”
- MUST NOT accept a handshake without site-prefix egress verify.
- MUST NOT run the hub watch on the agent workstation.
- MUST NOT restart the WireGuard interface from a watchdog on every tick (use `wg set` / firmware set when possible; a full restart can wipe FORWARD — [OEN-22](22-delayed-wg-forward-wipe.md)).

## Expected samples

```text
# WAN health independent of tunnel
200
# Endpoint after hop
endpoint: [2001:db8::1]:<port>   # documentation prefix only; operator uses allowlist
persistent keepalive: every 25 seconds
```

## Related specs

- [OEN-01 Overlay SSH byte cliff](01-overlay-ssh-byte-cliff.md) — hub watch rides overlay SSH
- [OEN-21 Shared commercial-VPN NAT and CrowdSec](21-shared-vpn-nat-crowdsec-ban.md)
- [OEN-22 Delayed WG FORWARD wipe](22-delayed-wg-forward-wipe.md)
- [OEN-S26 Wi-Fi vs cellular underlay](../supporting/s26-wifi-vs-cellular-underlay.md)
- [OEN-S33 Consumer-router cron PATH](../supporting/s33-router-cron-path-set-e.md)

## Prior art (Not novel)

Handshake-age failover and scheduled hops are documented in generic WireGuard ops posts. This spec’s claim is IPv6-literal endpoints plus WAN-vs-tunnel health split plus site-prefix egress bind plus shuffle bag plus Pi hub watch as one contract.
