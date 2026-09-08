---
title: Overlay and Edge Notes changelog
date_published: 2026-09-08
author: Eugene Armstead
author_url: https://www.armsteadent.com/
canonical: https://eugenearmstead.github.io/overlay-and-edge-notes/changelog.html
description: Series changelog for Overlay and Edge Notes. Dated in Mountain Time.
terms:
  - abbr: OEN
    expansion: Overlay and Edge Notes
  - abbr: MST
    expansion: Mountain Standard Time
  - abbr: HTML
    expansion: HyperText Markup Language
  - abbr: SSH
    expansion: Secure Shell
  - abbr: MSS
    expansion: Maximum Segment Size
  - abbr: ICMP
    expansion: Internet Control Message Protocol
  - abbr: MTU
    expansion: Maximum Transmission Unit
  - abbr: IPv4
    expansion: Internet Protocol version 4
  - abbr: IPv6
    expansion: Internet Protocol version 6
  - abbr: TCP
    expansion: Transmission Control Protocol
  - abbr: HTTPS
    expansion: Hypertext Transfer Protocol Secure
  - abbr: nft
    expansion: nftables (Linux packet filter)
---

# Changelog

Dated in Mountain Time (MST) for this series. Spec URLs do not change when an edition bumps.

## 2026-09-08 MST — Agent-reproducible complete series

First public slice (six pages, 7 Sep 2026 MST) plus this completion:

- **23 original** specs and **34 supporting** methods are live. No citation ID is “forthcoming.”
- Agent reproduction bar on every spec: ASCII topology, Bind table, formulas (`mss4 = <wg-mtu> - 40`, `mss6 = <wg-mtu> - 60`; historical 1160 is wrong-scope evidence), copy-pasteable IPv4/IPv6 and nft/iptables where the step mutates a node, scrubbed samples, agent stop rule.
- Retrofit of OEN-01, OEN-08, OEN-16, OEN-17, OEN-18, OEN-S01 to edition 2 (same URLs).
- `AGENTS.md` requires Bind-before-apply and forbids treating ICMP success as a TCP/SSH/HTTPS fix.
- `llms.txt`, `llms-full.txt`, `sitemap.xml`, and [2026 edition index](editions/2026.md).

## 2026-09-07 MST — First public slice

Published OEN-01, OEN-08, OEN-16, OEN-17, OEN-18, and OEN-S01 with Armstead chrome, per-page Terms keys, and GitHub Pages from the repository root.
