---
id: "OEN-S28"
title: "Reconnect during overlay peer-API outage sticks after heal"
kind: "supporting"
status: "active"
edition: 2
date_published: "2026-09-08"
author: "Eugene Armstead"
author_url: "https://www.armsteadent.com/"
canonical: "https://eugenearmstead.github.io/overlay-and-edge-notes/supporting/s28-sticky-reconnect-during-peerapi-outage.html"
keywords:
  - "sticky reconnect PeerAPI outage"
  - "phone stuck after PeerAPI heal"
  - "client toggle after DoH dead"
  - "heal exit stub not coordinator yaml"
  - "use_with_exit_node does not open PeerAPI"
  - "Android exit DNS sticky"
  - "reconnect during outage"
  - "PeerAPI recovers client stuck"
  - "do not change coordinator DNS yaml"
  - "Headscale PeerAPI sticky"
  - "exit DoH outage phones"
  - "toggle exit after heal"
backs:
  - OEN-14
  - OEN-19
backed_by:
  []
description: "Phones that rejoin while DoH is dead stay stuck after PeerAPI recovers until that client toggles. Heal the exit stub, not coordinator DNS yaml. Empty use_with_exit_node does not open PeerAPI."
terms:
  - abbr: API
    expansion: application programming interface
  - abbr: DNS
    expansion: Domain Name System
  - abbr: DoH
    expansion: DNS over HTTPS
  - abbr: OEN
    expansion: Overlay and Edge Notes
  - abbr: PeerAPI
    expansion: overlay peer application-programming interface (exit DNS over HTTPS)
  - abbr: RD
    expansion: Recursion Desired (DNS flag)
---

# Reconnect during overlay peer-API outage sticks after heal

## Context

Backs [OEN-14](../networking/14-exit-dns-is-peerapi.md). Sticky client after outage.

## Topology

```text
Phone reconnects while PeerAPI DoH is dead
PeerAPI heals  -->  that phone stays stuck until client toggle
Heal exit stub, not coordinator DNS yaml
```

## Bind

Fill this table **before** any live change. Do **not** paste real values back into public notes.

| Placeholder | Operator fills | Class |
|-------------|----------------|-------|
| *(none)* | No packet-path Bind for this trap | Use the git host, origin, or API the operator already has |

## Formulas

Empty use_with_exit_node does not open PeerAPI.

## Method

Heal PeerAPI on the exit. Toggle the stuck client. MUST NOT rewrite coordinator DNS yaml (fleet reconnect).

## Consequences

New clients work; stuck phones need a toggle, not a coordinator bounce.

## Agent stop rule

> MUST heal PeerAPI on the exit, then toggle the stuck client, after Bind is filled.
> MUST NOT rewrite coordinator DNS yaml for one sticky client.
> MUST NOT apply netfilter from this page.

## Procedure


### Copy-paste commands (after Bind)

```bash
# After stub heal: new client works. Stuck phone: exit off/on or app toggle.
```

1. **P1 — Heal exit DoH.**
   - **Action:** Fix stub/RD ([OEN-05](../networking/05-exit-peerapi-dns-stub.md), [OEN-19](../networking/19-unbound-refuses-rd0.md)). New client works.
   - **Expected:** PeerAPI up.
   - **On failure:** Do not touch coordinator yaml.
2. **P2 — Toggle stuck phones.**
   - **Action:** Phones that reconnected during the outage stay dead until exit off/on or app toggle.
   - **Expected:** They recover after toggle.
   - **On failure:** Do not restart coordination for them.
3. **P3 — Empty use_with_exit_node.**
   - **Action:** That flag does not open PeerAPI.
   - **Expected:** Do not set it as a heal.
   - **On failure:** Local DNS on exit still needs the stub.

## Expected samples

```text
# new client DoH 200; sticky phone still DNS_PROBE until toggle
```

## Verify

- New client DoH works after heal.
- Stuck client documented as toggle, not yaml.

## MUST NOT

- MUST NOT change coordinator DNS yaml to heal PeerAPI.
- MUST NOT expect empty use_with_exit_node to open PeerAPI.
- MUST NOT publish hostnames, addresses, ULAs, or custom ports.

## Page changelog

- Edition 2 (8 Sep 2026, Mountain Time): Trap-specific Bind and agent stop rule (review cleanup).

## Related specs

- [OEN-14](../networking/14-exit-dns-is-peerapi.md)
- [OEN-05](../networking/05-exit-peerapi-dns-stub.md)

