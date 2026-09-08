---
id: "OEN-S26"
title: "Wi-Fi underlay vs cellular underlay to the same cloud exit"
kind: "supporting"
status: "active"
edition: 2
date_published: "2026-09-08"
author: "Eugene Armstead"
author_url: "https://www.armsteadent.com/"
canonical: "https://eugenearmstead.github.io/overlay-and-edge-notes/supporting/s26-wifi-vs-cellular-underlay.html"
keywords:
  - "Wi-Fi vs cellular underlay"
  - "same cloud exit two underlays"
  - "home Wi-Fi encapsulates overlay"
  - "cellular direct to cloud"
  - "IPv4 cloud IPv6 home leak"
  - "not the GCP exit is broken"
  - "underlay WireGuard vs cellular"
  - "split v4/v6 underlay"
  - "Tailscale exit Wi-Fi cellular"
  - "Happy-Eyeballs vs underlay"
  - "phone Wi-Fi tunnel encapsulate"
  - "cellular overlay path"
backs:
  - OEN-13
  - OEN-16
  - OEN-17
backed_by:
  []
description: "Home Wi-Fi may encapsulate overlay inside commercial WireGuard; cellular may go direct. IPv4 can show the cloud while IPv6 leaks the home tunnel. Not “the GCP exit is broken.”"
terms:
  - abbr: GCP
    expansion: Google Cloud Platform
  - abbr: Happy-Eyeballs
    expansion: dual-stack connection racing (RFC 8305)
  - abbr: IPv4
    expansion: Internet Protocol version 4
  - abbr: IPv6
    expansion: Internet Protocol version 6
  - abbr: LAN
    expansion: Local Area Network
  - abbr: MTU
    expansion: Maximum Transmission Unit
  - abbr: NAT
    expansion: network address translation
  - abbr: OEN
    expansion: Overlay and Edge Notes
  - abbr: PC
    expansion: personal computer
  - abbr: Pi
    expansion: single-board computer (Raspberry Pi class)
  - abbr: ULA
    expansion: unique-local address (IPv6)
  - abbr: VM
    expansion: virtual machine
  - abbr: WG
    expansion: WireGuard
---

# Wi-Fi underlay vs cellular underlay to the same cloud exit

## Context

Distinct from [OEN-20](../networking/20-lan-ula-happy-eyeballs-leak.md) (LAN ULA Happy-Eyeballs while an exit is selected). This is two underlays to the same cloud exit.

## Topology

```text
Same <exit-node>, two underlays:
  home Wi-Fi MAY encapsulate overlay inside commercial WG
  cellular MAY go direct
v4 cloud / v6 home leak is NOT "GCP broken"
Distinct from [OEN-20](../networking/20-lan-ula-happy-eyeballs-leak.md)
```

## Bind

Fill this table **before** any live change. Do **not** paste real values back into public notes.

| Placeholder | Operator fills | Class |
|-------------|----------------|-------|
| `<exit-node>` | Overlay exit node | Cloud VM or LAN Pi |

## Method

Always A/B Wi-Fi vs cellular before changing GCP NAT/MTU. MUST NOT treat a Wi-Fi-only v6 leak as a broken cloud exit.

## Consequences

Fewer pointless GCP MTU changes.

## Agent stop rule

> MUST soak the same exit from Wi-Fi and cellular after Bind is filled.
> MUST NOT declare a cloud exit broken when only one underlay fails.
> MUST NOT apply netfilter from this page.

## Procedure


### Copy-paste commands (after Bind)

```bash
# A/B: curl -4/-6 on Wi-Fi vs cellular with the same exit selected (phone), not the agent PC
```

1. **P1 — Same exit, two underlays.**
   - **Action:** Select `<exit-node>`. curl -4/-6 on home Wi-Fi vs cellular.
   - **Expected:** Families and egress differ by underlay.
   - **On failure:** If both underlays fail the same way, look at the exit ([OEN-17](../networking/17-gcp-overlay-exit.md)).
2. **P2 — Name encapsulation.**
   - **Action:** Wi-Fi may ride commercial WG; cellular may be direct overlay.
   - **Expected:** Do not call that “GCP broken.”
   - **On failure:** See [OEN-13](../networking/13-overlay-underlay-ula-layers.md).
3. **P3 — Distinct from OEN-20.**
   - **Action:** If LAN ULA Happy-Eyeballs, that spec. If only underlay differs, this spec.
   - **Expected:** One sentence in the incident which trap.
   - **On failure:** Do not mix the tables.

## Expected samples

```text
# Wi-Fi v6 egress = home tunnel prefix; cellular v6 = cloud
```

## Verify

- Wi-Fi vs cellular matrix recorded.
- GCP not blamed for a Wi-Fi-only encapsulate leak.

## MUST NOT

- MUST NOT keep changing GCP MTU for a Wi-Fi/cellular split.
- MUST NOT publish underlay IPs.
- MUST NOT publish hostnames, addresses, ULAs, or custom ports.

## Page changelog

- Edition 2 (8 Sep 2026, Mountain Time): Trap-specific Bind and agent stop rule (review cleanup).

## Related specs

- [OEN-20](../networking/20-lan-ula-happy-eyeballs-leak.md)
- [OEN-17](../networking/17-gcp-overlay-exit.md)
- [OEN-16](../networking/16-commercial-wg-endpoint-rotation.md)

## Prior art (Not novel)

Different underlays are obvious. This note is the false “GCP exit is broken” when only Wi-Fi encapsulates.

