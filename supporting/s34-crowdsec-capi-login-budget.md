---
id: "OEN-S34"
title: "CrowdSec free-tier Central API login budget"
kind: "supporting"
status: "active"
edition: 3
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
  - abbr: SSH
    expansion: SSH
  - abbr: URL
    expansion: URL
---

# CrowdSec free-tier Central API login budget

## Context

Method behind [OEN-07](../networking/07-crowdsec-capi-403.md). Docker healthchecks are documented. Native systemd+collector is the unique stack. About **20 Central API logins / 50 minutes / source IP → HTTP 403 for about an hour** is an **observed free-tier** order of magnitude, not a substitute for CrowdSec’s current published limits.

## Topology

N/A — API

## Bind

Fill this table **before** any live change. Do **not** paste real values back into public notes.

| Placeholder | Operator fills | Class |
|-------------|----------------|-------|
| `<cloud-vps>` | Native CrowdSec host | Cloud VPS |
| `<user>` | SSH user if you inspect the host | Guest account |

## Method

Cache CAPI status. Nested SLI probes MUST skip live cscli. For 401 vs 403, reuse the **same** unauthenticated enroll request as [OEN-07](../networking/07-crowdsec-capi-403.md) — a dummy POST is not a different test.

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
# Same unauthenticated enroll POST as OEN-07 (no credentials)
curl -4 -sS -o /dev/null -w '%{http_code}\n' --max-time 15 -X POST https://api.crowdsec.net/v3/watchers/enroll
curl -6 -sS -o /dev/null -w '%{http_code}\n' --max-time 15 -X POST https://api.crowdsec.net/v3/watchers/enroll
```

1. **P1 — Stop the loop.**
   - **Action:** Disable repeating cscli capi status.
   - **Expected:** No further logins this window.
   - **On failure:** Retries keep the 403.
2. **P2 — Same enroll POST as OEN-07.**
   - **Action:** Unauthenticated enroll POST v4 vs v6 — copy [OEN-07](../networking/07-crowdsec-capi-403.md), do not invent a second dummy URL.
   - **Expected:** 401 = that source IP is accepted. 403 = that source IP is banned. That meaning comes from OEN-07, not from a different POST.
   - **On failure:** Do not put credentials on the dummy POST.
3. **P3 — Cache.**
   - **Action:** Health reads cache or logs. Far below ~20/50 min.
   - **Expected:** Collector quiet.
   - **On failure:** One cscli after hosts unpin if needed.

## Expected samples

Stdout of the copy-paste block (one code per family):

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

[CrowdSec documentation](https://docs.crowdsec.net/) covers Central API enrollment and health. This note is the native-host cache contract and the observed free-tier login budget.

