---
id: "OEN-07"
title: "CrowdSec Central API HTTP 403 from native health probes"
kind: "original"
status: "active"
edition: 2
date_published: "2026-09-08"
author: "Eugene Armstead"
author_url: "https://www.armsteadent.com/"
canonical: "https://eugenearmstead.github.io/overlay-and-edge-notes/networking/07-crowdsec-capi-403.html"
keywords:
  - "cscli capi 403"
  - "CrowdSec CAPI 403"
  - "CrowdSec Central API Forbidden"
  - "cscli capi status"
  - "CrowdSec healthcheck 403"
  - "systemd CrowdSec probe"
  - "CAPI IPv4 banned IPv6 401"
  - "dummy enroll POST 401 vs 403"
  - "CrowdSec Docker healthcheck"
  - "api.crowdsec.net 403"
  - "CAPI login budget"
  - "native CrowdSec not Docker"
  - "hosts pin CrowdSec IPv4"
backs:
  []
backed_by:
  - OEN-S34
description: "Native systemd health and fleet collectors that loop cscli capi status can 403 a Virtual Private Server IPv4 the same way Docker healthchecks do. Dummy enroll POST distinguishes banned IPv4 from a dead install."
terms:
  - abbr: AAAA
    expansion: DNS IPv6 address record
  - abbr: API
    expansion: application programming interface
  - abbr: CAPI
    expansion: CrowdSec Central API
  - abbr: CLI
    expansion: command-line interface
  - abbr: ControlPath
    expansion: OpenSSH multiplexing socket path option
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
  - abbr: JSON
    expansion: JavaScript Object Notation
  - abbr: NAT
    expansion: network address translation
  - abbr: nft
    expansion: nftables (Linux packet filter)
  - abbr: NIC
    expansion: network interface card
  - abbr: OEN
    expansion: Overlay and Edge Notes
  - abbr: POST
    expansion: HTTP method
  - abbr: SSH
    expansion: Secure Shell
  - abbr: systemd
    expansion: Linux service manager
  - abbr: UI
    expansion: user interface
  - abbr: VPN
    expansion: Virtual Private Network
  - abbr: VPS
    expansion: Virtual Private Server
---

# CrowdSec Central API HTTP 403 from native health probes

## Context

CrowdSec Central API (CAPI) HTTP **403 Forbidden** on a **native** (non-Docker) Virtual Private Server (VPS) looks like “CrowdSec is broken.” Docker `healthcheck: cscli capi status` is already documented (~20 logins / 50 minutes → about one hour ban). The unique add-on is **stacked systemd health plus a fleet collector** calling the same CLI every fifteen minutes (plus retries).

A leftover `/etc/hosts` **A-record pin** for `api.crowdsec.net` forces Go onto **banned IPv4** while IPv6 still returns **401** on a dummy enroll (IP accepted, auth expected to fail). Dummy unauthenticated enroll POST is a 401-versus-403 matrix **without** more `cscli`.

CAPI egress on this class of host is the **public NIC**, not the commercial tunnel. MUST NOT publish real public IPs. Generic: “VPS IPv4 banned, IPv6 still accepted.” Distinct from [OEN-21](21-shared-vpn-nat-crowdsec-ban.md) (shared VPN NAT house ban).

## Topology

N/A — API

## Bind

Fill this table **before** any live change. Do **not** paste real values back into public notes.

| Placeholder | Operator fills | Class |
|-------------|----------------|-------|
| `<user>` | SSH user | Guest account |
| `<cloud-vps>` | Cloud VPS under test | Cloud VPS |

## Formulas

Free-tier order of magnitude: about **20 CAPI logins / 50 minutes / source IP** then ~1 hour of HTTP 403. Cache status; dummy unauthenticated enroll POST for 401 vs 403 **without** more `cscli`.

## Decision

Operators MUST cache `cscli capi status` and MUST NOT loop it ([OEN-S34](../supporting/s34-crowdsec-capi-login-budget.md)).

Diagnose with one dummy enroll POST per address family. Remove A-record hosts pins. Prefer CAPI log lines and the Console UI over extra CLI logins.

## Consequences

- IPv6 CAPI keeps working while IPv4 cools down.
- Health probes stop re-banning the VPS.
- Console “enrolled” is not confused with a fleet dashboard 403.

## Agent stop rule

> MUST emit the dummy unauthenticated enroll POST per address family after `<cloud-vps>` is filled.
> MUST NOT loop `cscli capi status`.
> MUST NOT apply nft or iptables from this page.
> MUST NOT file a CrowdSec upstream bug from this page.

## Procedure


### Copy-paste commands (after Bind)

```bash
ssh -o ControlPath=none <user>@<cloud-vps> 'systemctl is-active crowdsec; grep -n crowdsec /etc/hosts || true'
# Dummy enroll POST (no credentials) v4 vs v6 — expect 401 (accepted path) vs 403 (banned family)
curl -4 -sS -o /dev/null -w '%{http_code}\n' --max-time 15 -X POST https://api.crowdsec.net/v2/watchers
curl -6 -sS -o /dev/null -w '%{http_code}\n' --max-time 15 -X POST https://api.crowdsec.net/v2/watchers
```

MUST NOT loop `cscli capi status`. Nested probes MUST read a cache ([OEN-S34](../supporting/s34-crowdsec-capi-login-budget.md)).

1. **P1 — Stop looping cscli.**
   - **Action:** Disable or rate-limit systemd health and fleet collector units that run `cscli capi status`. Do not run it “to check again.”
   - **Expected:** No further CAPI logins this hour.
   - **On failure:** If you already looped, wait the free-tier window (~1 h) before P3.
2. **P2 — Dummy enroll POST per family.**
   - **Action:** From `<cloud-vps>`, `curl -4` and `curl -6` POST `https://api.crowdsec.net/v3/watchers/enroll` with empty JSON, no credentials. If `/etc/hosts` has an A pin, resolve AAAA via a public resolver and `curl --resolve` for v6.
   - **Expected:** 401 = that source IP is accepted. 403 = that source IP is banned. Compare a second cloud host if you have one.
   - **On failure:** Do not put credentials on the dummy POST.
3. **P3 — Remove A-record pins.**
   - **Action:** If `/etc/hosts` pins `api.crowdsec.net` to IPv4, delete it. Confirm `getent` no longer returns `::ffff:` mapped v4 for the name.
   - **Expected:** Go/cscli can use IPv6. One `cscli capi status` after the pin is gone.
   - **On failure:** Do not restore the pin “to force IPv4.”
4. **P4 — Cache status; skip nested probes.**
   - **Action:** Health MUST read a cached CAPI result or log lines, not nested `cscli` every scrape.
   - **Expected:** Collector interval is far below ~20 / 50 min per IP.
   - **On failure:** If 403 remains on both families on two hosts, wait; do not probe harder.

## Expected samples

```text
# Banned IPv4 family
403
# Other family still accepted (example)
401
```

## Verify

- Dummy enroll: 401 on at least one family on this VPS.
- No api.crowdsec.net A pin in hosts.
- At most rare cscli capi status (cached).
- Console shows enrolled after one successful status.

## MUST NOT

- MUST NOT loop cscli capi status or console enroll.
- MUST NOT pin api.crowdsec.net to an A record.
- MUST NOT publish VPS public IPs or control-host names.
- MUST NOT treat a fleet dashboard “CAPI push FAIL” as proof of not enrolled without parsing console status.
- MUST NOT route CAPI “through the tunnel” as the first fix — default egress is often already the public NIC.
- MUST NOT publish hostnames, addresses, ULAs, or custom ports.

## Page changelog

- Edition 2 (8 Sep 2026, Mountain Time): Trap-specific Bind and agent stop rule (review cleanup).

## Related specs

- [OEN-S34 CrowdSec free-tier CAPI login budget](../supporting/s34-crowdsec-capi-login-budget.md)
- [OEN-21 Shared VPN NAT house ban](21-shared-vpn-nat-crowdsec-ban.md)
- [OEN-15 Split host vs overlay resolver](15-split-host-vs-overlay-resolver.md)

## Prior art (Not novel)

Docker healthcheck CAPI bans are documented. This spec’s claim is native systemd + fleet collector + hosts A-pin + 401/403 dummy matrix without more cscli.

