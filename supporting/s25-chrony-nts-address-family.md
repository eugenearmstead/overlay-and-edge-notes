---
id: "OEN-S25"
title: "Network Time Security chrony address-family flags need a newer chrony than the distro"
kind: "supporting"
status: "active"
edition: 2
date_published: "2026-09-08"
author: "Eugene Armstead"
author_url: "https://www.armsteadent.com/"
canonical: "https://eugenearmstead.github.io/overlay-and-edge-notes/supporting/s25-chrony-nts-address-family.html"
keywords:
  - "chrony NTS ipv6 flag distro"
  - "distro chrony parse NTS flags"
  - "Cloudflare NTS newer chrony"
  - "try v6 then v4 NTS"
  - "Network Time Security chrony"
  - "NTS address-family flags"
  - "VPS host time NTS"
  - "chrony ipv6 server option"
  - "upgrade chrony NTS"
  - "NTS handshake family"
  - "coordinator chrony NTS"
  - "time sync NTS Cloudflare"
backs:
  - OEN-15
backed_by:
  []
description: "Distro chrony may not parse NTS ipv6/ipv4 server flags. Use a newer chrony plus Cloudflare NTS; try v6 then v4."
terms:
  - abbr: chrony
    expansion: NTP/NTS time daemon
  - abbr: Cloudflare
    expansion: content delivery and Workers platform
  - abbr: ControlPath
    expansion: OpenSSH multiplexing socket path option
  - abbr: DNS
    expansion: Domain Name System
  - abbr: IPv4
    expansion: Internet Protocol version 4
  - abbr: IPv6
    expansion: Internet Protocol version 6
  - abbr: NTP
    expansion: Network Time Protocol
  - abbr: NTS
    expansion: Network Time Security
  - abbr: OEN
    expansion: Overlay and Edge Notes
  - abbr: PeerAPI
    expansion: overlay peer application-programming interface (exit DNS over HTTPS)
  - abbr: SSH
    expansion: Secure Shell
  - abbr: VPS
    expansion: Virtual Private Server
---

# Network Time Security chrony address-family flags need a newer chrony than the distro

## Context

Backs [OEN-15](../networking/15-split-host-vs-overlay-resolver.md) host stack on the VPS. Distro chrony rejects `ipv6`/`ipv4` NTS server flags.

## Topology

N/A — DNS

## Bind

Fill this table **before** any live change. Do **not** paste real values back into public notes.

| Placeholder | Operator fills | Class |
|-------------|----------------|-------|
| `<user>` | SSH user | Guest account |
| `<cloud-vps>` | Cloud VPS under test | Cloud VPS |

## Formulas

Upgrade chrony; do not comment out NTS to make it start.

## Method

Install a chrony new enough to parse address-family flags. Try NTS over IPv6 then IPv4. Host time MUST NOT depend on the commercial tunnel.

## Consequences

NTS works. Distro package is not blamed forever.

## Agent stop rule

> MUST emit bound chrony/NTS version and address-family checks after Bind is filled.
> MUST NOT comment out NTS to make distro chrony start.
> MUST NOT apply netfilter from this page.

## Procedure


### Copy-paste commands (after Bind)

```bash
ssh -o ControlPath=none <user>@<cloud-vps> 'chronyd --version; chronyc sources || true'
```

1. **P1 — chrony version.**
   - **Action:** `chronyd --version`. If NTS server lines with ipv6/ipv4 fail to parse, the distro is too old.
   - **Expected:** Need newer chrony.
   - **On failure:** Do not comment out NTS “to make it start.”
2. **P2 — v6 then v4.**
   - **Action:** Cloudflare NTS (or equivalent): try IPv6 then IPv4.
   - **Expected:** chronyc sources shows NTS.
   - **On failure:** Host view still works with tunnel down ([OEN-15](../networking/15-split-host-vs-overlay-resolver.md)).
3. **P3 — Not overlay DNS.**
   - **Action:** Time is host stack, not PeerAPI.
   - **Expected:** NTP/NTS independent of exit DNS.
   - **On failure:** Do not restart coordination for time.

## Expected samples

```text
# old: invalid directive ipv6
```

## Verify

- NTS selected in chronyc.
- Tunnel-down host still steps time or at least still resolves.

## MUST NOT

- MUST NOT drop NTS because the distro binary cannot parse flags — upgrade chrony.
- MUST NOT pin time to the tunnel.
- MUST NOT publish hostnames, addresses, ULAs, or custom ports.

## Page changelog

- Edition 2 (8 Sep 2026, Mountain Time): Trap-specific Bind and agent stop rule (review cleanup).

## Related specs

- [OEN-15](../networking/15-split-host-vs-overlay-resolver.md)

## Prior art (Not novel)

NTS is documented. This note is distro chrony rejecting address-family flags.

