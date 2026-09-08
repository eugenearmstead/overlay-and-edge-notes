---
id: OEN-S08
title: "Canonical disk + tmpfs RAM origin on a Pi"
kind: supporting
status: active
edition: 1
date_published: 2026-09-08
author: Eugene Armstead
author_url: https://www.armsteadent.com/
canonical: https://eugenearmstead.github.io/overlay-and-edge-notes/supporting/s08-canonical-disk-tmpfs-origin.html
keywords:
  - "canonical disk tmpfs RAM origin"
  - "Pi SD wear Cloudflare origin"
  - "deploy persistent then sync RAM"
  - "HTML-only rsync wrong tree"
  - "tmpfs origin Raspberry Pi"
  - "CDN hits RAM not SD"
  - "static site tmpfs serve"
  - "looks deployed wrong root"
  - "canonical disk tree"
  - "Pi origin sync-to-RAM"
  - "nginx tmpfs document root"
  - "SD card static origin"
backs:
  - OEN-10
backed_by: []
description: "Deploy to the persistent disk tree, then sync to a tmpfs RAM origin so the content delivery network hits RAM, not the SD card."
terms:
  - abbr: OEN
    expansion: Overlay and Edge Notes
  - abbr: SSH
    expansion: Secure Shell
  - abbr: TCP
    expansion: Transmission Control Protocol
  - abbr: ICMP
    expansion: Internet Control Message Protocol
  - abbr: HTTPS
    expansion: Hypertext Transfer Protocol Secure
  - abbr: HTML
    expansion: HyperText Markup Language
  - abbr: CSS
    expansion: Cascading Style Sheets
  - abbr: JS
    expansion: JavaScript
  - abbr: nft
    expansion: nftables (Linux packet filter)
  - abbr: ControlPath
    expansion: OpenSSH multiplexing socket path option
  - abbr: URL
    expansion: Uniform Resource Locator
  - abbr: UI
    expansion: user interface
  - abbr: RAM
    expansion: random-access memory
  - abbr: Pi
    expansion: single-board computer (Raspberry Pi class)
  - abbr: SD
    expansion: Secure Digital (flash storage)
  - abbr: tmpfs
    expansion: temporary file system in RAM
  - abbr: Cloudflare
    expansion: content delivery and Workers platform
---

# Canonical disk + tmpfs RAM origin on a Pi

## Context

Not new as “logs in RAM.” The claim is deploy-to-persistent then sync-to-RAM. HTML-only rsync to the wrong tree looks deployed ([OEN-S06](s06-do-not-ship-html-only.md)). MUST NOT describe a private origin hostname.

## Topology

```text
[Pi] canonical disk tree  -->  sync --> tmpfs RAM origin
Cloudflare origin SHOULD hit RAM, not the SD card
HTML-only rsync to the wrong tree looks deployed
```

## Bind

Fill this table **before** any live change. Do **not** paste real values back into public notes.

| Placeholder | Operator fills | Class |
|-------------|----------------|-------|
| `<worker-root>` | Worker / UI source tree | Directory on the workstation |
| `<live-url>` | Public HTTPS origin | URL the browser loads |
| `<preview-url>` | Preview origin if used | URL |
| `<html-path>` | Path that becomes a Response body | File glob |


## Formulas

Deploy to persistent, then sync-to-RAM. Confirm both trees have CSS/JS.

## Method

Canonical files live on disk. The serve root MAY be tmpfs. Sync disk→RAM after deploy. MUST NOT treat RAM-only as the backup.

## Consequences

SD wear drops. Missed sync looks like a CSS bug.

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
ssh -o ControlPath=none <user>@<lan-pi> 'df -hT | grep -E "tmpfs|ext"; ls <ram-origin>/chrome.css <disk-origin>/chrome.css'
```

1. **P1 — Name the two trees.**
   - **Action:** Persistent canonical vs tmpfs serve path (class, not inventory).
   - **Expected:** Both exist. Serve reads RAM.
   - **On failure:** If sudo path missing, do not invent it.
2. **P2 — Deploy disk first.**
   - **Action:** Rsync full site (HTML/CSS/JS/images) to disk. Then copy to tmpfs.
   - **Expected:** Bytes match. Asset 200s ([OEN-S06](s06-do-not-ship-html-only.md)).
   - **On failure:** HTML-only to RAM is a false deploy.
3. **P3 — Reboot behavior.**
   - **Action:** After reboot, tmpfs is empty until sync. A boot unit MUST restore from disk.
   - **Expected:** Site returns after reboot without a manual copy.
   - **On failure:** Missing unit means the origin is empty — not a Cloudflare outage.

## Expected samples

```text
tmpfs   ...  /srv/ram-origin
```

## Verify

- Disk and RAM hashes match after deploy.
- Reboot restores RAM from disk.
- ICMP / small ping success was **not** used as the pass criterion when this spec names TCP, SSH, or HTTPS.
- Bind table was filled by a human before any live `ip` / nft / iptables change.

## MUST NOT

- MUST NOT skip the disk copy.
- MUST NOT publish the Pi hostname.
- MUST NOT HTML-only to RAM.
- MUST NOT apply live network or firewall changes until Bind is filled by a human.
- MUST NOT claim a fix on ICMP ping alone when Verify names TCP, SSH, or HTTPS.
- MUST NOT publish hostnames, addresses, ULAs, or custom ports.

## Related specs

- [OEN-S06](s06-do-not-ship-html-only.md)
- [OEN-10](../web/10-one-blocking-stylesheet-variable-fonts.md)

## Prior art (Not novel)

tmpfs origins are known. This note is disk-then-RAM plus wrong-tree HTML-only.

