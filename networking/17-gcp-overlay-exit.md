---
id: "OEN-17"
title: "Google Cloud overlay exit (IP forwarding, listen port, Identity-Aware Proxy)"
kind: "original"
status: "active"
edition: 2
date_published: "2026-09-07"
author: "Eugene Armstead"
author_url: "https://www.armsteadent.com/"
canonical: "https://eugenearmstead.github.io/overlay-and-edge-notes/networking/17-gcp-overlay-exit.html"
keywords:
  - "canIpForward exit node"
  - "Google Cloud overlay exit"
  - "Identity-Aware Proxy break-glass"
  - "advertise 0.0.0.0/0 and ::/0"
  - "overlay PORT 41641"
  - "Android hides exit without ::/0"
  - "ip_forward GCE"
  - "do not double ip6tables MASQUERADE"
  - "rp_filter=2 GCP NIC"
  - "tailscale ssh KEX fail GCE"
  - "accept-dns vs PeerAPI"
  - "VPC UDP 41641 PORT=0"
  - "Headscale GCP exit"
backs:
  []
backed_by:
  []
description: "A Google Cloud virtual machine can advertise an overlay exit only with IP forwarding, both default routes, a fixed overlay UDP listen port, scoped network address translation, and Identity-Aware Proxy as break-glass — not as the daily door."
terms:
  - abbr: OEN
    expansion: Overlay and Edge Notes
  - abbr: GCP
    expansion: Google Cloud Platform
  - abbr: GCE
    expansion: Google Compute Engine
  - abbr: IP
    expansion: Internet Protocol
  - abbr: IPv4
    expansion: Internet Protocol version 4
  - abbr: IPv6
    expansion: Internet Protocol version 6
  - abbr: IAP
    expansion: Identity-Aware Proxy
  - abbr: VM
    expansion: virtual machine
  - abbr: UDP
    expansion: User Datagram Protocol
  - abbr: VPC
    expansion: Virtual Private Cloud
  - abbr: NAT
    expansion: network address translation
  - abbr: NIC
    expansion: network interface card
  - abbr: SSH
    expansion: Secure Shell
  - abbr: OpenSSH
    expansion: OpenBSD Secure Shell
  - abbr: DNS
    expansion: Domain Name System
  - abbr: DoH
    expansion: DNS over HTTPS
  - abbr: PeerAPI
    expansion: overlay peer application-programming interface (exit DNS over HTTPS)
  - abbr: HTTPS
    expansion: Hypertext Transfer Protocol Secure
  - abbr: HTTP
    expansion: Hypertext Transfer Protocol
  - abbr: API
    expansion: application programming interface
  - abbr: CLI
    expansion: command-line interface
  - abbr: MTU
    expansion: Maximum Transmission Unit
  - abbr: ULA
    expansion: unique-local address (IPv6)
  - abbr: LAN
    expansion: Local Area Network
  - abbr: WG
    expansion: WireGuard
  - abbr: canIpForward
    expansion: Google Cloud instance flag that allows IP forwarding
  - abbr: PORT
    expansion: overlay UDP listen port setting
  - abbr: MASQUERADE
    expansion: iptables masquerade (source NAT)
  - abbr: KEX
    expansion: key exchange
  - abbr: RD
    expansion: Recursion Desired (DNS flag)
  - abbr: Happy-Eyeballs
    expansion: dual-stack connection racing (RFC 8305)
  - abbr: LOCAL
    expansion: iptables addrtype match for locally-owned addresses
  - abbr: nft
    expansion: nftables (Linux packet filter)
  - abbr: Pi
    expansion: single-board computer (Raspberry Pi class)
  - abbr: ControlPath
    expansion: OpenSSH multiplexing socket path option
  - abbr: UNCONN
    expansion: ss(8) unconnected socket state
  - abbr: Android
    expansion: mobile operating system
---

# Google Cloud overlay exit (IP forwarding, listen port, Identity-Aware Proxy)

## Context

A cloud virtual machine (VM) on Google Cloud Platform (GCP) is a reasonable **backup** `<exit-node>`. It is a poor daily primary if the operator’s workstation is the agent host that would lose internet when the exit is wrong.

Several independent switches have to be true at once. Missing any one looks like “the overlay product is broken”:

- The VM instance MUST have Internet Protocol (IP) forwarding (`canIpForward` true in the instance application programming interface (API), plus `net.ipv4.ip_forward` / IPv6 forwarding in the guest).
- The overlay node MUST advertise `0.0.0.0/0` **and** `::/0`. Android clients hide the exit if `::/0` is stripped (`ExitNodeOption=false`).
- Overlay User Datagram Protocol (UDP) listen **PORT MUST be a fixed well-known 41641** (the overlay product’s usual UDP port). Opening a Virtual Private Cloud (VPC) firewall rule for 41641 while the daemon has `PORT=0` (ephemeral) is a no-op. An **empty** `PORT=` can fail daemon start. Ship PORT + daemon restart + guest firewall + VPC rule **together**.
- MUST NOT add a second `ip6tables MASQUERADE -o <gcp-nic>` on top of the overlay postrouting chain. Duplicate IPv6 masquerade (source network address translation (NAT)) breaks exit-client Hypertext Transfer Protocol Secure (HTTPS) over IPv6. Use the overlay’s own postrouting plus `addrtype LOCAL` only.
- The policy-routing IPv6 default toward the internet MUST be `via fe80::… dev <gcp-nic>`, not `dev <gcp-nic>` alone. Link-local gateway is required on GCP-style networking.
- `rp_filter=2` (loose) on `<gcp-nic>` so return traffic from the exit path is not dropped as martian.
- **Identity-Aware Proxy (IAP)** SSH is **break-glass**. Daily admin is overlay OpenSSH on port 22. The overlay product’s `ssh` command-line interface (CLI) MAY fail key exchange (KEX) on some guest images — use **plain OpenSSH** to the overlay address.
- `tailscale dns query` (or equivalent) on the VM often shows metadata `169.254.169.254`. That is **guest resolver pretty-print**, not the exit overlay peer-API (PeerAPI) DNS over HTTPS (DoH) path.
- A popular leak-test website often returns **502** from some GCP ranges. Use `example.com` / `www.google.com` as browse gates, not that leak-test as a hard canary.

This exit is **backup only**. MUST NOT publish a ranked “try exit A then B” ladder in a public spec. MUST NOT select this exit on the **agent workstation** to reproduce ([OEN-S18](../supporting/s18-do-not-set-exit-on-agent-workstation.md)).

## Topology

```text
[<overlay-peer> LAN Pi] --exit selected--> [<exit-node> GCE-like VM]
    canIpForward + guest ip_forward
    advertise 0.0.0.0/0 AND ::/0
    overlay UDP PORT=41641  +  VPC allow UDP 41641  (together)
    NAT: overlay postrouting only — MUST NOT second MASQUERADE -o <gcp-nic>
    IPv6 default via fe80::… dev <gcp-nic>
    rp_filter=2 on <gcp-nic>

Admin: OpenSSH overlay :22 daily; IAP break-glass
Soak: <overlay-peer>, NEVER the agent workstation
```

## Bind

| Placeholder | Operator fills | Class |
|-------------|----------------|-------|
| `<exit-node>` | Google Cloud overlay exit VM | Cloud VM |
| `<overlay-peer>` | Soak client | LAN Pi |
| `<gcp-nic>` | Guest public NIC | Iface |
| `<overlay-tun>` | Overlay tun | Iface |
| `<user>` | SSH user | Guest |
| `<overlay-v4>` | Overlay IPv4 of the exit | Never publish |

## Formulas

`mss4 = <wg-mtu> - 40`, `mss6 = <wg-mtu> - 60` apply on the **client underlay**, not as a GCP MTU knob. Do not keep changing GCP MTU for Wi-Fi vs cellular splits ([OEN-S26](../supporting/s26-wifi-vs-cellular-underlay.md)).

## Decision

Bring a Google Cloud overlay exit up as a **checklist**, not as a single `advertise-exit-node` flag. Treat Identity-Aware Proxy as recovery. Treat metadata Domain Name System (DNS) and leak-test HTTP 502 as misleading diagnostics. Never hairpin the operator’s workstation through this exit while an agent session needs the internet.

## Consequences

- Phones can see the exit (because `::/0` is present).
- Mesh UDP actually hits the VM (because PORT is fixed and the VPC rule matches).
- Exit-client IPv6 HTTPS works (because NAT is not double-masqueraded).
- Operators still have a door when overlay SSH key exchange fails (IAP), without making IAP the daily path.

## Agent stop rule

> MUST emit a bound checklist (`canIpForward`, `PORT=41641`, `ss`, `curl -4/-6` from `<overlay-peer>`).  
> MUST NOT `gcloud compute instances reset`.  
> MUST NOT select this exit on the agent workstation.  
> MUST NOT add a second IPv6 MASQUERADE on `<gcp-nic>`.

## Procedure

Placeholders: `<exit-node>` is the GCP VM. `<gcp-nic>` is the guest network interface (NIC). `<overlay-peer>` is a **non-workstation** client used for soak (a LAN Pi). Never the agent workstation.

1. **P1 — Confirm IP forwarding in the instance and the guest.**
   - **Action:** From break-glass SSH, `gcloud compute instances describe` (or equivalent) and check `canIpForward` is true. In the guest: `sysctl net.ipv4.ip_forward` (and IPv6 forwarding if you advertise `::/0`).
   - **Expected:** API `canIpForward: true`. sysctl is 1.
   - **On failure:** Stop. Set canIpForward on the instance (requires recreate or the documented API update) before debugging NAT.

2. **P2 — Advertise both default routes and keep accept-dns off on the exit VM.**
   - **Action:** On `<exit-node>`, advertise exit plus `0.0.0.0/0,::/0`. Set `accept-dns=false` on this VM (guest DNS pretty-print is not PeerAPI; turning accept-dns on can break Recursion Desired (RD)=0 exit DNS — [OEN-23](23-cloud-exit-accept-dns.md)).
   - **Expected:** Coordinator or `status` shows the node offers exit and both routes. Android does not hide the node.
   - **On failure:** If `::/0` is missing, phones will not list the exit. Re-advertise; do not debug DNS first.

3. **P3 — Fix overlay UDP PORT and the cloud firewall together.**
   - **Action:** Set daemon `PORT=41641` (never empty, never leave `0` in production). Restart the daemon. Allow UDP 41641 on the guest firewall **and** the VPC rule for `<gcp-nic>`.

     ```bash
     ssh -o ControlPath=none <user>@<exit-node> 'ss -ulnp | grep 41641; sysctl net.ipv4.ip_forward net.ipv6.conf.all.forwarding'
     ```
   - **Expected:** `ss` / `netstat` shows UDP 41641. VPC rule is not a decoration on top of PORT=0.
   - **On failure:** If PORT was 0, the VPC allow did nothing. Set PORT, restart, then re-check. [OEN-S23](../supporting/s23-vpc-41641-useless-while-port-0.md).

4. **P4 — NAT and policy routing without a second MASQUERADE.**
   - **Action:** Inspect ip6tables/nft. There MUST NOT be an extra `MASQUERADE -o <gcp-nic>` beside overlay postrouting. IPv6 default in the exit policy table MUST be `via fe80::… dev <gcp-nic>`. Set `net.ipv4.conf.<gcp-nic>.rp_filter=2` (and the IPv6 analogue if used).
   - **Expected:** Exit-client `curl -6 https://example.com` returns 200. No duplicate masquerade.
   - **On failure:** Remove the extra MASQUERADE. Fix the default route to include the link-local gateway. Do not add more NAT.

5. **P5 — Soak from a LAN Pi, not from the agent workstation.**
   - **Action:** On `<overlay-peer>` (LAN Pi), select `<exit-node>` briefly. `curl -4` and `curl -6` to `https://example.com` with a short timeout. Then clear the exit.
   - **Expected:** HTTP 200 on both families. Egress addresses belong to the cloud, not the home tunnel.
   - **On failure:** If v4 works and v6 leaks home, that may be LAN unique-local address (ULA) Happy-Eyeballs ([OEN-20](20-lan-ula-happy-eyeballs-leak.md)) or Wi-Fi vs cellular underlay ([OEN-S26](../supporting/s26-wifi-vs-cellular-underlay.md)) — not automatically a GCP NAT bug. If cellular-class clients work and Wi-Fi does not, do not keep changing GCP Maximum Transmission Unit (MTU).

6. **P6 — Admin door: plain OpenSSH on overlay 22; IAP is break-glass.**
   - **Action:** Prefer `ssh user@<exit-node-overlay>`. If the overlay `ssh` CLI fails during key exchange, use plain OpenSSH. Use IAP only when overlay is down.
   - **Expected:** Overlay OpenSSH works for daily ops. IAP is documented, unused in the happy path.
   - **On failure:** Do not `gcloud compute instances reset` as a debug step. Check PORT/mesh first ([OEN-01](01-overlay-ssh-byte-cliff.md) if large output hangs).

7. **P7 — Ignore misleading DNS and leak-test canaries.**
   - **Action:** If `dns query` on the VM shows `169.254.169.254`, ignore it for exit-client DNS. If a leak-test site returns 502 from GCP, switch the browse gate to `example.com`.
   - **Expected:** Exit DNS is proven with PeerAPI DoH from a **non-exit** client ([OEN-05](05-exit-peerapi-dns-stub.md) / [OEN-14](14-exit-dns-is-peerapi.md)), not with guest `dig`.
   - **On failure:** Do not set `accept-dns=true` on the exit VM to make the display pretty.

## Verify

- `canIpForward` true; guest forwarding on; both default routes advertised.
- Daemon listens UDP 41641; VPC and guest firewall allow it.
- No extra `MASQUERADE -o <gcp-nic>`.
- Policy IPv6 default uses `via fe80::…`.
- `<overlay-peer>` soak: `example.com` 200 over the exit; agent workstation exit remains unset.
- IAP is available and unused in the happy path.

## Expected samples

```text
canIpForward: true
udp UNCONN ... 0.0.0.0:41641
# soak from <overlay-peer>
200
200
```

## MUST NOT

- MUST NOT put GCP **project ids**, **zones**, or **VM inventory names** in public text.
- MUST NOT publish a ranked exit ladder.
- MUST NOT select this exit on the agent workstation to reproduce.
- MUST NOT add a second IPv6 MASQUERADE on `<gcp-nic>`.
- MUST NOT leave `PORT` empty or `0` while counting on a VPC UDP 41641 rule.
- MUST NOT treat metadata DNS or a leak-test 502 as proof the exit is down.
- MUST NOT reset the VM as a first debug step.

## Related specs

- [OEN-01 Overlay SSH byte cliff](01-overlay-ssh-byte-cliff.md)
- [OEN-16 Commercial WireGuard endpoint rotation](16-commercial-wg-endpoint-rotation.md) — underlay to this VM may still be commercial WireGuard (WG) from home
- [OEN-13 Overlay vs underlay vs unique-local layers](13-overlay-underlay-ula-layers.md)
- [OEN-23 Cloud-exit accept-dns](23-cloud-exit-accept-dns.md)
- [OEN-S18 Do not set exit on the agent workstation](../supporting/s18-do-not-set-exit-on-agent-workstation.md)
- [OEN-S21 Cloud exit hairpins home LAN](../supporting/s21-cloud-exit-hairpin-lan.md)
- [OEN-S22 Identity-Aware Proxy vs overlay key exchange](../supporting/s22-iap-break-glass-kex.md)
- [OEN-S23 VPC 41641 while PORT=0](../supporting/s23-vpc-41641-useless-while-port-0.md)

## Prior art (Not novel)

GCP `canIpForward` and “allow UDP 41641” appear in overlay exit tutorials. This spec’s claim is the **failure cluster**: PORT=0 vs VPC, duplicate v6 MASQUERADE, policy default without link-local gateway, Android hiding exits without `::/0`, IAP vs CLI KEX, metadata DNS vs PeerAPI, and leak-test 502 from GCP ranges.
