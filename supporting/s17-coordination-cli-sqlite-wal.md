---
id: "OEN-S17"
title: "Coordination CLI blocks on SQLite write-ahead log while serve is up"
kind: "supporting"
status: "active"
edition: 2
date_published: "2026-09-08"
author: "Eugene Armstead"
author_url: "https://www.armsteadent.com/"
canonical: "https://eugenearmstead.github.io/overlay-and-edge-notes/supporting/s17-coordination-cli-sqlite-wal.html"
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
backs:
  []
backed_by:
  []
description: "Coordination nodes-list CLI can block minutes on SQLite WAL while serve is up. Health checks MUST use HTTP /health or a readonly sqlite query, not the admin CLI."
terms:
  - abbr: API
    expansion: application programming interface
  - abbr: CLI
    expansion: command-line interface
  - abbr: DB
    expansion: database
  - abbr: GET
    expansion: HTTP method
  - abbr: HTTP
    expansion: Hypertext Transfer Protocol
  - abbr: OEN
    expansion: Overlay and Edge Notes
  - abbr: SIGKILL
    expansion: Unix signal 9 (kill)
  - abbr: SQLite
    expansion: embedded SQL database
  - abbr: SSH
    expansion: Secure Shell
  - abbr: systemd
    expansion: Linux service manager
  - abbr: WAL
    expansion: write-ahead log
---

# Coordination CLI blocks on SQLite write-ahead log while serve is up

## Context

Operators hang SSH sessions on `nodes list` during WAL checkpoints. Serve is fine.

## Topology

N/A — API

## Bind

Fill this table **before** any live change. Do **not** paste real values back into public notes.

| Placeholder | Operator fills | Class |
|-------------|----------------|-------|
| `<health-port>` | Coordination HTTP health port | Port the operator already uses |

## Formulas

Serve can be up while CLI is stuck.

## Method

Health MUST NOT call the admin CLI. Use HTTP `/health` or a readonly sqlite query.

## Consequences

Health checks return. Serve is not mistaken for dead.

## Agent stop rule

> MUST emit bound `/health` (or readonly sqlite) checks after Bind is filled.
> MUST NOT call the coordination admin CLI from a health probe.
> MUST NOT apply netfilter from this page.

## Procedure


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

## MUST NOT

- MUST NOT health-check with nodes list.
- MUST NOT publish the DB path.
- MUST NOT publish hostnames, addresses, ULAs, or custom ports.

## Page changelog

- Edition 2 (8 Sep 2026, Mountain Time): Trap-specific Bind and agent stop rule (review cleanup).

## Related specs

- [OEN-14](../networking/14-exit-dns-is-peerapi.md)
- [OEN-S19](s19-push-small-overlay-snapshots.md)

## Prior art (Not novel)

SQLite WAL blocking is known. This note is coordination CLI vs /health as the health contract.

