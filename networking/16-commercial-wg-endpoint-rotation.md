---
id: "OEN-16"
title: "Commercial WireGuard endpoint rotation (IPv6, leftover bag, hub watch)"
kind: "original"
status: "active"
edition: 3
date_published: "2026-09-07"
author: "Eugene Armstead"
author_url: "https://www.armsteadent.com/"
canonical: "https://eugenearmstead.github.io/overlay-and-edge-notes/networking/16-commercial-wg-endpoint-rotation.html"
keywords:
  - "WireGuard leftover bag"
  - "leftover bag stay-put"
  - "wake tick vs hop interval"
  - "WireGuard endpoint rotation"
  - "IPv6-only WireGuard endpoint"
  - "PersistentKeepalive NAT"
  - "curl -6 WAN health check"
  - "WireGuard handshake stale"
  - "commercial WireGuard rotator"
  - "tunnel ULA egress verify"
  - "hub watch LAN Pi"
  - "Endpoint IPv6 port not FQDN"
  - "WireGuard hop cooldown"
  - "ISP down vs VPN down"
  - "skip sick leftover names"
  - "verified hop interval"
  - "allowlisted IPv6 endpoints"
  - "status JSON is not a hop"
backs:
  - OEN-S33
  - OEN-S35
  - OEN-22
backed_by:
  []
description: "IPv6-only WireGuard leftover-bag rotation fails when sick names are dropped and the bag refills healthy-only; stay-put, split wake vs hop."
terms:
  - abbr: OEN
    expansion: Overlay and Edge Notes
  - abbr: WG
    expansion: WireGuard
  - abbr: IPv6
    expansion: Internet Protocol version 6
  - abbr: IPv4
    expansion: Internet Protocol version 4
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
  - abbr: PATH
    expansion: Unix executable search path
  - abbr: CrowdSec
    expansion: open-source IDS/IPS with a Central API
---

# Commercial WireGuard endpoint rotation (IPv6, leftover bag, hub watch)

## Context

Public WireGuard rotators already exist: hop when the handshake goes stale, or hop on a schedule. What still gets operators stuck is a **commercial** tunnel whose published endpoint is **Internet Protocol version 6 (IPv6)-only**, whose “Virtual Private Network (VPN) is down” signal is confused with “Internet Service Provider (ISP) is down,” and whose leftover pool is emptied by deleting sick names so the next refill repeats a peer that just failed.

This note is the unpublished combo:

- `Endpoint` is `[IPv6]:port` only. Never a fully qualified domain name (FQDN) (Domain Name System (DNS) during a hop is another failure domain). Never Internet Protocol version 4 (IPv4) when the product’s working path is v6.
- Health of the **provider control plane** is probed with `curl -6` **bound to the Wide Area Network (WAN) interface**, not through `<wg-iface>`. Otherwise ISP death looks like VPN death, and you hop forever.
- After a hop, **egress verify** binds the **tunnel unique-local address (ULA)** (or the tunnel address the peer assigned) and MUST match **that endpoint’s site prefix**. A handshake without matching egress is a false UP. Only a prefix match is a **verified** hop.
- Eligible peers live in a **leftover bag**. One region is the **boot-default**. Consume leftover names until the bag is empty, then refill the allowlist minus the **current** name and global unicast address (GUA). Never hop to the same server (name + GUA).
- Peers that fail an IPv6 preflight or provider health check **stay in the leftover bag and are skipped**, not deleted. Recovered names become pickable on later wake ticks. If every leftover is still sick and the current endpoint is healthy: **stay put**. Do **not** refill from a healthy-only subset while leftovers remain.
- **Wake tick** (minutes) is not the **hop interval** (hours, measured from the last verified hop). Immediate hop when WAN or provider health fails, when the handshake is stale (a few minutes), or when the hop interval has elapsed.
- Cooldown after a hop or failed hop. Leftover draw **ignores cooldown on other peers** so a different leftover is not blocked. Cooldown MUST NOT be used as a reason to hop to the current name + GUA or to refill healthy-only.
- `PersistentKeepalive` MUST be non-zero so network address translation (NAT) mappings stay warm. Suggested example (upstream WireGuard NAT documentation): `25`. Second example (aggressive NAT / short mapping): `10`. Operators MAY pick any value in a 10–30 second textbook window. MUST NOT imply two different values on the cloud Virtual Private Server (VPS) versus the consumer router client.
- The **same leftover-bag idea** runs on a **consumer router VPN client** and on a **cloud VPS** client. An **always-on Local Area Network (LAN) Pi** watches freshness of both rotators and remediates if status goes stale. The watch MUST run on **one** `<lan-pi>`. It MUST NOT also run on the VPS or on the interactive workstation.
- A scheduled hop on a single VPS iface is a cold cut. Make-before-break spare-iface cutover is [OEN-S35](../supporting/s35-make-before-break-wg-cutover.md). Consumer-router cron PATH and `set -e` silent ticks are [OEN-S33](../supporting/s33-router-cron-path-set-e.md). Do not bounce the production iface on every successful hop ([OEN-22](22-delayed-wg-forward-wipe.md)).

Do not name the commercial provider. Do not name server nicknames. Public wording: allowlisted IPv6 endpoints, boot-default region, leftover bag, hub watch on an always-on Pi.

## Topology

```text
[<cloud-vps> WG client]  Endpoint = [IPv6]:port only
[<consumer router WG client>]  same leftover-bag contract
[<lan-pi> hub watch]  freshness of both rotators — NOT the VPS, NOT the workstation

Health: curl -6 --interface <wan-iface>     (ISP vs VPN split)
Egress: curl -6 --interface <tunnel-ula>    MUST match that endpoint's site prefix
```

## Bind

Fill this table **before** any live change. Do **not** paste real values back into public notes.

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

Wake tick and hop interval are different clocks. Handshake stale and cooldown are operator-tuned. This page has no path-size formula family.

- Wake tick: minutes, so a health or handshake hop is not delayed until the next scheduled hop. MUST NOT set the wake timer to the hop interval.
- Hop interval: hours, measured from the last **verified** hop.
- Handshake stale: a few minutes.
- Cooldown: tens of minutes after a hop or a failed hop. Leftover draw MUST ignore cooldown on **other** peers.
- `PersistentKeepalive` MUST be non-zero. Suggested example (upstream): `25`. Second example: `10`. Textbook window: 10–30 seconds.

Endpoint MUST be an IPv6 **literal**, never FQDN.

## Decision

A commercial WireGuard client that must stay up across endpoint failure MUST implement all of:

1. IPv6 literal endpoints from an allowlist.
2. WAN-bound v6 health, tunnel-bound egress verify, site-prefix match (verified hop).
3. Leftover bag: consume until empty, then refill allowlist minus current name + GUA; skip sick leftovers; stay put when the bag is all sick and current is healthy.
4. Split wake tick (minutes) from hop interval (hours from last verified hop). Immediate hop on WAN/provider health fail, stale handshake, or interval elapsed.
5. Leftover draw ignores cooldown on other peers. MUST NOT hop to current name + GUA.
6. Non-zero PersistentKeepalive (examples `25` and `10`; textbook 10–30 s). Same idea on VPS and router — do not publish two different values for those two clients.
7. One hub watch on `<lan-pi>`. MUST NOT also run on the VPS or the workstation. A status JavaScript Object Notation (JSON) refresh is not a hop.

Example timers operators MAY use: handshake stale after a few minutes; hop interval on the order of hours; cooldown of tens of minutes. Tune to the provider.

## Consequences

- Hops continue when the ISP is healthy even if a particular endpoint dies.
- ISP IPv6 loss does not burn the leftover bag.
- A peer that handshakes but egresses the wrong prefix is rejected and is not a verified hop.
- Sick names stay skippable; recovered names return without a healthy-only refill that repeats the last failure.
- Stay-put avoids flapping when the leftover pool is still sick and current is fine.
- The LAN Pi notices a silent rotator (no fresh status, including a silent tick exit) and can tick it. The VPS and the workstation are not watchdog hosts.
- A dashboard that only rereads JSON does not change the endpoint.

## Agent stop rule

> MUST emit bound `curl --interface` and `wg set` commands after Bind is filled.  
> MUST NOT hop, restart WireGuard, or apply `wg set` until a human filled Bind.  
> MUST NOT restart the WG interface from a watchdog on every tick ([OEN-22](22-delayed-wg-forward-wipe.md)).  
> MUST NOT treat a status JSON refresh as a hop.

## Procedure

Placeholders: `<cloud-vps>`, `<lan-pi>`, `<wg-iface>`, WAN interface on that host.

1. **P1 — Confirm Endpoint is an IPv6 literal.**
   - **Action:** Read the live WireGuard config on `<cloud-vps>` and on the consumer router client. Check `Endpoint`.
   - **Expected:** `[IPv6]:port` only. No hostname. No IPv4 literal if the working product path is v6.
   - **On failure:** Rewrite the peer to an allowlisted IPv6 GUA and restart the client once. Do not leave FQDN in production.

2. **P2 — Health-check the provider over WAN IPv6, not the tunnel.**
   - **Action:** `curl -6 --interface <wan-iface> --max-time 20 https://<isp-v6-canary>` (or any WAN-only v6 canary you control). Do **not** bind `<wg-iface>`. Provider health fail is an immediate hop trigger **only if** WAN IPv6 itself is up.

     ```bash
     curl -6 --interface <wan-iface> --max-time 20 -sS -o /dev/null -w '%{http_code}\n' https://<isp-v6-canary>
     curl -6 --interface <wg-iface> --max-time 20 -sS -o /dev/null -w '%{http_code}\n' https://<isp-v6-canary>
     ```
   - **Expected:** Success means the ISP v6 path is up. Failure means do not hop; fix WAN first.
   - **On failure:** Stop rotation. Investigate WAN IPv6. Hopping cannot repair an ISP outage.

3. **P3 — Leftover bag: consume, skip sick, stay put.**
   - **Action:** Draw from leftovers until the bag is empty, then refill **allowlist minus current name + GUA**. On each wake tick, skip leftovers that fail preflight or provider health; do **not** delete them. If a skipped name later reports healthy, it is pickable. If every leftover is still sick and current is healthy: stay put. Do **not** refill from a healthy-only subset while leftovers remain.
   - **Expected:** Bag still lists skipped sick names. Boot-default is identified. Current name + GUA is never the next draw.
   - **On failure:** If the bag is empty of pickable leftovers and current is healthy, stay put. If current is unhealthy, pick a recovered leftover; refill only when the bag is empty.

4. **P4 — Hop on health, stale handshake, or interval.**
   - **Action:** Immediate hop when (a) WAN is up and provider health is bad, (b) handshake age is stale (a few minutes), or (c) hop interval elapsed since the last **verified** hop. Draw the next leftover (skip current). Cooldown on the peer you left MUST NOT block drawing a **different** leftover. Set endpoint with `wg set` or the firmware equivalent **after Bind**. On a cloud VPS, prefer make-before-break when the hop is a scheduled interval hop ([OEN-S35](../supporting/s35-make-before-break-wg-cutover.md)); health and handshake hops MAY stay a cold `wg set`.
   - **Expected:** New endpoint is live. Old peer is not redrawn as current. A different leftover is eligible even if another peer is in cooldown.
   - **On failure:** Restore previous GUA. Do not loop `--force` without a bag. MUST NOT hop to current name + GUA.

5. **P5 — Verify egress on the tunnel address.**
   - **Action:** `curl -6 --interface <tunnel-ula> --max-time 15 https://<what-is-my-ip>` over HTTPS. Compare the returned IPv6 with the **site prefix** documented for that endpoint.

     ```bash
     curl -6 --interface <tunnel-ula> --max-time 15 -sS https://<what-is-my-ip>
     wg show <wg-iface>
     ```
   - **Expected:** Prefix matches the peer you just selected. Only then record a verified hop (start the hop-interval clock).
   - **On failure:** Treat as failed hop. Restore previous endpoint. Skip that leftover on later ticks; do not delete it from the bag.

6. **P6 — Set PersistentKeepalive.**
   - **Action:** Ensure the client peer has a non-zero `PersistentKeepalive`. Suggested example: `25` (WireGuard NAT documentation). Second example: `10` (aggressive NAT). Textbook window: 10–30 seconds. Use one value on a given client; do not document a VPS-versus-router split.
   - **Expected:** `wg show` reports a non-zero persistent keepalive (example: every 25 seconds).
   - **On failure:** Add a non-zero value and sync the interface. NAT mappings otherwise idle out and look like a dead endpoint.

7. **P7 — Hub watch on the LAN Pi only.**
   - **Action:** On `<lan-pi>`, poll rotator status freshness (age of the last successful rotate JSON or equivalent). If stale beyond your threshold (example: ten minutes), remotely tick the rotator on `<cloud-vps>` and on the consumer router. Do **not** install this watch on the VPS. Do **not** install it on the interactive workstation. A status dashboard or JSON refresh MUST NOT hop.
   - **Expected:** Stale rotators get one remediation tick. Logs show the Pi as the only watcher.
   - **On failure:** Check overlay SSH to those hosts (see [OEN-01](01-overlay-ssh-byte-cliff.md)) before blaming the rotator. A silent tick exit also looks like a stale rotator ([OEN-S33](../supporting/s33-router-cron-path-set-e.md)).

## Verify

- `Endpoint` remains `[IPv6]:port` after reboot (`--boot` path lands on the boot-default region, then leftover-bag draws).
- WAN-bound `curl -6` can fail independently of tunnel-bound `curl -6`.
- A hop is **verified** only when egress IPv6 prefix matches the selected endpoint. Small ping success is not that check.
- Sick leftovers remain in the bag (skipped), not deleted. Recovered names can be drawn later.
- Stay-put: all leftovers still sick and current healthy → no hop and no healthy-only refill.
- Watch runs on `<lan-pi>` only. The VPS and the workstation have no always-on rotate watch.
- Refreshing status JSON did not change `Endpoint`.

## MUST NOT

- MUST NOT publish commercial VPN **brand names** or **server nicknames**.
- MUST NOT put FQDN or IPv4 in `Endpoint` when the working path is IPv6-only.
- MUST NOT health-check through `<wg-iface>` and treat failure as “time to hop.”
- MUST NOT accept a handshake without site-prefix egress verify.
- MUST NOT delete sick leftover names; skip them. MUST NOT refill healthy-only while leftovers remain.
- MUST NOT hop to the current name + GUA.
- MUST NOT set the wake timer to the hop interval.
- MUST NOT run the hub watch on the VPS or on the agent workstation.
- MUST NOT treat a status dashboard or JSON refresh as a hop.
- MUST NOT restart the WireGuard interface from a watchdog on every tick (use `wg set` / firmware set when possible; a full restart can wipe FORWARD — [OEN-22](22-delayed-wg-forward-wipe.md)).

## Expected samples

```text
# WAN health independent of tunnel
200
# Endpoint after hop
endpoint: [2001:db8::1]:<port>   # documentation prefix only; operator uses allowlist
persistent keepalive: every 25 seconds
```

## Page changelog

- Edition 3 (10 Sep 2026, Mountain Time): Leftover bag, stay-put, wake tick versus hop interval, hub watch on one Pi.

## Related specs

- [OEN-01 Overlay SSH byte cliff](01-overlay-ssh-byte-cliff.md) — hub watch rides overlay SSH
- [OEN-21 Shared commercial-VPN NAT and CrowdSec](21-shared-vpn-nat-crowdsec-ban.md) — refresh trusted egress after a verified hop
- [OEN-22 Delayed WG FORWARD wipe](22-delayed-wg-forward-wipe.md)
- [OEN-S26 Wi-Fi vs cellular underlay](../supporting/s26-wifi-vs-cellular-underlay.md)
- [OEN-S33 Consumer-router cron PATH](../supporting/s33-router-cron-path-set-e.md) — silent tick exit also looks like a stale rotator
- [OEN-S35 Make-before-break commercial WireGuard cutover](../supporting/s35-make-before-break-wg-cutover.md)
