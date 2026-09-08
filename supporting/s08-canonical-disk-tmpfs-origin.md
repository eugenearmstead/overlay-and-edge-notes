---
id: "OEN-S08"
title: "Canonical disk + tmpfs RAM origin on a Pi"
kind: "supporting"
status: "active"
edition: 2
date_published: "2026-09-08"
author: "Eugene Armstead"
author_url: "https://www.armsteadent.com/"
canonical: "https://eugenearmstead.github.io/overlay-and-edge-notes/supporting/s08-canonical-disk-tmpfs-origin.html"
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
backed_by:
  []
description: "Deploy to the persistent disk tree, then sync to a tmpfs RAM origin so the content delivery network hits RAM, not the SD card."
terms:
  - abbr: Cloudflare
    expansion: content delivery and Workers platform
  - abbr: ControlPath
    expansion: OpenSSH multiplexing socket path option
  - abbr: CSS
    expansion: Cascading Style Sheets
  - abbr: HTML
    expansion: HyperText Markup Language
  - abbr: JS
    expansion: JavaScript
  - abbr: LAN
    expansion: Local Area Network
  - abbr: OEN
    expansion: Overlay and Edge Notes
  - abbr: Pi
    expansion: single-board computer (Raspberry Pi class)
  - abbr: RAM
    expansion: random-access memory
  - abbr: SD
    expansion: Secure Digital (flash storage)
  - abbr: SSH
    expansion: Secure Shell
---

# Canonical disk + tmpfs RAM origin on a Pi

## Context

Not new as “logs in RAM.” The claim is deploy-to-persistent then sync-to-RAM. HTML-only rsync to the wrong tree looks deployed ([OEN-S06](s06-do-not-ship-html-only.md)). MUST NOT describe a private origin hostname.

## Topology

N/A — deploy

## Bind

Fill this table **before** any live change. Do **not** paste real values back into public notes.

| Placeholder | Operator fills | Class |
|-------------|----------------|-------|
| `<user>` | SSH user | Guest account |
| `<lan-pi>` | Always-on LAN Pi | LAN Pi |
| `<ram-origin>` | tmpfs serve root | Directory on the Pi |
| `<site.css>` | Origin stylesheet filename | Asset |
| `<disk-origin>` | Persistent canonical web tree | Directory on the Pi |

## Formulas

Deploy to persistent, then sync-to-RAM. Confirm both trees have CSS/JS.

## Method

Canonical files live on disk. The serve root MAY be tmpfs. Sync disk→RAM after deploy. MUST NOT treat RAM-only as the backup.

## Consequences

SD wear drops. Missed sync looks like a CSS bug.

## Agent stop rule

> MUST name `<disk-origin>` and `<ram-origin>` after Bind is filled.
> MUST NOT rsync HTML-only to the RAM tree.
> MUST NOT call a missing `<site.css>` on one tree a CSS bug ([OEN-S06](s06-do-not-ship-html-only.md)).
> MUST NOT apply netfilter from this page.

## Procedure


### Copy-paste commands (after Bind)

```bash
ssh -o ControlPath=none <user>@<lan-pi> 'df -hT | grep -E "tmpfs|ext"; ls <ram-origin>/<site.css> <disk-origin>/<site.css>'
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

## MUST NOT

- MUST NOT skip the disk copy.
- MUST NOT publish the Pi hostname.
- MUST NOT HTML-only to RAM.
- MUST NOT publish hostnames, addresses, ULAs, or custom ports.

## Page changelog

- Edition 2 (8 Sep 2026, Mountain Time): Trap-specific Bind and agent stop rule (review cleanup).

## Related specs

- [OEN-S06](s06-do-not-ship-html-only.md)
- [OEN-10](../web/10-one-blocking-stylesheet-variable-fonts.md)

