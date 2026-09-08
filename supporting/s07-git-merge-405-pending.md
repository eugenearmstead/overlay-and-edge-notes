---
id: "OEN-S07"
title: "Git merge 405 while mergeability is pending"
kind: "supporting"
status: "active"
edition: 2
date_published: "2026-09-08"
author: "Eugene Armstead"
author_url: "https://www.armsteadent.com/"
canonical: "https://eugenearmstead.github.io/overlay-and-edge-notes/supporting/s07-git-merge-405-pending.html"
keywords:
  - "git merge 405 pending"
  - "GitLab mergeability 405"
  - "405 Method Not Allowed merge"
  - "not a dead token 405"
  - "contrast real 401"
  - "merge_status can_be_merged"
  - "poll merge request 405"
  - "GitLab REST merge timing"
  - "unauthorized vs pending merge"
  - "MR 405 retry"
  - "token 401 tell operator"
  - "mergeability still checking"
backs:
  - OEN-09
backed_by:
  []
description: "HTTP 405 on merge right after opening a merge request is usually mergeability still pending, not a dead token. Contrast with real 401."
terms:
  - abbr: API
    expansion: application programming interface
  - abbr: GitLab
    expansion: git hosting and merge-request service
  - abbr: HTTP
    expansion: Hypertext Transfer Protocol
  - abbr: ICMP
    expansion: Internet Control Message Protocol
  - abbr: OEN
    expansion: Overlay and Edge Notes
  - abbr: PUT
    expansion: HTTP method
  - abbr: URL
    expansion: Uniform Resource Locator
---

# Git merge 405 while mergeability is pending

## Context

Git hosting checks mergeability asynchronously. `PUT …/merge` often 405 until `merge_status` is `can_be_merged`. Auth failures are different: 401 / missing token — tell the operator immediately.

## Topology

N/A — deploy

## Bind

Fill this table **before** any live change. Do **not** paste real values back into public notes.

| Placeholder | Operator fills | Class |
|-------------|----------------|-------|
| *(none)* | No packet-path Bind for this trap | Use the git host, origin, or API the operator already has |

## Formulas

405 while pending is timing. Poll; do not declare the bot cannot merge on a lone 405.

## Method

Poll until can_be_merged or a real blocker. MUST NOT tell the operator the bot “cannot merge” for a lone 405 until after that wait. MUST report 401 immediately.

## Consequences

Fewer false “token dead” pages. Real 401 still surfaces fast.

## Agent stop rule

> MUST classify HTTP 401 vs 405 before retrying merge.
> MUST NOT treat a lone 405 as a dead token; poll mergeability.
> MUST report 401 immediately.
> MUST NOT apply netfilter or claim an ICMP ping as a git-host fix.

## Procedure


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

## MUST NOT

- MUST NOT hide 401 as timing.
- MUST NOT declare cannot-merge on the first 405.
- MUST NOT publish hostnames, addresses, ULAs, or custom ports.

## Page changelog

- Edition 2 (8 Sep 2026, Mountain Time): Trap-specific Bind and agent stop rule (review cleanup).

## Related specs

- [OEN-09](../web/09-git-merge-is-not-a-live-worker.md)

