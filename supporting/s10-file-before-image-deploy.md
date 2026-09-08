---
id: OEN-S10
title: "file(1) before image deploy"
kind: supporting
status: active
edition: 1
date_published: 2026-09-08
author: Eugene Armstead
author_url: https://www.armsteadent.com/
canonical: https://eugenearmstead.github.io/overlay-and-edge-notes/supporting/s10-file-before-image-deploy.html
keywords:
  - images
  - file-command
backs:
  - OEN-10
  - OEN-11
backed_by: []
description: "Extension is not format. Map source to destination by actual type from file(1). Do not swap look-alike attachments."
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
  - abbr: nft
    expansion: nftables (Linux packet filter)
  - abbr: URL
    expansion: Uniform Resource Locator
  - abbr: UI
    expansion: user interface
  - abbr: JPEG
    expansion: Joint Photographic Experts Group image format
  - abbr: PNG
    expansion: Portable Network Graphics
---

# file(1) before image deploy

## Context

A `.png` can be JPEG data. Hero cutouts need alpha. Swapping look-alike attachments without `file` ships the wrong bytes.

## Topology

```text
source_path --file(1)--> actual type  -->  dest_path same type
Extension ≠ format. Do not swap look-alike attachments.
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

Map source → dest in writing before copy. Bytes verbatim unless the operator asks to re-process.

## Method

Run `file` on source and destination. Copy bytes verbatim unless the operator asks to re-process.

## Consequences

Hero transparency and photo JPEG stay in the right slots.

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
file <src-a> <src-b>
# After copy: file <dest>
```

1. **P1 — file sources.**
   - **Action:** `file` every source. Write source → dest (actual type).
   - **Expected:** Types known.
   - **On failure:** Do not trust the extension.
2. **P2 — Copy verbatim.**
   - **Action:** scp/rsync bytes. `file` the destination.
   - **Expected:** Destination type matches intent.
   - **On failure:** Do not rename to “fix” display without re-running file.
3. **P3 — HTML src=.**
   - **Action:** Grep live HTML src= against the filenames you meant.
   - **Expected:** src matches the typed files.
   - **On failure:** A JPEG served as PNG still needs the right name if the type is JPEG.

## Expected samples

```text
hero.png: JPEG image data   # trap: named png, is jpeg
```

## Verify

- file agrees on both ends.
- HTML src matches.
- ICMP / small ping success was **not** used as the pass criterion when this spec names TCP, SSH, or HTTPS.
- Bind table was filled by a human before any live `ip` / nft / iptables change.

## MUST NOT

- MUST NOT swap look-alike attachments without file.
- MUST NOT re-process unless asked.
- MUST NOT apply live network or firewall changes until Bind is filled by a human.
- MUST NOT claim a fix on ICMP ping alone when Verify names TCP, SSH, or HTTPS.
- MUST NOT publish hostnames, addresses, ULAs, or custom ports.

## Related specs

- [OEN-10](../web/10-one-blocking-stylesheet-variable-fonts.md)

## Prior art (Not novel)

file(1) is Unix 101. This note is extension≠format at deploy time.

