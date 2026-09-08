---
id: "OEN-S15"
title: "Router squashfs is always 100%; Save settings misses persistent overlay"
kind: "supporting"
status: "active"
edition: 2
date_published: "2026-09-08"
author: "Eugene Armstead"
author_url: "https://www.armsteadent.com/"
canonical: "https://eugenearmstead.github.io/overlay-and-edge-notes/supporting/s15-router-squashfs-jffs.html"
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
backed_by:
  []
description: "Router root squashfs reports 100% full; that is normal. Save settings .cfg does not include the persistent overlay scripts. Save JFFS separately. logread is OpenWrt — this firmware uses syslog files."
terms:
  - abbr: API
    expansion: application programming interface
  - abbr: JFFS
    expansion: journalled flash file system (router persistent overlay)
  - abbr: NVRAM
    expansion: non-volatile random-access memory
  - abbr: OEN
    expansion: Overlay and Edge Notes
  - abbr: USB
    expansion: Universal Serial Bus
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
| *(none)* | No packet-path Bind for this trap | Use the git host, origin, or API the operator already has |

## Formulas

Save JFFS/persistent overlay separately from NVRAM Save settings.

## Method

Do not “free root” on squashfs. Backup the persistent overlay separately from Save settings.

## Consequences

Scripts survive a settings save. Operators stop panicking at 100% squashfs.

## Agent stop rule

> MUST distinguish squashfs 100% from a missing persistent overlay after Bind is filled.
> MUST NOT “free root” on squashfs.
> MUST NOT apply netfilter from this page.

## Procedure


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

## MUST NOT

- MUST NOT publish real jffs paths as universal.
- MUST NOT wipe squashfs to “free space.”
- MUST NOT publish hostnames, addresses, ULAs, or custom ports.

## Page changelog

- Edition 2 (8 Sep 2026, Mountain Time): Trap-specific Bind and agent stop rule (review cleanup).

## Related specs

- [OEN-18](../networking/18-per-node-changelog-contract.md)
- [OEN-12](../networking/12-consumer-wg-phantom-bridge.md)

