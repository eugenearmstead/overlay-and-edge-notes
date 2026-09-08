---
id: "OEN-S16"
title: "Never nft flush / never start stock nftables.service"
kind: "supporting"
status: "active"
edition: 2
date_published: "2026-09-08"
author: "Eugene Armstead"
author_url: "https://www.armsteadent.com/"
canonical: "https://eugenearmstead.github.io/overlay-and-edge-notes/supporting/s16-never-nft-flush.html"
keywords:
  - "never nft flush ruleset"
  - "never start nftables.service"
  - "UFW CrowdSec custom tables"
  - "tunnel predown named tables only"
  - "nft flush wipes exit rules"
  - "stock nftables.service conflict"
  - "ip6tables MASQUERADE custom"
  - "do not flush whole ruleset"
  - "nft delete table named"
  - "UFW plus nft custom"
  - "CrowdSec nft coexistence"
  - "WireGuard predown nft"
backs:
  - OEN-06
  - OEN-17
backed_by:
  []
description: "Never nft flush ruleset and never start stock nftables.service on a host that also runs UFW, CrowdSec, and custom exit tables. Tunnel predown MUST delete only named custom tables."
terms:
  - abbr: CrowdSec
    expansion: open-source IDS/IPS with a Central API
  - abbr: HTTPS
    expansion: Hypertext Transfer Protocol Secure
  - abbr: ICMP
    expansion: Internet Control Message Protocol
  - abbr: NAT
    expansion: network address translation
  - abbr: nft
    expansion: nftables (Linux packet filter)
  - abbr: nftables
    expansion: Linux packet-filter framework
  - abbr: OEN
    expansion: Overlay and Edge Notes
  - abbr: SSH
    expansion: Secure Shell
  - abbr: TCP
    expansion: Transmission Control Protocol
  - abbr: UFW
    expansion: Uncomplicated Firewall
---

# Never nft flush / never start stock nftables.service

## Context

A flush wipes UFW + CrowdSec + exit NAT together. Predown scripts that flush “to be clean” take down the house.

## Topology

```text
Host runs UFW + CrowdSec + custom exit tables
nft flush ruleset  OR  starting stock nftables.service  -->  wipes everything
Tunnel predown MUST delete only named custom tables
```

## Bind

Fill this table **before** any live change. Do **not** paste real values back into public notes.

| Placeholder | Operator fills | Class |
|-------------|----------------|-------|
| `<custom-table>` | Named nft table this host owns | Table name |
| `<custom>` | Operator fills from this procedure | Local |

## Formulas

Never nft flush on a mixed UFW/CrowdSec/exit host.

## Method

Delete only named custom tables on tunnel down. MUST NOT start distro nftables.service beside UFW.

## Consequences

Exit and UFW rules survive tunnel hops.

## Agent stop rule

> MUST emit bound `nft list` / delete-named-table commands after Bind is filled.
> MUST NOT `nft flush` or start stock nftables.service on a mixed UFW/CrowdSec/exit host.
> MUST NOT claim ICMP ping as a firewall-restore fix.
> MUST NOT file an upstream nftables bug from this page.

## Procedure


### Copy-paste commands (after Bind)

```bash
nft list tables
systemctl is-enabled nftables.service || true
# Predown: nft delete table inet <custom-table>   — not flush ruleset
```

1. **P1 — List tables.**
   - **Action:** nft list tables. Note UFW, CrowdSec, custom exit.
   - **Expected:** Several tables coexist.
   - **On failure:** A single flush would drop all.
2. **P2 — Predown deletes named tables only.**
   - **Action:** Tunnel predown: `nft delete table inet <custom>` only.
   - **Expected:** UFW/CrowdSec remain.
   - **On failure:** If someone added flush ruleset, remove it.
3. **P3 — Distro nftables.service stays off.**
   - **Action:** systemctl is-enabled nftables. Must be off if UFW owns the host.
   - **Expected:** No dual policy.
   - **On failure:** Do not enable it to “manage v6.”

## Expected samples

```text
# After accidental flush: UFW empty, exit NAT gone
```

## Verify

- No flush in predown.
- nftables.service disabled.
- UFW and CrowdSec tables persist across tunnel restart.
- ICMP / small ping success was **not** used as the pass criterion when this spec names TCP, SSH, or HTTPS.
- Bind table was filled by a human before any live `ip` / nft / iptables change.

## MUST NOT

- MUST NOT nft flush ruleset on this host class.
- MUST NOT enable stock nftables.service beside UFW+CrowdSec.
- MUST NOT apply live network or firewall changes until Bind is filled by a human.
- MUST NOT claim a fix on ICMP ping alone when Verify names TCP, SSH, or HTTPS.
- MUST NOT publish hostnames, addresses, ULAs, or custom ports.

## Page changelog

- Edition 2 (8 Sep 2026, Mountain Time): Trap-specific Bind and agent stop rule (review cleanup).

## Related specs

- [OEN-06](../networking/06-netfilter-off-v6-return.md)
- [OEN-07](../networking/07-crowdsec-capi-403.md)

## Prior art (Not novel)

nft flush is an obvious footgun. This note is the coexistence with UFW, CrowdSec, and exit tables.

