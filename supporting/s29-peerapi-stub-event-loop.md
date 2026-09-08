---
id: "OEN-S29"
title: "Overlay peer-API stub event-loop blocks; UDP receive queue grows"
kind: "supporting"
status: "active"
edition: 2
date_published: "2026-09-08"
author: "Eugene Armstead"
author_url: "https://www.armsteadent.com/"
canonical: "https://eugenearmstead.github.io/overlay-and-edge-notes/supporting/s29-peerapi-stub-event-loop.html"
keywords:
  - "PeerAPI stub event-loop blocks"
  - "UDP recv-Q grows"
  - "select() sync upstream DNS"
  - "cellular DNS dies stub"
  - "thread pool PeerAPI stub"
  - "upstream timeout stub"
  - "single-threaded DoH stub"
  - "recv-Q 160KB DNS"
  - "exit stub event loop"
  - "Android exit DNS timeout"
  - "PeerAPI UDP queue"
  - "do not block select DNS"
backs:
  - OEN-05
  - OEN-19
backed_by:
  []
description: "Synchronous upstream inside select() fills UDP recv-Q; cellular DNS dies. Thread pool plus timeouts."
terms:
  - abbr: API
    expansion: application programming interface
  - abbr: ControlPath
    expansion: OpenSSH multiplexing socket path option
  - abbr: DNS
    expansion: Domain Name System
  - abbr: KB
    expansion: kilobyte
  - abbr: LAN
    expansion: Local Area Network
  - abbr: OEN
    expansion: Overlay and Edge Notes
  - abbr: PeerAPI
    expansion: overlay peer application-programming interface (exit DNS over HTTPS)
  - abbr: Pi
    expansion: single-board computer (Raspberry Pi class)
  - abbr: SSH
    expansion: Secure Shell
  - abbr: UDP
    expansion: User Datagram Protocol
  - abbr: VM
    expansion: virtual machine
---

# Overlay peer-API stub event-loop blocks; UDP receive queue grows

## Context

Backs [OEN-05](../networking/05-exit-peerapi-dns-stub.md). ~160 KB recv-Q under phone load in the field.

## Topology

```text
PeerAPI stub select() + sync upstream  -->  UDP recv-Q grows (~160 KB field)
cellular DNS dies
Thread pool + upstream timeout; still bind 127.0.0.1 only
```

## Bind

Fill this table **before** any live change. Do **not** paste real values back into public notes.

| Placeholder | Operator fills | Class |
|-------------|----------------|-------|
| `<user>` | SSH user | Guest account |
| `<exit-node>` | Overlay exit node | Cloud VM or LAN Pi |

## Formulas

MUST NOT sync-resolve inside select().

## Method

MUST NOT call upstream synchronously in the select loop. Thread pool + upstream timeout.

## Consequences

Cellular DNS survives bursts.

## Agent stop rule

> MUST emit bound PeerAPI stub / recv-Q checks after Bind is filled.
> MUST NOT sync-resolve inside the select loop.
> MUST NOT apply netfilter from this page.

## Procedure


### Copy-paste commands (after Bind)

```bash
ssh -o ControlPath=none <user>@<exit-node> 'ss -u -n | awk "NR==1 || /:53/"'
```

1. **P1 — Watch recv-Q.**
   - **Action:** During phone soak, `ss -u` recv-Q on the stub.
   - **Expected:** Growing queue = blocked loop.
   - **On failure:** If queue stays 0, this spec does not apply.
2. **P2 — Thread pool + timeout.**
   - **Action:** Move upstream I/O off the event loop. Timeout the forward.
   - **Expected:** recv-Q stays low. Cellular DNS lives.
   - **On failure:** Do not add more inline handlers.
3. **P3 — Loopback only still.**
   - **Action:** Bind remains 127.0.0.1 ([OEN-05](../networking/05-exit-peerapi-dns-stub.md)).
   - **Expected:** Exit still works.
   - **On failure:** Do not bind overlay :53 to “help load.”

## Expected samples

```text
# Recv-Q climbing under phone soak
```

## Verify

- recv-Q near 0 under load.
- Thread pool present.

## MUST NOT

- MUST NOT sync-resolve inside select().
- MUST NOT bind overlay :53.
- MUST NOT publish hostnames, addresses, ULAs, or custom ports.

## Page changelog

- Edition 2 (8 Sep 2026, Mountain Time): Trap-specific Bind and agent stop rule (review cleanup).

## Related specs

- [OEN-05](../networking/05-exit-peerapi-dns-stub.md)

