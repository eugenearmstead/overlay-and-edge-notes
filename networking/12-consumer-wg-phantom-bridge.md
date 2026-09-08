---
id: "OEN-12"
title: "Consumer-router WireGuard FORWARD only on a phantom bridge"
kind: "original"
status: "active"
edition: 2
date_published: "2026-09-08"
author: "Eugene Armstead"
author_url: "https://www.armsteadent.com/"
canonical: "https://eugenearmstead.github.io/overlay-and-edge-notes/networking/12-consumer-wg-phantom-bridge.html"
keywords:
  - "WireGuard FORWARD phantom bridge"
  - "Merlin connected without internet"
  - "router curl wg LAN dead"
  - "ASUSWRT-Merlin FORWARD guest bridge"
  - "restart_wgc wipes FORWARD"
  - "LAN bridge WireGuard MASQUERADE"
  - "iptables -C || -I firewall-start"
  - "consumer router WG no internet"
  - "delayed Starting client 2"
  - "guest bridge does not exist"
  - "WireGuard client FORWARD 0"
  - "Merlin VPN Director FORWARD"
backs:
  []
backed_by:
  - OEN-22
  - OEN-S20
  - OEN-S33
description: "Merlin-class firmware may allow FORWARD only for a guest bridge that does not exist, so the router can curl through WireGuard while LAN clients have no internet."
terms:
  - abbr: ACCEPT
    expansion: iptables target that accepts a packet
  - abbr: ESTABLISHED
    expansion: conntrack state for packets in an existing flow
  - abbr: FORWARD
    expansion: netfilter/iptables forward chain
  - abbr: HTTPS
    expansion: Hypertext Transfer Protocol Secure
  - abbr: ICMP
    expansion: Internet Control Message Protocol
  - abbr: IPv4
    expansion: Internet Protocol version 4
  - abbr: IPv6
    expansion: Internet Protocol version 6
  - abbr: LAN
    expansion: Local Area Network
  - abbr: MASQUERADE
    expansion: iptables masquerade (source NAT)
  - abbr: NAT
    expansion: network address translation
  - abbr: nft
    expansion: nftables (Linux packet filter)
  - abbr: OEN
    expansion: Overlay and Edge Notes
  - abbr: PATH
    expansion: Unix executable search path
  - abbr: PeerAPI
    expansion: overlay peer application-programming interface (exit DNS over HTTPS)
  - abbr: RELATED
    expansion: conntrack state for packets related to an existing flow
  - abbr: SSH
    expansion: Secure Shell
  - abbr: TCP
    expansion: Transmission Control Protocol
  - abbr: URL
    expansion: Uniform Resource Locator
  - abbr: VPN
    expansion: Virtual Private Network
  - abbr: VPS
    expansion: Virtual Private Server
  - abbr: WG
    expansion: WireGuard
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
| `<lan-bridge>` | LAN bridge | Router |
| `<wg-iface>` | Commercial WireGuard iface | Router or VPS client |

## Decision

firewall-start (or equivalent) MUST install idempotent `iptables -C || -I` rules for **LAN-bridge↔`<wg-iface>`** (v4 and v6) plus MASQUERADE. MUST NOT rely on the guest-bridge allow.

A watchdog MAY re-apply rules. It MUST NOT restart WireGuard ([OEN-22](22-delayed-wg-forward-wipe.md), [OEN-S33](../supporting/s33-router-cron-path-set-e.md)).

## Consequences

- LAN clients get internet through the tunnel.
- Router curl-on-iface staying green is no longer mistaken for LAN-up.
- Boot wipe is handled by the delayed re-apply spec, not by restarting the tunnel.

## Agent stop rule

> MUST emit bound FORWARD / iface checks for `<wg-iface>` after Bind is filled.
> MUST NOT apply iptables/nft until a human filled Bind.
> MUST NOT claim ICMP ping as the FORWARD fix.
> MUST NOT file a public firmware bug from this page.

## Procedure


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

## Page changelog

- Edition 2 (8 Sep 2026, Mountain Time): Trap-specific Bind and agent stop rule (review cleanup).

## Related specs

- [OEN-22 Delayed WireGuard FORWARD wipe](22-delayed-wg-forward-wipe.md)
- [OEN-16 Commercial WireGuard endpoint rotation](16-commercial-wg-endpoint-rotation.md)
- [OEN-S20 SSH TCP-open with no banner](../supporting/s20-ssh-open-no-banner.md)
- [OEN-S33 Router cron PATH](../supporting/s33-router-cron-path-set-e.md)
- [OEN-S14 Broadcom in-kernel WireGuard SUnreclaim](../supporting/s14-broadcom-wg-sunreclaim.md)

