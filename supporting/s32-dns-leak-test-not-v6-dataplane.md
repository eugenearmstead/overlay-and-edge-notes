---
id: OEN-S32
title: "DNS leak-test green is not IPv6 data-plane green"
kind: supporting
status: active
edition: 1
date_published: 2026-09-08
author: Eugene Armstead
author_url: https://www.armsteadent.com/
canonical: https://eugenearmstead.github.io/overlay-and-edge-notes/supporting/s32-dns-leak-test-not-v6-dataplane.html
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
backed_by: []
description: "A leak-test resolver name can look OK while ::/0 TCP times out. DNS and IPv6 data are different paths."
terms:
  - abbr: OEN
    expansion: Overlay and Edge Notes
  - abbr: SSH
    expansion: Secure Shell
  - abbr: LAN
    expansion: Local Area Network
  - abbr: WAN
    expansion: Wide Area Network
  - abbr: TCP
    expansion: Transmission Control Protocol
  - abbr: TCPMSS
    expansion: iptables/nft target that sets TCP Maximum Segment Size
  - abbr: MTU
    expansion: Maximum Transmission Unit
  - abbr: ICMP
    expansion: Internet Control Message Protocol
  - abbr: HTTP
    expansion: Hypertext Transfer Protocol
  - abbr: HTTPS
    expansion: Hypertext Transfer Protocol Secure
  - abbr: IP
    expansion: Internet Protocol
  - abbr: IPv6
    expansion: Internet Protocol version 6
  - abbr: DNS
    expansion: Domain Name System
  - abbr: NAT
    expansion: network address translation
  - abbr: GCP
    expansion: Google Cloud Platform
  - abbr: VM
    expansion: virtual machine
  - abbr: NIC
    expansion: network interface card
  - abbr: PeerAPI
    expansion: overlay peer application-programming interface (exit DNS over HTTPS)
  - abbr: nft
    expansion: nftables (Linux packet filter)
  - abbr: FORWARD
    expansion: netfilter/iptables forward chain
  - abbr: URL
    expansion: Uniform Resource Locator
  - abbr: Pi
    expansion: single-board computer (Raspberry Pi class)
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
| `<exit-node>` | Overlay exit node | Cloud VM or LAN Pi used as exit |
| `<overlay-peer>` | Soak client (**not** the agent workstation) | LAN Pi |
| `<user>` | SSH user | Guest |
| `<overlay-tun>` | Overlay tun on the exit | Iface |
| `<gcp-nic>` | Public NIC on a Google Cloud guest | Iface; omit on non-GCP exits |
| `<wan-iface>` | WAN / public NIC | Iface |
| `<mss4>` / `<mss6>` | Computed from underlay or overlay tun MTU | Formulas |


## Formulas

Always curl -6 a real HTTPS URL. Some leak-test sites 502 from cloud ranges.

## Method

Always `curl -6` a real HTTPS URL. MUST NOT declare the exit healthy on DNS color alone.

## Consequences

v6 FORWARD/NAT bugs get found. Leak-test 502 from some clouds is ignored ([OEN-17](../networking/17-gcp-overlay-exit.md)).

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
- ICMP / small ping success was **not** used as the pass criterion when this spec names TCP, SSH, or HTTPS.
- Bind table was filled by a human before any live `ip` / nft / iptables change.

## MUST NOT

- MUST NOT treat leak-test DNS green as IPv6 HTTP green.
- MUST NOT publish leak-test URLs as required canaries.
- MUST NOT apply live network or firewall changes until Bind is filled by a human.
- MUST NOT claim a fix on ICMP ping alone when Verify names TCP, SSH, or HTTPS.
- MUST NOT publish hostnames, addresses, ULAs, or custom ports.

## Related specs

- [OEN-04](../networking/04-exit-tcpmss-after-ts-forward.md)
- [OEN-06](../networking/06-netfilter-off-v6-return.md)
- [OEN-14](../networking/14-exit-dns-is-peerapi.md)

## Prior art (Not novel)

DNS vs data plane is textbook. This note is leak-test green specifically.

