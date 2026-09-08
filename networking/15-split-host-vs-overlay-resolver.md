---
id: "OEN-15"
title: "Split host vs overlay resolver views on the coordinator VPS"
kind: "original"
status: "active"
edition: 2
date_published: "2026-09-08"
author: "Eugene Armstead"
author_url: "https://www.armsteadent.com/"
canonical: "https://eugenearmstead.github.io/overlay-and-edge-notes/networking/15-split-host-vs-overlay-resolver.html"
keywords:
  - "split host vs overlay resolver"
  - "loopback Unbound tunnel down"
  - "tailnet DNS fails tunnel down"
  - "do not edit resolv.conf VPS"
  - "coordinator split-horizon DNS"
  - "host dig vs overlay dig"
  - "Unbound views commercial tunnel"
  - "Headscale nameserver view"
  - "127.0.0.1 still resolves"
  - "overlay NS timeout expected"
  - "chrony NTS host stack"
  - "VPS resolver preference script"
backs:
  []
backed_by:
  - OEN-S25
description: "The coordinator host resolver on loopback MUST keep working when the commercial tunnel is down. The overlay nameserver view MAY fail in that state if it forwards through the tunnel."
terms:
  - abbr: CAPI
    expansion: CrowdSec Central API
  - abbr: chrony
    expansion: NTP/NTS time daemon
  - abbr: ControlPath
    expansion: OpenSSH multiplexing socket path option
  - abbr: CrowdSec
    expansion: open-source IDS/IPS with a Central API
  - abbr: DNS
    expansion: Domain Name System
  - abbr: dnsmasq
    expansion: lightweight DNS forwarder and DHCP server
  - abbr: NS
    expansion: DNS nameserver (or overlay nameserver view)
  - abbr: NTS
    expansion: Network Time Security
  - abbr: OEN
    expansion: Overlay and Edge Notes
  - abbr: PeerAPI
    expansion: overlay peer application-programming interface (exit DNS over HTTPS)
  - abbr: SERVFAIL
    expansion: DNS response code meaning the server failed
  - abbr: SSH
    expansion: Secure Shell
  - abbr: Unbound
    expansion: validating recursive DNS resolver
  - abbr: VPS
    expansion: Virtual Private Server
---

# Split host vs overlay resolver views on the coordinator VPS

## Context

On the coordination Virtual Private Server (VPS), two resolver views exist. The **host** view (`127.0.0.1`) must keep resolving if the commercial WireGuard tunnel drops — or the box cannot update, enroll, or reach CrowdSec. The **overlay** nameserver view MAY fail in that state if it forwards through the tunnel. That is expected.

Operators who hand-edit `resolv.conf` fight the tunnel up/down scripts and lose the split. Network Time Security (NTS) on this host may need a newer chrony than the distro ([OEN-S25](../supporting/s25-chrony-nts-address-family.md)).

## Topology

```text
[<cloud-vps>]
    host view  127.0.0.1 Unbound/dnsmasq   MUST work with commercial tunnel DOWN
    overlay NS view                       MAY fail while tunnel is down (expected)
Tunnel up/down scripts flip resolv preference. Do not hand-edit resolv.conf.
```

## Bind

Fill this table **before** any live change. Do **not** paste real values back into public notes.

| Placeholder | Operator fills | Class |
|-------------|----------------|-------|
| `<user>` | SSH user | Guest account |
| `<cloud-vps>` | Cloud VPS under test | Cloud VPS |
| `<wg-iface>` | Commercial WireGuard iface | Router or VPS client |
| `<overlay-ns>` | Overlay resolver view | View or namespace |

## Formulas

NTS/chrony is host stack, not PeerAPI ([OEN-S25](../supporting/s25-chrony-nts-address-family.md)).

## Decision

Host `dig @127.0.0.1` MUST succeed after a tunnel stop. Overlay-view dig MAY time out until the tunnel returns. MUST NOT hand-edit `resolv.conf` on the VPS. Tunnel up/down scripts flip preference.

## Consequences

- The VPS remains administrable when the tunnel is down.
- Overlay clients see the intended failure if they depend on tunnel-forwarded DNS.
- No more “fix DNS” by freezing resolv.conf.

## Agent stop rule

> MUST emit bound host vs overlay resolver lookups after Bind is filled.
> MUST NOT treat coordinator Unbound failure as overlay PeerAPI failure (or the reverse).
> MUST NOT apply netfilter from this page.

## Procedure


### Copy-paste commands (after Bind)

```bash
ssh -o ControlPath=none <user>@<cloud-vps> 'dig +time=2 @127.0.0.1 example.com; ip link show <wg-iface>'
# After a controlled tunnel stop (human-approved): host dig still works; overlay NS MAY time out.
# Start tunnel; overlay NS works again.
```

1. **P1 — Record both views while the tunnel is up.**
   - **Action:** On `<cloud-vps>`: `dig @127.0.0.1 example.com` and `dig @<overlay-ns> example.com` with short timeouts.
   - **Expected:** Both succeed while `<wg-iface>` is up.
   - **On failure:** If host view already fails, fix host Unbound/dnsmasq before touching the tunnel.
2. **P2 — Stop the tunnel; retest.**
   - **Action:** Stop `<wg-iface>` (or the WireGuard unit). Repeat both digs. Do not edit resolv.conf.
   - **Expected:** Host dig still works. Overlay-ns dig times out or SERVFAIL if it forwarded through the tunnel.
   - **On failure:** If host dig dies, the host view was secretly tunnel-dependent — that is the bug to fix.
3. **P3 — Start the tunnel; retest.**
   - **Action:** Bring `<wg-iface>` up. Overlay-ns dig works again. Host dig still works.
   - **Expected:** Split restored.
   - **On failure:** If overlay view stays dead, the forwarder did not recover — check Unbound, not resolv.conf.
4. **P4 — Confirm no hand-edited resolv.conf.**
   - **Action:** `lsattr` / package scripts / wg-quick PostUp. resolv.conf SHOULD be managed, not a frozen manual file.
   - **Expected:** No operator comment “I set nameserver 1.1.1.1 to fix it.”
   - **On failure:** Revert manual edits; restore the scripted split.

## Expected samples

```text
# Host view still answers with tunnel down
example.com.  300  IN  A  ...
```

## Verify

- Tunnel down: host dig works; overlay-ns MAY fail.
- Tunnel up: both work.
- resolv.conf is not a hand-frozen file.
- chrony NTS still steps if that is in scope ([OEN-S25](../supporting/s25-chrony-nts-address-family.md)).

## MUST NOT

- MUST NOT hand-edit resolv.conf on the coordinator VPS as a DNS fix.
- MUST NOT require overlay-ns to work while the commercial tunnel is down.
- MUST NOT publish the overlay nameserver address.
- MUST NOT restart coordination serve to “refresh DNS” ([OEN-14](14-exit-dns-is-peerapi.md)).
- MUST NOT publish hostnames, addresses, ULAs, or custom ports.

## Page changelog

- Edition 2 (8 Sep 2026, Mountain Time): Trap-specific Bind and agent stop rule (review cleanup).

## Related specs

- [OEN-14 Exit DNS is PeerAPI](14-exit-dns-is-peerapi.md)
- [OEN-07 CrowdSec CAPI 403](07-crowdsec-capi-403.md)
- [OEN-S25 chrony NTS address-family](../supporting/s25-chrony-nts-address-family.md)
- [OEN-16 Commercial WireGuard endpoint rotation](16-commercial-wg-endpoint-rotation.md)

