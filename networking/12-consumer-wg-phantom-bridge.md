---
id: OEN-12
title: "Consumer-router WireGuard FORWARD only on a phantom bridge"
kind: original
status: active
edition: 1
date_published: 2026-09-08
author: Eugene Armstead
author_url: https://www.armsteadent.com/
canonical: https://eugenearmstead.github.io/overlay-and-edge-notes/networking/12-consumer-wg-phantom-bridge.html
keywords:
  - wireguard
  - merlin
  - forward
  - bridge
backs: []
backed_by:
  - OEN-22
  - OEN-S20
  - OEN-S33
description: "Merlin-class firmware may allow FORWARD only for a guest bridge that does not exist, so the router can curl through WireGuard while LAN clients have no internet."
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
  - abbr: NAT
    expansion: network address translation
  - abbr: PeerAPI
    expansion: overlay peer application-programming interface (exit DNS over HTTPS)
  - abbr: nft
    expansion: nftables (Linux packet filter)
  - abbr: FORWARD
    expansion: netfilter/iptables forward chain
  - abbr: MASQUERADE
    expansion: iptables masquerade (source NAT)
  - abbr: URL
    expansion: Uniform Resource Locator
  - abbr: PATH
    expansion: Unix executable search path
  - abbr: ACCEPT
    expansion: iptables target that accepts a packet
  - abbr: ESTABLISHED
    expansion: conntrack state for packets in an existing flow
  - abbr: RELATED
    expansion: conntrack state for packets related to an existing flow
---

# Consumer-router WireGuard FORWARD only on a phantom bridge

## Context

The consumer router `curl --interface <wg-iface>` works. Local Area Network (LAN) clients show “connected without internet.” Operators blame client auth.

Firmware helpers often allow **guest-bridge↔tunnel** FORWARD. That guest bridge **does not exist**. LAN-bridge↔tunnel is missing. `restart_wgc` or a delayed “Starting client 2” after boot re-runs the helper and **wipes** persistent FORWARD/MASQUERADE. `service-event` does not fire on that boot path — that wipe is [OEN-22](22-delayed-wg-forward-wipe.md).

Public wording: consumer Merlin-class firmware, LAN bridge, WireGuard client iface. No model serials, no persistent-store paths in dumps.

## Topology

```text
[LAN client] --NAT--> [<lan-bridge>] --X--> <wg-iface>   FORWARD missing (TRAP)
[router] curl --interface <wg-iface>  WORKS
Firmware helper allowed a **phantom guest bridge** that does not exist.
Delayed WG start later wipes jffs FORWARD ([OEN-22](22-delayed-wg-forward-wipe.md)).
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

firewall-start (or equivalent) MUST install idempotent `iptables -C || -I` rules for **LAN-bridge↔`<wg-iface>`** (v4 and v6) plus MASQUERADE. MUST NOT rely on the guest-bridge allow.

A watchdog MAY re-apply rules. It MUST NOT restart WireGuard ([OEN-22](22-delayed-wg-forward-wipe.md), [OEN-S33](../supporting/s33-router-cron-path-set-e.md)).

## Consequences

- LAN clients get internet through the tunnel.
- Router curl-on-iface staying green is no longer mistaken for LAN-up.
- Boot wipe is handled by the delayed re-apply spec, not by restarting the tunnel.

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
iptables -S FORWARD | grep -E '<lan-bridge>|<wg-iface>' || true
ip6tables -S FORWARD | grep -E '<lan-bridge>|<wg-iface>' || true
curl --interface <wg-iface> -4 -sS -o /dev/null -w '%{http_code}\n' --max-time 8 https://example.com
curl --interface <wg-iface> -6 -sS -o /dev/null -w '%{http_code}\n' --max-time 8 https://example.com

# Idempotent LAN<->tunnel forward (IPv4 shown; repeat ip6tables)
iptables -C FORWARD -i <lan-bridge> -o <wg-iface> -j ACCEPT \
  || iptables -I FORWARD -i <lan-bridge> -o <wg-iface> -j ACCEPT
iptables -C FORWARD -i <wg-iface> -o <lan-bridge> -m state --state RELATED,ESTABLISHED -j ACCEPT \
  || iptables -I FORWARD -i <wg-iface> -o <lan-bridge> -m state --state RELATED,ESTABLISHED -j ACCEPT
```

MUST NOT `restart` the WireGuard client from a watchdog ([OEN-22](22-delayed-wg-forward-wipe.md)).

1. **P1 — Compare router-on-iface vs LAN client.**
   - **Action:** On the router: `curl --interface <wg-iface> --max-time 10 https://example.com`. On a LAN client: the same URL without a bind.
   - **Expected:** Router 200; LAN timeout or no route to internet.
   - **On failure:** If both fail, the tunnel itself is down ([OEN-16](16-commercial-wg-endpoint-rotation.md)).
2. **P2 — List FORWARD for the real LAN bridge.**
   - **Action:** `iptables -S FORWARD` / ip6tables. Look for LAN-bridge↔`<wg-iface>`. Note any allow that names a **guest** bridge that `ip link` does not show.
   - **Expected:** Guest-bridge allow present; that iface missing; LAN-bridge pair missing or counters 0.
   - **On failure:** Do not create the phantom guest bridge “to match the rule.”
3. **P3 — Idempotent LAN↔tunnel rules.**
   - **Action:** In firewall-start: `iptables -C ... || iptables -I ...` for LAN-bridge↔`<wg-iface>` FORWARD and MASQUERADE. Repeat for IPv6.
   - **Expected:** LAN client curl 200. Counters increment on the LAN-bridge rules.
   - **On failure:** If rules vanish minutes after boot, continue in [OEN-22](22-delayed-wg-forward-wipe.md).
4. **P4 — Overlay SSH banner check on the router.**
   - **Action:** If overlay SSH to the router is TCP-open with no banner, userspace is sick ([OEN-S20](../supporting/s20-ssh-open-no-banner.md)) — PeerAPI and FORWARD helpers can fail together.
   - **Expected:** Banner present, or a documented reboot restored both.
   - **On failure:** nmap `open` is not enough.

## Expected samples

```text
# Router curl via tunnel 200; LAN client no internet; FORWARD counters 0
200
```

## Verify

- LAN client HTTPS works; router-on-iface still works.
- FORWARD rules name the LAN bridge that exists.
- No dependence on a missing guest bridge.
- Watchdog does not restart WireGuard.
- ICMP / small ping success was **not** used as the pass criterion when this spec names TCP, SSH, or HTTPS.
- Bind table was filled by a human before any live `ip` / nft / iptables change.

## MUST NOT

- MUST NOT publish firmware serials or persistent-store script dumps.
- MUST NOT restart WireGuard from the watchdog.
- MUST NOT treat “connected without internet” as a Wi-Fi password failure first.
- MUST NOT name the commercial VPN provider.
- MUST NOT apply live network or firewall changes until Bind is filled by a human.
- MUST NOT claim a fix on ICMP ping alone when Verify names TCP, SSH, or HTTPS.
- MUST NOT publish hostnames, addresses, ULAs, or custom ports.

## Related specs

- [OEN-22 Delayed WireGuard FORWARD wipe](22-delayed-wg-forward-wipe.md)
- [OEN-16 Commercial WireGuard endpoint rotation](16-commercial-wg-endpoint-rotation.md)
- [OEN-S20 SSH TCP-open with no banner](../supporting/s20-ssh-open-no-banner.md)
- [OEN-S33 Router cron PATH](../supporting/s33-router-cron-path-set-e.md)
- [OEN-S14 Broadcom in-kernel WireGuard SUnreclaim](../supporting/s14-broadcom-wg-sunreclaim.md)

## Prior art (Not novel)

Missing FORWARD is a classic NAT router bug. This spec’s claim is phantom guest-bridge allow plus helper wipe as the Merlin-class pattern.

