---
id: "OEN-S32"
title: "DNS leak-test green is not IPv6 data-plane green"
kind: "supporting"
status: "active"
edition: 2
date_published: "2026-09-08"
author: "Eugene Armstead"
author_url: "https://www.armsteadent.com/"
canonical: "https://eugenearmstead.github.io/overlay-and-edge-notes/supporting/s32-dns-leak-test-not-v6-dataplane.html"
keywords:
  - "DNS leak-test green not IPv6 data-plane"
  - "ipleak DNS ok TCP timeout"
  - "resolver name OK ::/0 dies"
  - "exit node IPv6 data path"
  - "DNS vs TCP different paths"
  - "leak test not enough"
  - "IPv6 HTTPS timeout exit"
  - "Headscale ::/0 TCP"
  - "verify IPv6 IP not DNS only"
  - "cellular DNS_PROBE vs IP"
  - "exit v6 forwarding"
  - "do not trust DNS-only leak test"
backs:
  - OEN-04
  - OEN-06
  - OEN-14
backed_by:
  []
description: "A leak-test resolver name can look OK while ::/0 TCP times out. DNS and IPv6 data are different paths."
terms:
  - abbr: CLI
    expansion: command-line interface
  - abbr: DNS
    expansion: Domain Name System
  - abbr: FORWARD
    expansion: netfilter/iptables forward chain
  - abbr: GCP
    expansion: Google Cloud Platform
  - abbr: HTTP
    expansion: Hypertext Transfer Protocol
  - abbr: HTTPS
    expansion: Hypertext Transfer Protocol Secure
  - abbr: IP
    expansion: Internet Protocol
  - abbr: IPv6
    expansion: Internet Protocol version 6
  - abbr: NAT
    expansion: network address translation
  - abbr: OEN
    expansion: Overlay and Edge Notes
  - abbr: PeerAPI
    expansion: overlay peer application-programming interface (exit DNS over HTTPS)
  - abbr: TCP
    expansion: Transmission Control Protocol
  - abbr: TCPMSS
    expansion: iptables/nft target that sets TCP Maximum Segment Size
  - abbr: URL
    expansion: Uniform Resource Locator
---

# DNS leak-test green is not IPv6 data-plane green

## Context

Wi-Fi “DNS looks OK”; HTTP/IP tests time out. Cellular DNS_PROBE_*. Backs exit TCPMSS and v6 return specs.

## Topology

```text
leak-test DNS green
curl -6 HTTPS timeout  -->  different path
```

## Bind

Fill this table **before** any live change. Do **not** paste real values back into public notes.

| Placeholder | Operator fills | Class |
|-------------|----------------|-------|
| `<overlay-impl>` | Overlay implementation class | `tailscale-compatible` or other — stop and translate CLI |

## Formulas

Always curl -6 a real HTTPS URL. Some leak-test sites 502 from cloud ranges.

## Method

Always `curl -6` a real HTTPS URL. MUST NOT declare the exit healthy on DNS color alone.

## Consequences

v6 FORWARD/NAT bugs get found. Leak-test 502 from some clouds is ignored ([OEN-17](../networking/17-gcp-overlay-exit.md)).

## Agent stop rule

> MUST `curl -6` a real HTTPS URL after Bind is filled.
> MUST NOT declare the exit healthy on DNS leak-test color alone.
> This spec does not apply if `<overlay-impl>` is not tailscale-compatible when using overlay CLI.
> MUST NOT apply netfilter from this page.

## Procedure

This spec does not apply if `<overlay-impl>` is not tailscale-compatible.

### Copy-paste commands (after Bind)

```bash
curl -6 --max-time 8 -sS -o /dev/null -w '%{http_code}\n' https://example.com
```

1. **P1 — DNS vs curl -6.**
   - **Action:** Leak-test DNS green? `curl -6 --max-time 8 https://example.com`.
   - **Expected:** DNS may pass; TCP fail.
   - **On failure:** That is this spec.
2. **P2 — Then OEN-04/06/14.**
   - **Action:** TCPMSS ([OEN-04](../networking/04-exit-tcpmss-after-ts-forward.md)), v6 return ([OEN-06](../networking/06-netfilter-off-v6-return.md)), or PeerAPI ([OEN-14](../networking/14-exit-dns-is-peerapi.md)).
   - **Expected:** Data plane fixed.
   - **On failure:** Do not stop at DNS.
3. **P3 — example.com not leak-test as hard canary.**
   - **Action:** Some leak-test sites 502 from GCP ranges.
   - **Expected:** example.com 200.
   - **On failure:** Do not flip accept-dns.

## Expected samples

```text
# DNS green; curl -6 hangs then 000
000
```

## Verify

- curl -6 used as the gate.
- DNS-only never called success.

## MUST NOT

- MUST NOT treat leak-test DNS green as IPv6 HTTP green.
- MUST NOT publish leak-test URLs as required canaries.
- MUST NOT publish hostnames, addresses, ULAs, or custom ports.

## Page changelog

- Edition 2 (8 Sep 2026, Mountain Time): Trap-specific Bind and agent stop rule (review cleanup).

## Related specs

- [OEN-04](../networking/04-exit-tcpmss-after-ts-forward.md)
- [OEN-06](../networking/06-netfilter-off-v6-return.md)
- [OEN-14](../networking/14-exit-dns-is-peerapi.md)

## Prior art (Not novel)

DNS vs data plane is textbook. This note is leak-test green specifically.

