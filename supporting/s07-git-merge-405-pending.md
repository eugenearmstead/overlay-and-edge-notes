---
id: OEN-S07
title: "Git merge 405 while mergeability is pending"
kind: supporting
status: active
edition: 1
date_published: 2026-09-08
author: Eugene Armstead
author_url: https://www.armsteadent.com/
canonical: https://eugenearmstead.github.io/overlay-and-edge-notes/supporting/s07-git-merge-405-pending.html
keywords:
  - gitlab
  - merge
  - 405
backs:
  - OEN-09
backed_by: []
description: "HTTP 405 on merge right after opening a merge request is usually mergeability still pending, not a dead token. Contrast with real 401."
terms:
  - abbr: OEN
    expansion: Overlay and Edge Notes
  - abbr: SSH
    expansion: Secure Shell
  - abbr: TCP
    expansion: Transmission Control Protocol
  - abbr: ICMP
    expansion: Internet Control Message Protocol
  - abbr: HTTP
    expansion: Hypertext Transfer Protocol
  - abbr: HTTPS
    expansion: Hypertext Transfer Protocol Secure
  - abbr: nft
    expansion: nftables (Linux packet filter)
  - abbr: URL
    expansion: Uniform Resource Locator
  - abbr: UI
    expansion: user interface
  - abbr: GitLab
    expansion: git hosting and merge-request service
  - abbr: PUT
    expansion: HTTP method
  - abbr: MR
    expansion: merge request
---

# Git merge 405 while mergeability is pending

## Context

Git hosting checks mergeability asynchronously. `PUT …/merge` often 405 until `merge_status` is `can_be_merged`. Auth failures are different: 401 / missing token — tell the operator immediately.

## Topology

```text
[create MR] --> Git host mergeability async
PUT merge  -->  405 until can_be_merged
401 is a dead token (tell the operator immediately)
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

405 while pending is timing. Poll; do not declare the bot cannot merge on a lone 405.

## Method

Poll until can_be_merged or a real blocker. MUST NOT tell the operator the bot “cannot merge” for a lone 405 until after that wait. MUST report 401 immediately.

## Consequences

Fewer false “token dead” pages. Real 401 still surfaces fast.

## Agent stop rule

> A coding agent MUST emit a **bound runbook** (placeholders replaced from Bind).
> MUST NOT apply live `ip rule`, nft, iptables, ip6tables, sysctl, `wg set`, daemon restart, or deploy until a **human** filled Bind.
> MUST NOT claim a fix on ICMP ping alone when Verify names TCP, SSH, or HTTPS.
> MUST NOT file an upstream bug from this page.
> MUST NOT publish real addresses, hostnames, or custom ports.

## Procedure

Placeholders only until Bind is filled: `<cloud-vps>`, `<lan-pi>`, `<overlay-peer>`, `<exit-node>`, `<wg-iface>`, `<gcp-nic>`, plus the Bind extras on this page.

### Copy-paste commands (after Bind)

```text
# Agent: poll merge_status until can_be_merged, retry 405. Distinct from HTTP 401.
```

1. **P1 — Classify 405 vs 401.**
   - **Action:** Read status. 401 → stop, tell operator. 405 → poll merge_status.
   - **Expected:** 401 never waited out.
   - **On failure:** Conflicts (cannot_be_merged) are not timing.
2. **P2 — Poll mergeability.**
   - **Action:** Retry merge up to ~90s while merge_status is checking.
   - **Expected:** Merges when can_be_merged.
   - **On failure:** If still 405 after the wait, leave the request URL; do not ask the operator to run git.
3. **P3 — Do not use the GitLab token against GitHub.**
   - **Action:** GitHub publish uses `gh auth`. GitLab PAT is not a GitHub PAT.
   - **Expected:** Correct host for the token.
   - **On failure:** Do not invent a GitHub token.

## Expected samples

```text
405 Method Not Allowed
# minutes later: merged
```

## Verify

- 401 reported immediately if it happened.
- 405 retried until mergeability or timeout.
- ICMP / small ping success was **not** used as the pass criterion when this spec names TCP, SSH, or HTTPS.
- Bind table was filled by a human before any live `ip` / nft / iptables change.

## MUST NOT

- MUST NOT hide 401 as timing.
- MUST NOT declare cannot-merge on the first 405.
- MUST NOT apply live network or firewall changes until Bind is filled by a human.
- MUST NOT claim a fix on ICMP ping alone when Verify names TCP, SSH, or HTTPS.
- MUST NOT publish hostnames, addresses, ULAs, or custom ports.

## Related specs

- [OEN-09](../web/09-git-merge-is-not-a-live-worker.md)

## Prior art (Not novel)

GitLab mergeability is documented. This note is 405-as-timing versus 401-as-dead-token.

