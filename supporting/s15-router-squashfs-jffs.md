---
id: OEN-S15
title: "Router squashfs is always 100%; Save settings misses persistent overlay"
kind: supporting
status: active
edition: 1
date_published: 2026-09-08
author: Eugene Armstead
author_url: https://www.armsteadent.com/
canonical: https://eugenearmstead.github.io/overlay-and-edge-notes/supporting/s15-router-squashfs-jffs.html
keywords:
  - "router squashfs 100% full"
  - "Save settings misses jffs"
  - "Save JFFS separately"
  - "logread is OpenWrt"
  - "Merlin syslog not logread"
  - "squashfs always 100%"
  - "ASUSWRT-Merlin jffs scripts"
  - ".cfg backup without overlay scripts"
  - "judge USB jffs not root"
  - "persistent overlay Save"
  - "consumer router disk 100%"
  - "jffs scripts not in cfg"
backs:
  - OEN-12
backed_by: []
description: "Router root squashfs reports 100% full; that is normal. Save settings .cfg does not include the persistent overlay scripts. Save JFFS separately. logread is OpenWrt — this firmware uses syslog files."
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
  - abbr: WireGuard
    expansion: UDP-based VPN protocol
  - abbr: DNS
    expansion: Domain Name System
  - abbr: nft
    expansion: nftables (Linux packet filter)
  - abbr: USB
    expansion: Universal Serial Bus
  - abbr: JFFS
    expansion: journalled flash file system (router persistent overlay)
  - abbr: NVRAM
    expansion: non-volatile random-access memory
---

# Router squashfs is always 100%; Save settings misses persistent overlay

## Context

Judge USB/jffs, not squashfs percent. Public wording: persistent overlay store, not a path dump.

## Topology

```text
Router root squashfs reports 100%  (normal)
Save settings .cfg does NOT include persistent-overlay scripts
Judge USB / jffs-class store separately
logread is OpenWrt — this firmware uses syslog files
```

## Bind

Fill this table **before** any live change. Do **not** paste real values back into public notes.

| Placeholder | Operator fills | Class |
|-------------|----------------|-------|
| `<wg-iface>` | Consumer-router WireGuard client iface | Iface |
| `<lan-bridge>` | LAN bridge | Iface; MTU 1500 |
| `<wan-iface>` | WAN iface | Iface |
| `<lan-resolver>` | Intended LAN DNS | Address; never publish |


## Formulas

Save JFFS/persistent overlay separately from NVRAM Save settings.

## Method

Do not “free root” on squashfs. Backup the persistent overlay separately from Save settings.

## Consequences

Scripts survive a settings save. Operators stop panicking at 100% squashfs.

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
df -h
# Confirm writable overlay has the scripts; squashfs 100% is not "disk full."
```

1. **P1 — Ignore squashfs 100%.**
   - **Action:** df on root squashfs is 100%. Check USB/jffs-class space instead.
   - **Expected:** Writable store has room.
   - **On failure:** Do not delete firmware files on squashfs.
2. **P2 — Save JFFS separately.**
   - **Action:** Save settings .cfg does not include /jffs/scripts-class files. Copy the overlay store.
   - **Expected:** Scripts exist after a settings-only restore test (or documented equivalent).
   - **On failure:** A settings restore without JFFS loses hooks.
3. **P3 — Logs.**
   - **Action:** This firmware class uses syslog files, not OpenWrt logread.
   - **Expected:** You read the right log.
   - **On failure:** Do not require logread.

## Expected samples

```text
/dev/root  ...  100%
```

## Verify

- Ops backup includes persistent overlay.
- squashfs 100% not treated as an incident.
- ICMP / small ping success was **not** used as the pass criterion when this spec names TCP, SSH, or HTTPS.
- Bind table was filled by a human before any live `ip` / nft / iptables change.

## MUST NOT

- MUST NOT publish real jffs paths as universal.
- MUST NOT wipe squashfs to “free space.”
- MUST NOT apply live network or firewall changes until Bind is filled by a human.
- MUST NOT claim a fix on ICMP ping alone when Verify names TCP, SSH, or HTTPS.
- MUST NOT publish hostnames, addresses, ULAs, or custom ports.

## Related specs

- [OEN-18](../networking/18-per-node-changelog-contract.md)
- [OEN-12](../networking/12-consumer-wg-phantom-bridge.md)

## Prior art (Not novel)

squashfs-as-root is normal. This note is Save settings missing JFFS plus logread-vs-syslog.

