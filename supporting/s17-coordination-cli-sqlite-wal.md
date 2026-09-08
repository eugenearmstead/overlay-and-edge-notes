---
id: OEN-S17
title: "Coordination CLI blocks on SQLite write-ahead log while serve is up"
kind: supporting
status: active
edition: 1
date_published: 2026-09-08
author: Eugene Armstead
author_url: https://www.armsteadent.com/
canonical: https://eugenearmstead.github.io/overlay-and-edge-notes/supporting/s17-coordination-cli-sqlite-wal.html
keywords:
  - "coordination CLI SQLite WAL block"
  - "nodes list blocks while serve up"
  - "Headscale sqlite WAL"
  - "health check HTTP /health"
  - "do not use admin CLI health"
  - "readonly sqlite query"
  - "CLI hang minutes WAL"
  - "self-hosted coordination WAL"
  - "serve up CLI blocked"
  - "SQLite write-ahead log lock"
  - "Headscale nodes list timeout"
  - "healthcheck not CLI"
backs: []
backed_by: []
description: "Coordination nodes-list CLI can block minutes on SQLite WAL while serve is up. Health checks MUST use HTTP /health or a readonly sqlite query, not the admin CLI."
terms:
  - abbr: OEN
    expansion: Overlay and Edge Notes
  - abbr: SSH
    expansion: Secure Shell
  - abbr: VPS
    expansion: Virtual Private Server
  - abbr: LAN
    expansion: Local Area Network
  - abbr: WAN
    expansion: Wide Area Network
  - abbr: TCP
    expansion: Transmission Control Protocol
  - abbr: MSS
    expansion: Maximum Segment Size
  - abbr: MTU
    expansion: Maximum Transmission Unit
  - abbr: ICMP
    expansion: Internet Control Message Protocol
  - abbr: HTTP
    expansion: Hypertext Transfer Protocol
  - abbr: HTTPS
    expansion: Hypertext Transfer Protocol Secure
  - abbr: WireGuard
    expansion: UDP-based VPN protocol
  - abbr: CLI
    expansion: command-line interface
  - abbr: nft
    expansion: nftables (Linux packet filter)
  - abbr: WAL
    expansion: write-ahead log
  - abbr: Pi
    expansion: single-board computer (Raspberry Pi class)
  - abbr: SQLite
    expansion: embedded SQL database
  - abbr: systemd
    expansion: Linux service manager
  - abbr: GET
    expansion: HTTP method
  - abbr: DB
    expansion: database
  - abbr: SIGKILL
    expansion: Unix signal 9 (kill)
---

# Coordination CLI blocks on SQLite write-ahead log while serve is up

## Context

Operators hang SSH sessions on `nodes list` during WAL checkpoints. Serve is fine.

## Topology

```text
coordination `nodes list` CLI  -->  blocks minutes on SQLite WAL
HTTP /health or readonly sqlite still works
Health checks MUST NOT use the admin CLI
```

## Bind

Fill this table **before** any live change. Do **not** paste real values back into public notes.

| Placeholder | Operator fills | Class |
|-------------|----------------|-------|
| `<cloud-vps>` | Overlay SSH target | Cloud VPS |
| `<lan-pi>` | Overlay SSH target | LAN Pi |
| `<user>` | SSH user | Guest account |
| `<wg-iface>` | Commercial WireGuard iface | Router or VPS client |
| `<wan-iface>` | WAN iface | Router |
| `<lan-bridge>` | LAN bridge | Router (MTU 1500) |
| `<overlay-tun>` | Overlay tun iface | Node under test |
| `<wg-mtu>` | MTU integer from `ip link` | Measured |
| `<mss4>` / `<mss6>` | Computed MSS | Formulas |
| `<vps-public-v4>` / `<vps-public-v6>` | VPS public addresses | WAN; never publish |
| `<overlay-v4>` / `<overlay-v6>` | Overlay addresses | Overlay; never publish |


## Formulas

Serve can be up while CLI is stuck.

## Method

Health MUST NOT call the admin CLI. Use HTTP `/health` or a readonly sqlite query.

## Consequences

Health checks return. Serve is not mistaken for dead.

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
curl -sS --max-time 5 http://127.0.0.1:<health-port>/health
# Do not: coordination nodes list   from a 15-min timer
```

1. **P1 — Reproduce the block.**
   - **Action:** With serve up, run nodes list; time it. Concurrently GET /health.
   - **Expected:** /health is fast; CLI blocks.
   - **On failure:** If both hang, that is a different outage.
2. **P2 — Switch health to HTTP.**
   - **Action:** Replace CLI in systemd/fleet health with /health.
   - **Expected:** Health 200 while CLI may still be slow.
   - **On failure:** Do not SIGKILL serve to unblock the CLI.
3. **P3 — Readonly sqlite if you must query.**
   - **Action:** A readonly query against the DB MAY be used. Not the admin CLI.
   - **Expected:** Returns without taking the write lock the CLI wants.
   - **On failure:** Do not vacuum from health.

## Expected samples

```text
ok
# CLI still hung on WAL
```

## Verify

- Health uses /health.
- CLI slowness no longer pages as down.
- ICMP / small ping success was **not** used as the pass criterion when this spec names TCP, SSH, or HTTPS.
- Bind table was filled by a human before any live `ip` / nft / iptables change.

## MUST NOT

- MUST NOT health-check with nodes list.
- MUST NOT publish the DB path.
- MUST NOT apply live network or firewall changes until Bind is filled by a human.
- MUST NOT claim a fix on ICMP ping alone when Verify names TCP, SSH, or HTTPS.
- MUST NOT publish hostnames, addresses, ULAs, or custom ports.

## Related specs

- [OEN-14](../networking/14-exit-dns-is-peerapi.md)
- [OEN-S19](s19-push-small-overlay-snapshots.md)

## Prior art (Not novel)

SQLite WAL blocking is known. This note is coordination CLI vs /health as the health contract.

