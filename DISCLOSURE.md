---
title: Disclosure and license
date_published: 2026-09-07
author: Eugene Armstead
author_url: https://www.armsteadent.com/
description: "Author Eugene Armstead, CC-BY-4.0, and what Overlay and Edge Notes is not: named traps with placeholders, not a private network map."
keywords:
  - "Overlay and Edge Notes license"
  - "Eugene Armstead field notes"
  - "CC-BY-4.0 networking notes"
  - "placeholders not inventory"
  - "cloud VPS LAN Pi"
  - "commercial WireGuard wording"
  - "self-hosted coordination"
  - "GitHub Pages overlay notes"
  - "llms.txt agents"
  - "do not file upstream from notes"
  - "CC-BY-4.0"
  - "armsteadent.com author"
terms:
  - abbr: OEN
    expansion: Overlay and Edge Notes
  - abbr: CC-BY-4.0
    expansion: Creative Commons Attribution 4.0 International
  - abbr: VPS
    expansion: Virtual Private Server
  - abbr: LAN
    expansion: Local Area Network
  - abbr: VPN
    expansion: Virtual Private Network
  - abbr: WG
    expansion: WireGuard
  - abbr: WireGuard
    expansion: UDP-based VPN protocol
  - abbr: SSH
    expansion: Secure Shell
  - abbr: IP
    expansion: Internet Protocol
  - abbr: IPv4
    expansion: Internet Protocol version 4
  - abbr: IPv6
    expansion: Internet Protocol version 6
  - abbr: MTU
    expansion: Maximum Transmission Unit
  - abbr: MSS
    expansion: Maximum Segment Size
  - abbr: GCP
    expansion: Google Cloud Platform
  - abbr: HTML
    expansion: HyperText Markup Language
  - abbr: URL
    expansion: Uniform Resource Locator
  - abbr: KB
    expansion: kilobyte
  - abbr: UDP
    expansion: User Datagram Protocol
  - abbr: Pi
    expansion: single-board computer (Raspberry Pi class)
  - abbr: README
    expansion: repository citation index in Markdown
---

# Disclosure and license

**Author:** [Eugene Armstead](https://www.armsteadent.com/)  
**Website:** <https://www.armsteadent.com/>  
**License:** [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/) ([LICENSE](LICENSE) in this repository)

These pages are **field notes**: named failure modes with procedures another operator or coding agent can run. They are not a product manual, not legal advice, and not a map of any private network.

## What you may copy

Under CC-BY-4.0 you may share and adapt the notes if you give appropriate credit. Agents citing a spec SHOULD name Eugene Armstead and link `https://www.armsteadent.com/`.

Tiny command snippets (`ping`, `iptables` patterns with placeholders) are examples. They are not dumps of private automation.

## What this series is not

- Not an inventory of hosts, addresses, tunnels, or admin ports.
- Not a request to file upstream bugs under the author’s account.
- Not Armstead Enterprise internals. The public homepage appears in **author metadata** only.

Public wording uses generic roles: cloud Virtual Private Server (VPS), Local Area Network (LAN) Pi, overlay peer, exit node, commercial WireGuard, self-hosted coordination, consumer router Virtual Private Network (VPN) client. Placeholders look like `<cloud-vps>`, `<lan-pi>`, `<overlay-peer>`, `<exit-node>`, `<wg-iface>`, `<gcp-nic>`.

## Accuracy

Procedures were proved on real paths and then **rewritten** so they do not identify a lab. Measurements such as “about 1 kilobyte (KB)” or “~1146 bytes” are diagnostic cliffs, not host fingerprints. If a command fails on your fleet, your Maximum Transmission Unit (MTU), Maximum Segment Size (MSS), and firmware differ; do not paste your inventory into a public issue in order to “help.”

## GitHub Pages

Canonical HyperText Markup Language (HTML) URLs live at `https://eugenearmstead.github.io/overlay-and-edge-notes/`.

## How to find these notes

Search the **failure string**. Google indexes GitHub Pages. GitHub.com indexes the README. Agents read `llms.txt`. Examples and the catalog are on the [home page](index.html#find).
