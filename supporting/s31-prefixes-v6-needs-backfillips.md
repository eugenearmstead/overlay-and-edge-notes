---
id: "OEN-S31"
title: "prefixes.v6 needs nodes backfillips, not restart alone"
kind: "supporting"
status: "active"
edition: 2
date_published: "2026-09-08"
author: "Eugene Armstead"
author_url: "https://www.armsteadent.com/"
canonical: "https://eugenearmstead.github.io/overlay-and-edge-notes/supporting/s31-prefixes-v6-needs-backfillips.html"
keywords:
  - "prefixes.v6 needs backfillips"
  - "nodes backfillips --force"
  - "restart alone tailscale ip -6 empty"
  - "Headscale prefixes.v6 existing nodes"
  - "ULA missing after enable v6"
  - "backfillips then restart"
  - "tailscale ip -6 empty"
  - "self-hosted coordination ULA"
  - "existing nodes no IPv6"
  - "prefixes.v6 rollout"
  - "Headscale backfillips"
  - "enable IPv6 overlay nodes"
backs:
  - OEN-13
backed_by:
  []
description: "Enabling prefixes.v6 on existing nodes needs nodes backfillips --force then restart. Restart alone leaves tailscale ip -6 empty."
terms:
  - abbr: CLI
    expansion: command-line interface
  - abbr: ControlPath
    expansion: OpenSSH multiplexing socket path option
  - abbr: HTTPS
    expansion: Hypertext Transfer Protocol Secure
  - abbr: IPv6
    expansion: Internet Protocol version 6
  - abbr: OEN
    expansion: Overlay and Edge Notes
  - abbr: SSH
    expansion: Secure Shell
  - abbr: ULA
    expansion: unique-local address (IPv6)
  - abbr: VPS
    expansion: Virtual Private Server
---

# prefixes.v6 needs nodes backfillips, not restart alone

## Context

Existing nodes do not grow ULA because a flag flipped. New nodes might. Backs [OEN-13](../networking/13-overlay-underlay-ula-layers.md).

## Topology

```text
prefixes.v6 enabled  +  restart only  -->  tailscale ip -6 empty on EXISTING nodes
Need nodes backfillips --force then restart
```

## Bind

Fill this table **before** any live change. Do **not** paste real values back into public notes.

| Placeholder | Operator fills | Class |
|-------------|----------------|-------|
| `<overlay-impl>` | Overlay implementation class | `tailscale-compatible` or other — stop and translate CLI |
| `<user>` | SSH user | Guest account |
| `<cloud-vps>` | Cloud VPS under test | Cloud VPS |

## Formulas

Do not bind HTTPS to missing ULA.

## Method

After prefixes.v6, run coordination `nodes backfillips --force` (or equivalent) then restart those nodes. MUST NOT expect restart alone.

## Consequences

Existing nodes get overlay IPv6. Binds that waited for ULA can start.

## Agent stop rule

> MUST emit bound `nodes backfillips` after `<overlay-impl>` is `tailscale-compatible`.
> MUST NOT expect `tailscale ip -6` on existing nodes from prefixes.v6 + restart alone.
> MUST NOT apply netfilter from this page.

## Procedure

This spec does not apply if `<overlay-impl>` is not tailscale-compatible.

### Copy-paste commands (after Bind)

```bash
ssh -o ControlPath=none <user>@<cloud-vps> 'tailscale ip -6 || true'
# Coordinator: backfill existing nodes (private ops), then restart those nodes.
```

1. **P1 — See empty ip -6.**
   - **Action:** `tailscale ip -6` empty after prefixes.v6 + restart only.
   - **Expected:** Need backfill.
   - **On failure:** Do not bind HTTPS to missing ULA.
2. **P2 — backfillips --force.**
   - **Action:** On the coordinator, backfill existing nodes, then restart nodes.
   - **Expected:** `ip -6` populated.
   - **On failure:** Do not paste node IDs publicly.
3. **P3 — Then bind.**
   - **Action:** Services that need ULA start after the address exists ([OEN-13](../networking/13-overlay-underlay-ula-layers.md)).
   - **Expected:** No boot hole.
   - **On failure:** Ops SSH still overlay v4.

## Expected samples

```text
# empty ip -6 after restart-only
```

## Verify

- Existing node has overlay v6 after backfill+restart.
- Restart-only was not enough.

## MUST NOT

- MUST NOT claim restart alone backfills prefixes.v6.
- MUST NOT publish node IDs or ULAs.
- MUST NOT publish hostnames, addresses, ULAs, or custom ports.

## Page changelog

- Edition 2 (8 Sep 2026, Mountain Time): Trap-specific Bind and agent stop rule (review cleanup).

## Related specs

- [OEN-13](../networking/13-overlay-underlay-ula-layers.md)

## Prior art (Not novel)

Prefix enable is documented. This note is existing nodes needing backfillips --force.

