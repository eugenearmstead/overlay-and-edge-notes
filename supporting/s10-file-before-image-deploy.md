---
id: "OEN-S10"
title: "file(1) before image deploy"
kind: "supporting"
status: "active"
edition: 2
date_published: "2026-09-08"
author: "Eugene Armstead"
author_url: "https://www.armsteadent.com/"
canonical: "https://eugenearmstead.github.io/overlay-and-edge-notes/supporting/s10-file-before-image-deploy.html"
keywords:
  - "file before image deploy"
  - "extension is not format"
  - "PNG is JPEG data"
  - "do not swap look-alike attachments"
  - "file(1) source destination"
  - "map actual type before scp"
  - "hero photo vs cutout PNG"
  - "identify alpha channel"
  - "wrong image filename deploy"
  - "file command MIME"
  - "static site image mixup"
  - "verify file after upload"
backs:
  - OEN-10
  - OEN-11
backed_by:
  []
description: "Extension is not format. Map source to destination by actual type from file(1). Do not swap look-alike attachments."
terms:
  - abbr: HTML
    expansion: HyperText Markup Language
  - abbr: JPEG
    expansion: Joint Photographic Experts Group image format
  - abbr: OEN
    expansion: Overlay and Edge Notes
  - abbr: PNG
    expansion: Portable Network Graphics
---

# file(1) before image deploy

## Context

A `.png` can be JPEG data. Hero cutouts need alpha. Swapping look-alike attachments without `file` ships the wrong bytes.

## Topology

N/A — deploy

## Bind

Fill this table **before** any live change. Do **not** paste real values back into public notes.

| Placeholder | Operator fills | Class |
|-------------|----------------|-------|
| `<src-a>` | First image source | Path |
| `<src-b>` | Second image source | Path |
| `<dest>` | Deploy destination path | Path |

## Formulas

Map source → dest in writing before copy. Bytes verbatim unless the operator asks to re-process.

## Method

Run `file` on source and destination. Copy bytes verbatim unless the operator asks to re-process.

## Consequences

Hero transparency and photo JPEG stay in the right slots.

## Agent stop rule

> MUST run `file` on `<src-a>` / `<src-b>` / `<dest>` after Bind is filled.
> MUST NOT swap filenames to “fix” display without confirming format.
> MUST NOT apply netfilter from this page.

## Procedure


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

## MUST NOT

- MUST NOT swap look-alike attachments without file.
- MUST NOT re-process unless asked.
- MUST NOT publish hostnames, addresses, ULAs, or custom ports.

## Page changelog

- Edition 2 (8 Sep 2026, Mountain Time): Trap-specific Bind and agent stop rule (review cleanup).

## Related specs

- [OEN-10](../web/10-one-blocking-stylesheet-variable-fonts.md)

