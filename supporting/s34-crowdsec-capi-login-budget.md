---
id: "OEN-S34"
title: "CrowdSec free-tier Central API login budget"
kind: "supporting"
status: "active"
edition: 2
date_published: "2026-09-08"
author: "Eugene Armstead"
author_url: "https://www.armsteadent.com/"
canonical: "https://eugenearmstead.github.io/overlay-and-edge-notes/supporting/s34-crowdsec-capi-login-budget.html"
keywords:
  - "CrowdSec CAPI login budget"
  - "20 CAPI logins 50 minutes"
  - "cscli capi 403 one hour"
  - "cache cscli capi status"
  - "do not loop capi status"
  - "free-tier CAPI 403"
  - "CrowdSec healthcheck budget"
  - "api.crowdsec.net rate limit"
  - "Docker healthcheck CAPI ban"
  - "native probe same budget"
  - "HTTP 403 CAPI login"
  - "skip nested CAPI SLI"
backs:
  - OEN-07
backed_by:
  []
description: "CrowdSec free-tier about 20 CAPI logins per 50 minutes per source IP yields HTTP 403 for about an hour. Cache cscli capi status; do not loop it."
terms:
  - abbr: API
    expansion: application programming interface
  - abbr: CAPI
    expansion: CrowdSec Central API
  - abbr: CrowdSec
    expansion: open-source IDS/IPS with a Central API
  - abbr: HTTP
    expansion: Hypertext Transfer Protocol
  - abbr: IP
    expansion: Internet Protocol
  - abbr: IPv4
    expansion: Internet Protocol version 4
  - abbr: IPv6
    expansion: Internet Protocol version 6
  - abbr: nft
    expansion: nftables (Linux packet filter)
  - abbr: OEN
    expansion: Overlay and Edge Notes
  - abbr: POST
    expansion: HTTP method
  - abbr: SLI
    expansion: service level indicator
  - abbr: systemd
    expansion: Linux service manager
  - abbr: VPS
    expansion: Virtual Private Server
---

# CrowdSec free-tier Central API login budget

## Context

Method behind [OEN-07](../networking/07-crowdsec-capi-403.md). Docker healthchecks are documented; native systemd+collector is the unique stack.

## Topology

N/A — API

## Bind

Fill this table **before** any live change. Do **not** paste real values back into public notes.

| Placeholder | Operator fills | Class |
|-------------|----------------|-------|
| *(none)* | No packet-path Bind for this trap | Use the git host, origin, or API the operator already has |

## Method

Cache CAPI status. Nested SLI probes MUST skip live cscli. Dummy enroll POST for 401 vs 403 without more logins.

## Consequences

The VPS IPv4 can cool down. IPv6 may still be 401.

## Agent stop rule

> MUST emit the dummy unauthenticated enroll POST (v4 and v6) from [OEN-07](../networking/07-crowdsec-capi-403.md) — not extra `cscli` logins.
> MUST NOT loop `cscli capi status`.
> MUST NOT apply nft, iptables, or sysctl from this page.
> MUST NOT file a CrowdSec upstream bug from this page.

## Procedure


### Copy-paste commands (after Bind)

```bash
curl -4 -sS -o /dev/null -w '%{http_code}\n' --max-time 15 -X POST https://api.crowdsec.net/v2/watchers
curl -6 -sS -o /dev/null -w '%{http_code}\n' --max-time 15 -X POST https://api.crowdsec.net/v2/watchers
```

1. **P1 — Stop the loop.**
   - **Action:** Disable repeating cscli capi status.
   - **Expected:** No further logins this window.
   - **On failure:** Retries keep the 403.
2. **P2 — Dummy POST matrix.**
   - **Action:** Unauthenticated enroll POST v4 vs v6 ([OEN-07](../networking/07-crowdsec-capi-403.md)).
   - **Expected:** 401 vs 403 per family.
   - **On failure:** No credentials.
3. **P3 — Cache.**
   - **Action:** Health reads cache or logs. Far below ~20/50 min.
   - **Expected:** Collector quiet.
   - **On failure:** One cscli after hosts unpin if needed.

## Expected samples

```text
403
401
```

## Verify

- No looping cscli.
- Budget respected.
- Dummy matrix used instead of more logins.

## MUST NOT

- MUST NOT loop cscli capi status.
- MUST NOT publish VPS IPs.
- MUST NOT publish hostnames, addresses, ULAs, or custom ports.

## Page changelog

- Edition 2 (8 Sep 2026, Mountain Time): Trap-specific Bind and agent stop rule (review cleanup).

## Related specs

- [OEN-07](../networking/07-crowdsec-capi-403.md)

## Prior art (Not novel)

CrowdSec documents the free-tier login budget. This note is cache-and-dummy-POST as the native-host contract.

