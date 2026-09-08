---
id: OEN-S18
title: "Do not set exit-node on the agent workstation"
kind: supporting
status: active
edition: 1
date_published: 2026-09-08
author: Eugene Armstead
author_url: https://www.armsteadent.com/
canonical: https://eugenearmstead.github.io/overlay-and-edge-notes/supporting/s18-do-not-set-exit-on-agent-workstation.html
keywords:
  - "do not set exit-node on agent workstation"
  - "tailscale set --exit-node workstation"
  - "overlay SSH first nmap after fail"
  - "Cursor workstation exit-node"
  - "do not test GCP exit from agent"
  - "hairpin LAN via workstation exit"
  - "operator must ask exit-node"
  - "Tailscale exit on workstation"
  - "debug from overlay SSH"
  - "nmap after failed connect"
  - "S18 workstation exit"
  - "agent must not select exit"
backs:
  - OEN-17
  - OEN-04
  - OEN-20
backed_by: []
description: "Do not tailscale set --exit-node on the agent workstation unless the operator asks. Overlay SSH first. nmap only after a failed connect."
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
  - abbr: DNS
    expansion: Domain Name System
  - abbr: GCP
    expansion: Google Cloud Platform
  - abbr: VM
    expansion: virtual machine
  - abbr: NIC
    expansion: network interface card
  - abbr: nft
    expansion: nftables (Linux packet filter)
  - abbr: Pi
    expansion: single-board computer (Raspberry Pi class)
---

# Do not set exit-node on the agent workstation

## Context

Selecting an exit on the Cursor/agent host can strand the session (hairpin, DNS, or a bad cloud exit). Overlay SSH to nodes does not require an exit.

## Topology

```text
[agent workstation] --set exit-node-->  loses general internet when exit is wrong
Soak exits on <lan-pi> / <overlay-peer>
Overlay SSH first; nmap only after a failed connect
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

MUST NOT select <exit-node> on the agent/Cursor workstation unless the operator asks.

## Method

MUST NOT set exit-node on the agent workstation unless the operator explicitly asks. Soak exits from `<overlay-peer>` / a phone.

## Consequences

Agent sessions keep internet. Exit tests still happen on a Pi.

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
# On the workstation: confirm exit unset
# On <overlay-peer>: select <exit-node> briefly, curl, then clear
```

1. **P1 — Check prefs.**
   - **Action:** On the workstation: overlay exit is unset.
   - **Expected:** No exit-node.
   - **On failure:** If set, clear it unless the operator asked.
2. **P2 — Connect overlay SSH first.**
   - **Action:** SSH to `<lan-pi>` / `<cloud-vps>` overlay. nmap only after a failed connect.
   - **Expected:** SSH works without an exit.
   - **On failure:** Do not debug the exit by enabling it here.
3. **P3 — Soak elsewhere.**
   - **Action:** Exit soak on `<overlay-peer>` ([OEN-17](../networking/17-gcp-overlay-exit.md)).
   - **Expected:** Workstation remains unset.
   - **On failure:** Hairpin is [OEN-S21](s21-cloud-exit-hairpin-lan.md).

## Expected samples

```text
# workstation: ExitNode: (none)
```

## Verify

- Workstation exit unset.
- Exit soak documented on a Pi or phone.
- ICMP / small ping success was **not** used as the pass criterion when this spec names TCP, SSH, or HTTPS.
- Bind table was filled by a human before any live `ip` / nft / iptables change.

## MUST NOT

- MUST NOT set exit on the agent workstation to reproduce.
- MUST NOT nmap before the first connect when using connect wrappers.
- MUST NOT apply live network or firewall changes until Bind is filled by a human.
- MUST NOT claim a fix on ICMP ping alone when Verify names TCP, SSH, or HTTPS.
- MUST NOT publish hostnames, addresses, ULAs, or custom ports.

## Related specs

- [OEN-17](../networking/17-gcp-overlay-exit.md)
- [OEN-S21](s21-cloud-exit-hairpin-lan.md)

## Prior art (Not novel)

Exit nodes are documented. This note is “not on the agent workstation” as a hard MUST NOT.

