---
id: OEN-14
title: "Exit app DNS is overlay peer-API, not coordinator Unbound"
kind: original
status: active
edition: 1
date_published: 2026-09-08
author: Eugene Armstead
author_url: https://www.armsteadent.com/
canonical: https://eugenearmstead.github.io/overlay-and-edge-notes/networking/14-exit-dns-is-peerapi.html
keywords:
  - exit-node
  - peerapi
  - dns
  - unbound
backs: []
backed_by:
  - OEN-S28
  - OEN-19
  - OEN-05
description: "dig against the coordinator nameserver can succeed while apps are DNS-dead. Exit-client DNS is HTTPS to the exit’s peer-API dns-query endpoint."
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
  - abbr: WireGuard
    expansion: UDP-based VPN protocol
  - abbr: DNS
    expansion: Domain Name System
  - abbr: DoH
    expansion: DNS over HTTPS
  - abbr: GCP
    expansion: Google Cloud Platform
  - abbr: VM
    expansion: virtual machine
  - abbr: NIC
    expansion: network interface card
  - abbr: API
    expansion: application programming interface
  - abbr: PeerAPI
    expansion: overlay peer application-programming interface (exit DNS over HTTPS)
  - abbr: RD
    expansion: Recursion Desired (DNS flag)
  - abbr: nft
    expansion: nftables (Linux packet filter)
  - abbr: URL
    expansion: Uniform Resource Locator
  - abbr: Pi
    expansion: single-board computer (Raspberry Pi class)
  - abbr: REFUSES
    expansion: DNS response code meaning the server will not answer
  - abbr: Unbound
    expansion: validating recursive DNS resolver
  - abbr: GET
    expansion: HTTP method
  - abbr: NOERROR
    expansion: DNS response code meaning the query succeeded
---

# Exit app DNS is overlay peer-API, not coordinator Unbound

## Context

`dig @<coordinator-ns>` works. `resolvectl` / `curl` on an exit-using client time out. WireGuard still shows `online`. Operators restart the coordinator.

Exit **app** Domain Name System (DNS) is Hypertext Transfer Protocol Secure (HTTPS) to `http://<exit>:<ephemeral>/dns-query` (overlay peer-API / PeerAPI). Empty `use_with_exit_node` means “use the exit’s local DNS”; it does **not** open or heal PeerAPI.

Changing coordinator DNS yaml forces a **fleet reconnect**. Sticky reconnect-during-outage is [OEN-S28](../supporting/s28-sticky-reconnect-during-peerapi-outage.md). Local Unbound Recursion Desired (RD)=0 refuse is [OEN-19](19-unbound-refuses-rd0.md).

## Topology

```text
[app on phone] --DoH--> PeerAPI on <exit-node>  (this is app DNS)
[operator] dig @<coordinator-ns>   MAY succeed while apps are DNS-dead
Empty use_with_exit_node ≠ opens PeerAPI
Changing coordinator DNS yaml  -->  fleet reconnect  (avoid)
```

## Bind

Fill this table **before** any live change. Do **not** paste real values back into public notes.

| Placeholder | Operator fills | Class |
|-------------|----------------|-------|
| `<exit-node>` | Overlay exit node | Cloud VM or LAN Pi used as exit |
| `<overlay-peer>` | Soak client (**not** the agent workstation) | LAN Pi |
| `<user>` | SSH user | Guest |
| `<overlay-tun>` | Overlay tun on the exit | Iface |
| `<gcp-nic>` | Public NIC on a Google Cloud guest | Iface; omit on non-GCP exits |
| `<wan-iface>` | WAN / public NIC | Iface |
| `<mss4>` / `<mss6>` | Computed from underlay or overlay tun MTU | Formulas |


## Formulas

Heal PeerAPI on the exit (restart the stub only). Do not restart coordination to “fix DNS.” Sticky clients: [OEN-S28](../supporting/s28-sticky-reconnect-during-peerapi-outage.md).

## Decision

Heal PeerAPI on the **exit** (restart the overlay DNS process / stub only). MUST NOT restart the coordinator to “fix DNS.” MUST NOT set exit-node on the agent workstation to reproduce ([OEN-S18](../supporting/s18-do-not-set-exit-on-agent-workstation.md)).

MUST NOT edit coordinator DNS yaml as a first DNS fix.

## Consequences

- Apps resolve again without a fleet bounce.
- Coordinator Unbound staying up is no longer mistaken for exit DNS.
- Phones that reconnected during the outage still need a client toggle ([OEN-S28](../supporting/s28-sticky-reconnect-during-peerapi-outage.md)).

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
# Coordinator view can be green:
dig +time=2 @<overlay-v4> example.com
# Exit-client view is PeerAPI DoH — prove from a non-exit peer:
curl -sS --max-time 8 -D- "http://<exit-overlay>:<peerapi-port>/dns-query" | head
```

MUST NOT set exit-node on the agent workstation ([OEN-S18](../supporting/s18-do-not-set-exit-on-agent-workstation.md)).

1. **P1 — Split coordinator dig vs app DNS.**
   - **Action:** `dig @<coordinator-ns> example.com` from a client. Then, with exit selected on `<overlay-peer>`, `curl --max-time 8 https://example.com` and a DoH GET to the exit PeerAPIURL dns-query.
   - **Expected:** Coordinator dig works; app/DoH fails — this spec applies.
   - **On failure:** If coordinator dig also fails, see [OEN-15](15-split-host-vs-overlay-resolver.md).
2. **P2 — Read PeerAPIURL; do not assume :53.**
   - **Action:** On `<exit-node>`, `tailscale status --json`. Note PeerAPIURL. Follow [OEN-05](05-exit-peerapi-dns-stub.md).
   - **Expected:** Ephemeral HTTPS DNS endpoint, not the coordinator.
   - **On failure:** If the URL is empty or connection refused, heal the exit daemon/stub.
3. **P3 — Heal the exit stub only.**
   - **Action:** Restart the exit DNS stub / overlay DNS process. Do not restart coordination `serve`. Do not rewrite coordinator DNS yaml.
   - **Expected:** DoH from a **non-exit** client returns NOERROR. curl through the exit works.
   - **On failure:** Phones that joined during the outage may stay stuck until toggled ([OEN-S28](../supporting/s28-sticky-reconnect-during-peerapi-outage.md)).
4. **P4 — Do not “fix” with accept-dns on the exit VM.**
   - **Action:** If this exit is a cloud VM, `accept-dns=true` pretty-prints and can break RD=0 ([OEN-23](23-cloud-exit-accept-dns.md)). Leave it off.
   - **Expected:** accept-dns remains false on the exit VM.
   - **On failure:** Guest `tailscale dns query` showing metadata is not PeerAPI.

## Expected samples

```text
# resolvectl / curl timeout on the phone; WireGuard still "online"
```

## Verify

- Coordinator dig still works; it was never the app path.
- PeerAPI DoH from a non-exit client succeeds.
- Exit-client curl resolves and fetches.
- Coordinator process was not restarted for this incident.
- ICMP / small ping success was **not** used as the pass criterion when this spec names TCP, SSH, or HTTPS.
- Bind table was filled by a human before any live `ip` / nft / iptables change.

## MUST NOT

- MUST NOT restart the coordinator to fix exit-client DNS.
- MUST NOT treat empty use_with_exit_node as opening PeerAPI.
- MUST NOT change coordinator DNS yaml as a first step (fleet reconnect).
- MUST NOT reproduce by setting exit-node on the agent workstation.
- MUST NOT apply live network or firewall changes until Bind is filled by a human.
- MUST NOT claim a fix on ICMP ping alone when Verify names TCP, SSH, or HTTPS.
- MUST NOT publish hostnames, addresses, ULAs, or custom ports.

## Related specs

- [OEN-05 Exit PeerAPI DNS stub](05-exit-peerapi-dns-stub.md)
- [OEN-19 Unbound REFUSES RD=0](19-unbound-refuses-rd0.md)
- [OEN-15 Split resolver views](15-split-host-vs-overlay-resolver.md)
- [OEN-23 Cloud-exit accept-dns](23-cloud-exit-accept-dns.md)
- [OEN-S28 Sticky reconnect during PeerAPI outage](../supporting/s28-sticky-reconnect-during-peerapi-outage.md)

## Prior art (Not novel)

Public docs say “local DNS for exit.” They rarely document PeerAPI DoH vs coordinator Unbound as two planes.

