---
id: OEN-S21
title: "Cloud exit hairpins home LAN HTTP while overlay SSH still works"
kind: supporting
status: active
edition: 1
date_published: 2026-09-08
author: Eugene Armstead
author_url: https://www.armsteadent.com/
canonical: https://eugenearmstead.github.io/overlay-and-edge-notes/supporting/s21-cloud-exit-hairpin-lan.html
keywords:
  - exit-node
  - hairpin
  - lan
backs:
  - OEN-17
backed_by: []
description: "With a cloud exit selected, overlay SSH to the router still works while HTTP to LAN DNS/GUI dies. Not a broken router. Clear the exit on the workstation."
terms:
  - abbr: OEN
    expansion: Overlay and Edge Notes
  - abbr: SSH
    expansion: Secure Shell
  - abbr: LAN
    expansion: Local Area Network
  - abbr: WAN
    expansion: Wide Area Network
  - abbr: VPN
    expansion: Virtual Private Network
  - abbr: TCP
    expansion: Transmission Control Protocol
  - abbr: MTU
    expansion: Maximum Transmission Unit
  - abbr: ICMP
    expansion: Internet Control Message Protocol
  - abbr: HTTP
    expansion: Hypertext Transfer Protocol
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
  - abbr: ControlPath
    expansion: OpenSSH multiplexing socket path option
  - abbr: Pi
    expansion: single-board computer (Raspberry Pi class)
  - abbr: GUI
    expansion: graphical user interface
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
| `<exit-node>` | Overlay exit node | Cloud VM or LAN Pi used as exit |
| `<overlay-peer>` | Soak client (**not** the agent workstation) | LAN Pi |
| `<user>` | SSH user | Guest |
| `<overlay-tun>` | Overlay tun on the exit | Iface |
| `<gcp-nic>` | Public NIC on a Google Cloud guest | Iface; omit on non-GCP exits |
| `<wan-iface>` | WAN / public NIC | Iface |
| `<mss4>` / `<mss6>` | Computed from underlay or overlay tun MTU | Formulas |


## Formulas

Hairpin: LAN GUI/DNS HTTP goes out the exit and cannot come back.

## Method

If overlay SSH to the LAN router works and LAN HTTP dies, clear exit-node on that client. MUST NOT reboot the router first.

## Consequences

LAN GUI returns. Router is not “down.”

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
- ICMP / small ping success was **not** used as the pass criterion when this spec names TCP, SSH, or HTTPS.
- Bind table was filled by a human before any live `ip` / nft / iptables change.

## MUST NOT

- MUST NOT reboot the router as the first hairpin fix.
- MUST NOT gcloud reset the VM.
- MUST NOT apply live network or firewall changes until Bind is filled by a human.
- MUST NOT claim a fix on ICMP ping alone when Verify names TCP, SSH, or HTTPS.
- MUST NOT publish hostnames, addresses, ULAs, or custom ports.

## Related specs

- [OEN-17](../networking/17-gcp-overlay-exit.md)
- [OEN-S18](s18-do-not-set-exit-on-agent-workstation.md)

## Prior art (Not novel)

VPN hairpin is known. This note is cloud overlay exit vs LAN HTTP with SSH still up.

