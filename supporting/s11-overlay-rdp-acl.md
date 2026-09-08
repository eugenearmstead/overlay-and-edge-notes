---
id: "OEN-S11"
title: "Overlay session-mirror remote desktop and access-control list without deny"
kind: "supporting"
status: "active"
edition: 2
date_published: "2026-09-08"
author: "Eugene Armstead"
author_url: "https://www.armsteadent.com/"
canonical: "https://eugenearmstead.github.io/overlay-and-edge-notes/supporting/s11-overlay-rdp-acl.html"
keywords:
  - "overlay session-mirror RDP"
  - "ACL without deny action"
  - "locked-screen remote desktop"
  - "Headscale ACL port-range allow"
  - "GNOME Remote Desktop overlay"
  - "overlay is an access plane"
  - "coordination ACL no deny"
  - "RDP overlay SSH still works"
  - "Tailscale RDP ACL"
  - "Allow Locked Remote Desktop"
  - "generic peers only ACL"
  - "session mirror not xrdp"
backs:
  - OEN-01
  - OEN-06
backed_by:
  []
description: "The overlay is an access plane, not only SSH. Session-mirror remote desktop plus a locked-screen extension. Coordination ACLs with no deny action need port-range allow holes. Generic peers only."
terms:
  - abbr: ACL
    expansion: access-control list
  - abbr: API
    expansion: application programming interface
  - abbr: LISTEN
    expansion: ss(8) listening socket state
  - abbr: OEN
    expansion: Overlay and Edge Notes
  - abbr: RDP
    expansion: Remote Desktop Protocol
  - abbr: SSH
    expansion: Secure Shell
  - abbr: VPN
    expansion: Virtual Private Network
  - abbr: WAN
    expansion: Wide Area Network
---

# Overlay session-mirror remote desktop and access-control list without deny

## Context

Remote Desktop Protocol (RDP) over overlay: session mirror, locked-screen extension. Self-hosted coordination with no `"deny"` action needs allow holes by port range. MUST NOT paste real access-control lists (ACL) or peer names.

## Topology

```text
[workstation] overlay RDP :3389  session mirror + locked-screen extension
Coordination ACL without a deny action needs port-range ALLOW holes
Generic peers only
```

## Bind

Fill this table **before** any live change. Do **not** paste real values back into public notes.

| Placeholder | Operator fills | Class |
|-------------|----------------|-------|
| *(none)* | No packet-path Bind for this trap | Use the git host, origin, or API the operator already has |

## Formulas

Overlay is an access plane, not only SSH. MUST NOT publish real ACL peers.

## Method

Document RDP as overlay, not a second VPN. ACL: allow the needed port range for the intended peer class. No real inventory.

## Consequences

Operators stop thinking overlay is SSH-only. ACL holes are explicit.

## Agent stop rule

> MUST emit bound ACL/RDP notes with placeholders only after Bind is filled.
> MUST NOT publish real ACL peers, usernames, or overlay addresses.
> MUST NOT apply netfilter from this page.

## Procedure


### Copy-paste commands (after Bind)

```bash
ss -lntp | grep 3389 || true
# Confirm overlay ACL allows the session-mirror port range; a product with no deny still needs allow holes.
```

1. **P1 — Session mirror + locked screen.**
   - **Action:** Use the desktop’s remote-desktop stack that mirrors the session. Enable locked-screen remote if required.
   - **Expected:** A phone client can attach to the existing session.
   - **On failure:** xrdp-style new sessions are a different product.
2. **P2 — Overlay bind, not WAN.**
   - **Action:** Listen on overlay addresses. Firewall: overlay prefix only.
   - **Expected:** WAN RDP closed.
   - **On failure:** Do not publish the overlay address.
3. **P3 — ACL without deny.**
   - **Action:** If the coordinator has no deny action, punch allow port ranges for the peer class that must RDP.
   - **Expected:** Intended peer can connect; others cannot.
   - **On failure:** Generic peers only in public text.

## Expected samples

```text
LISTEN 0  ... *:3389
```

## Verify

- RDP works over overlay while WAN is closed.
- ACL text in public has no real peers.

## MUST NOT

- MUST NOT paste real ACL peer lists.
- MUST NOT expose RDP on WAN.
- MUST NOT publish hostnames.
- MUST NOT publish hostnames, addresses, ULAs, or custom ports.

## Page changelog

- Edition 2 (8 Sep 2026, Mountain Time): Trap-specific Bind and agent stop rule (review cleanup).

## Related specs

- [OEN-01](../networking/01-overlay-ssh-byte-cliff.md)
- [OEN-13](../networking/13-overlay-underlay-ula-layers.md)

