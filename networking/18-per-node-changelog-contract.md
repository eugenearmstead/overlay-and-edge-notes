---
id: OEN-18
title: Per-node changelog contract (repo + hashed on-device copy)
kind: original
status: active
edition: 2
date_published: 2026-09-07
author: Eugene Armstead
author_url: https://www.armsteadent.com/
canonical: https://eugenearmstead.github.io/overlay-and-edge-notes/networking/18-per-node-changelog-contract.html
keywords:
  - "per-node changelog hash mismatch"
  - "on-device CHANGELOG sync"
  - "ops repo canonical changelog"
  - "changelog path class by node"
  - "sha256sum changelog verify"
  - "do not invent fake precision"
  - "timezone labeled not UTC prose"
  - "router jffs vs VPS vs Pi paths"
  - "same session changelog"
  - "homelab changelog contract"
  - "hashed on-device copy"
  - "Change Paths Verify entry"
backs: []
backed_by: []
description: "Per-node changelog hash mismatch: the ops-repo file is canonical; sync a hashed on-device copy the same session, with path class by node type."
terms:
  - abbr: OEN
    expansion: Overlay and Edge Notes
  - abbr: MSS
    expansion: Maximum Segment Size
  - abbr: SSH
    expansion: Secure Shell
  - abbr: UTC
    expansion: Coordinated Universal Time
  - abbr: TZ
    expansion: timezone abbreviation in a changelog heading
  - abbr: VPS
    expansion: Virtual Private Server
  - abbr: LAN
    expansion: Local Area Network
  - abbr: Pi
    expansion: single-board computer (Raspberry Pi class)
  - abbr: ControlPath
    expansion: OpenSSH multiplexing socket path option
  - abbr: TZ
    expansion: timezone abbreviation in a changelog heading
  - abbr: WG
    expansion: WireGuard
  - abbr: WireGuard
    expansion: UDP-based VPN protocol
  - abbr: URL
    expansion: Uniform Resource Locator
  - abbr: IP
    expansion: Internet Protocol
  - abbr: ControlPath
    expansion: OpenSSH multiplexing socket path option
---

# Per-node changelog contract (repo + hashed on-device copy)

## Context

Fleet changes (Maximum Segment Size (MSS), sysctl, tunnel client, exit advertise, Secure Shell (SSH) doors) are easy to lose in chat transcripts. A **per-node changelog** is the “at a glance” ops surface: what changed, on which class of device, how to verify.

The contract is the **pattern**, not anyone’s private log bodies.

Two copies:

1. **Repo file is canonical.** One Markdown file per node (or per node class if you truly have cattle). Newest entry first.
2. **On-device copy** exists so a future operator who is already on the box can read history without the laptop. Paths **differ by class**:

| Node class | On-device copy (class, not an inventory) |
|------------|------------------------------------------|
| Consumer router | Firmware persistent overlay such as a **jffs-class** path under the router’s writable store |
| Cloud Virtual Private Server (VPS) | A project tree under **`/opt`**, for example `/opt/<project>/docs/CHANGELOG.md` |
| Local Area Network (LAN) Pi | Distro-style **`/usr/local/share/<project>/CHANGELOG.md`** |
| Workstation | **User-writable home**, for example `~/.local/share/<project>/CHANGELOG.md` — not a sudo path assumed to exist |

Agents MUST NOT claim an on-device path exists without `ls` and a **hash match** against the repo file. Workstations in particular often **lack** a sudo tree such as `/usr/local/share/<project>` when passwordless sudo is off. Canonical remains the repo file.

## Topology

```text
[private ops repo]  <repo-changelog>     CANONICAL
        |
        |  same session as the change
        v
[on-device copy]    <on-device-changelog>   class path by node type
        |
        +-- ls + sha256sum MUST match
```

## Bind

| Placeholder | Operator fills | Class |
|-------------|----------------|-------|
| `<repo-changelog>` | Canonical Markdown in the private ops repo | Path class |
| `<on-device-changelog>` | On-device copy | Path class from the table |
| `<node>` | Role (cloud VPS, LAN Pi, router, workstation) | Role, not hostname |
| `<user>` | Account used to copy | Guest or workstation user |

## Parameters

Each entry MUST include Date + labeled timezone, Change, Paths, Verify. No secrets. Agents MUST NOT invent fake precision.

## Decision

Same session as the change:

1. Append to the repo changelog (newest first).
2. Sync the on-device copy for that node class.
3. Prove the copy with `ls` + `sha256sum` (or equivalent) vs the repo file.

Each entry MUST include:

- **Date** and a **labeled timezone** in operator prose (not unlabeled Coordinated Universal Time (UTC)).
- **Change** — one or two sentences.
- **Paths** — what was edited.
- **Verify** — one concrete check.

No secrets, tokens, or passwords. Agents MUST NOT invent fake precision: if the time of day is unknown, write a date with `time approximate` or `~YYYY-MM-DD`.

## Consequences

- Future sessions do not rediscover last month’s MSS clamp.
- On-device copies cannot silently diverge if the hash check is required.
- Public discussion of the **pattern** does not require publishing anyone’s hostnames or real paths.

## Agent stop rule

> MUST emit the class path table with `<repo-changelog>` filled.  
> MUST NOT claim an on-device path exists without `ls` + `sha256sum`.  
> MUST NOT copy secrets into the log.

## Procedure

Placeholders: `<node>` is a role, not a hostname. `<repo-changelog>` is the canonical Markdown file. `<on-device-changelog>` is the class path from the table.

1. **P1 — Edit the repo file first.**
   - **Action:** Open `<repo-changelog>`. Prepend a heading `## YYYY-MM-DD HH:MM TZ — short title` and the Change / Paths / Verify bullets.
   - **Expected:** Newest entry is at the top. Timezone is labeled (examples: Mountain Time for home-LAN nodes, Pacific Time for a US-West VPS).
   - **On failure:** Do not sync a stale on-device file. Fix the repo entry first.

2. **P2 — Choose the on-device class path without guessing.**
   - **Action:** For this node class, pick the path class in the table. If unsure whether the directory exists, `ls` the parent. Do not invent `/usr/local/share/<project>` on a workstation that has no sudo.
   - **Expected:** A writable path that this node can actually update.
   - **On failure:** Skip on-device sync and record in the repo entry that only the canonical file was updated, with the reason.

3. **P3 — Sync bytes.**
   - **Action:** Copy `<repo-changelog>` to `<on-device-changelog>` (install, scp, or a small sync helper). Preserve mode so a non-root workstation copy stays user-owned.
   - **Expected:** File exists at the destination.
   - **On failure:** Do not claim “synced.” Leave the repo entry noting the copy failed.

4. **P4 — Hash both sides.**
   - **Action:**

     ```bash
     sha256sum <repo-changelog>
     ssh -o ControlPath=none <user>@<node> 'sha256sum <on-device-changelog>'
     ```

   - **Expected:** Digests match.
   - **On failure:** Recopy. Never report success on a mismatched hash.

5. **P5 — Redact secrets before they land.**
   - **Action:** Read the new bullets. Strip tokens, passwords, private URLs, and inventory.
   - **Expected:** A stranger could read the entry and learn the **class** of change, not the lab map.
   - **On failure:** Edit the repo file and resync.

## Verify

- Repo file has a newest-first entry with date, timezone label, Change, Paths, Verify.
- `ls` shows the on-device file **or** the repo explicitly says the copy was skipped.
- `sha256sum` matches when a copy was made.
- No secrets in the text.

## Expected samples

```text
<hash>  docs/changelogs/<role>/CHANGELOG.md
<hash>  /opt/<project>/docs/CHANGELOG.md
# hashes equal
```

## MUST NOT

- MUST NOT claim a path exists without `ls` + hash vs repo.
- MUST NOT write unlabeled UTC in operator-facing changelog prose.
- MUST NOT invent a precise clock time when it was not recorded.
- MUST NOT put secrets, overlay addresses, or custom admin ports in the log.
- MUST NOT publish real on-device paths from a private fleet as if they were universal; use the **class** table.

## Related specs

- [OEN-01 Overlay SSH byte cliff](01-overlay-ssh-byte-cliff.md) — MSS and underlay changes belong in the node log
- [OEN-16 Commercial WireGuard endpoint rotation](16-commercial-wg-endpoint-rotation.md)
- [OEN-17 Google Cloud overlay exit](17-gcp-overlay-exit.md)

## Prior art (Not novel)

Dated changelogs and “docs next to the code” are ordinary. This spec’s claim is the **two-copy contract** with class-specific on-device paths, mandatory hash, timezone labeling, and a ban on fake precision.
