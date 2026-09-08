---
id: "OEN-S21"
title: "Cloud exit hairpins home LAN HTTP while overlay SSH still works"
kind: "supporting"
status: "active"
edition: 2
date_published: "2026-09-08"
author: "Eugene Armstead"
author_url: "https://www.armsteadent.com/"
canonical: "https://eugenearmstead.github.io/overlay-and-edge-notes/supporting/s21-cloud-exit-hairpin-lan.html"
keywords:
  - "cloud exit hairpin LAN HTTP"
  - "overlay SSH router still works"
  - "LAN DNS GUI dies with exit"
  - "not a broken router"
  - "clear exit on workstation"
  - "Tailscale exit hairpin home"
  - "HTTP LAN timeout exit selected"
  - "Identity-Aware Proxy not this trap"
  - "Allow LAN Access hairpin"
  - "cloud exit vs home LAN"
  - "SSH overlay HTTP LAN fail"
  - "workstation exit selected"
backs:
  - OEN-17
backed_by:
  []
description: "With a cloud exit selected, overlay SSH to the router still works while HTTP to LAN DNS/GUI dies. Not a broken router. Clear the exit on the workstation."
terms:
  - abbr: ControlPath
    expansion: OpenSSH multiplexing socket path option
  - abbr: DNS
    expansion: Domain Name System
  - abbr: GUI
    expansion: graphical user interface
  - abbr: HTTP
    expansion: Hypertext Transfer Protocol
  - abbr: LAN
    expansion: Local Area Network
  - abbr: LAN-HTTP
    expansion: LAN-HTTP
  - abbr: OEN
    expansion: Overlay and Edge Notes
  - abbr: Pi
    expansion: single-board computer (Raspberry Pi class)
  - abbr: SSH
    expansion: Secure Shell
  - abbr: URL
    expansion: Uniform Resource Locator
  - abbr: VM
    expansion: virtual machine
  - abbr: VPN
    expansion: Virtual Private Network
---

# Cloud exit hairpins home LAN HTTP while overlay SSH still works

## Context

Backs [OEN-17](../networking/17-gcp-overlay-exit.md) and [OEN-S18](s18-do-not-set-exit-on-agent-workstation.md). Hairpin: LAN HTTP goes out the exit and cannot come back.

## Topology

```text
[workstation] exit selected --> LAN HTTP hairpins out the exit
overlay SSH to the router still works
Clear exit on that client. MUST NOT reboot the router first.
```

## Bind

Fill this table **before** any live change. Do **not** paste real values back into public notes.

| Placeholder | Operator fills | Class |
|-------------|----------------|-------|
| `<user>` | SSH user | Guest account |
| `<router-overlay>` | Consumer-router overlay address | Overlay; never publish |
| `<lan-gui>` | LAN HTTP admin URL | URL; never publish the real host |

## Formulas

Hairpin: LAN GUI/DNS HTTP goes out the exit and cannot come back.

## Method

If overlay SSH to the LAN router works and LAN HTTP dies, clear exit-node on that client. MUST NOT reboot the router first.

## Consequences

LAN GUI returns. Router is not “down.”

## Agent stop rule

> MUST emit bound overlay-SSH vs LAN-HTTP checks after Bind is filled.
> MUST NOT reboot the router first when overlay SSH still works.
> MUST NOT apply netfilter from this page.

## Procedure


### Copy-paste commands (after Bind)

```bash
ssh -o ControlPath=none <user>@<router-overlay> 'echo overlay-ssh-ok'
curl -sS --max-time 5 http://<lan-gui>/ || true
# Clear exit on the workstation; retry LAN HTTP.
```

1. **P1 — Overlay SSH vs LAN HTTP.**
   - **Action:** SSH to the router overlay. curl the LAN DNS/GUI.
   - **Expected:** SSH works; HTTP dies.
   - **On failure:** If SSH also dead, not hairpin.
2. **P2 — Clear exit.**
   - **Action:** Unset exit-node on that client. Retry LAN HTTP.
   - **Expected:** HTTP 200.
   - **On failure:** Do not reset the cloud VM.
3. **P3 — Soak exits on a Pi.**
   - **Action:** Do not leave exit on the agent workstation ([OEN-S18](s18-do-not-set-exit-on-agent-workstation.md)).
   - **Expected:** Workstation unset.
   - **On failure:** Document privately; no hostnames.

## Expected samples

```text
overlay-ssh-ok
# curl: empty reply / timeout until exit cleared
```

## Verify

- LAN HTTP works with exit cleared.
- Overlay SSH was never the failure.

## MUST NOT

- MUST NOT reboot the router as the first hairpin fix.
- MUST NOT gcloud reset the VM.
- MUST NOT publish hostnames, addresses, ULAs, or custom ports.

## Page changelog

- Edition 2 (8 Sep 2026, Mountain Time): Trap-specific Bind and agent stop rule (review cleanup).

## Related specs

- [OEN-17](../networking/17-gcp-overlay-exit.md)
- [OEN-S18](s18-do-not-set-exit-on-agent-workstation.md)

## Prior art (Not novel)

VPN hairpin is known. This note is cloud overlay exit vs LAN HTTP with SSH still up.

