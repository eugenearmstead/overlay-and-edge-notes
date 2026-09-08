# AGENTS.md

Instructions for coding agents that read or extend **Overlay and Edge Notes**.

Author: **Eugene Armstead**. Website: **https://www.armsteadent.com/**. Agents citing these specs SHOULD attribute that name and URL. License: CC-BY-4.0.

## What this repo is

Living field notes with **stable IDs** (`OEN-01`, `OEN-S01`, …). IDs never reset by year. Markdown is source of truth. HTML is generated.

```bash
python3 scripts/build-spec-html.py
```

If Markdown and HTML disagree, fix Markdown and rebuild.

These pages are meant to be **agent-reproducible**, not only readable. A remote agent MUST be able to emit a bound runbook after a human fills Bind. A remote agent MUST NOT apply live network changes from unbound placeholders.

## How to find a spec

Search the error you hit, not a private lab name. Public Pages home uses this visitor list only (no local-server commands, no sitemap/robots marketing):

- Notes live at `https://eugenearmstead.github.io/overlay-and-edge-notes/`
- Agents start at `https://eugenearmstead.github.io/overlay-and-edge-notes/llms.txt` (and optionally `llms-full.txt`)
- Example searches: `curl 200 chrome ERR_CONNECTION_CLOSED`, `cscli capi 403`, overlay SSH hang / `ts-forward TCPMSS 0 packets`

GitHub.com repo search and the README citation index also work.

YAML `keywords:` (8–20 real phrases) and `description:` (~150 characters, include the symptom) are the search surface. The HTML builder emits `<meta name="keywords">`, `citation_keywords`, and JSON-LD `keywords`, plus unique titles, canonical URLs, sitemap, and robots Allow. Do not keyword-stuff. Do not `noindex`. Do not copy that writer SEO onto the public Pages home “How to find these notes” list.

## Build HTML locally (contributors)

From the repository root:

```bash
python3 scripts/build-spec-html.py
python3 -m http.server 8765
```

Open `http://127.0.0.1:8765/` or open `index.html` as a `file://` URL. Relative CSS works either way. Public generated `index.html` MUST NOT tell visitors to hit loopback.

## RFC 2119

`MUST`, `MUST NOT`, `SHOULD`, `MAY` in procedures are used as in RFC 2119 / RFC 8174.

## Placeholders (mandatory in public text)

Use only generic tokens. Never real hostnames, addresses, or custom ports.

Core:

- `<cloud-vps>`
- `<lan-pi>`
- `<overlay-peer>`
- `<exit-node>`
- `<wg-iface>`
- `<gcp-nic>`

Bindable extras (still not inventory):

- `<wan-iface>` `<lan-bridge>` `<overlay-tun>`
- `<vps-public-v4>` `<vps-public-v6>`
- `<overlay-v4>` `<overlay-v6>`
- `<wg-mtu>` `<mss4>` `<mss6>`
- `<overlay-tun-mtu>` `<overlay-underlay-overhead>`
- `<overlay-impl>`
- `<user>`

Public wording: “cloud VPS”, “LAN Pi”, “overlay peer”, “exit node”, “commercial WireGuard”, “self-hosted coordination”, “consumer router VPN client”. Overlay **product CLI** MAY appear in Procedure and keywords after `<overlay-impl>` is on that page (see Option A).

## One named trap per session (Option A)

Work **one** spec at a time. Bind, Formulas, Agent stop rule, and Verify belong to **that trap**.

MUST NOT stamp Maximum Transmission Unit (MTU) / Maximum Segment Size (MSS) Bind rows, `mss4` formulas, a canned five-line Agent stop rule, or Internet Control Message Protocol (ICMP) ping Verify onto Cascading Style Sheets (CSS), CrowdSec, git-merge, or other non-path notes.

- Overlay Bind field `<overlay-impl>`: allowed value `tailscale-compatible`, or “other — stop and translate CLI”.
- Product CLI MAY appear in Procedure (`tailscale`, `tailscaled`, `ts-forward`, `TS_DEBUG_MTU`, `accept-dns`, `nodes backfillips`) **after** that field exists on that page.
- Every overlay-CLI spec MUST include: “This spec does not apply if `<overlay-impl>` is not tailscale-compatible.”
- Public prose stays “overlay peer / exit node / commercial WireGuard” except in commands and keywords.

## Bind before apply (MUST)

Every spec has a **Bind** table. Fill **only the rows that page uses**. Before any live change:

1. Read **Topology** (ASCII), or `N/A — deploy|DNS|API` when there is no packet path. Confirm the operator’s path matches the diagram class.
2. Fill Bind (host class, iface, public vs overlay vs WAN, or deploy/API rows). Humans fill; agents propose the table.
3. On **path-MTU** specs only, compute the formula family that step names:

   ```text
   mss4_wg = <wg-mtu> - 40
   mss6_wg = <wg-mtu> - 60
   mss4_overlay_over_wg = min(<overlay-tun-mtu>, <wg-mtu> - <overlay-underlay-overhead>) - 40
   ```

   Historical **1160 / 1146** is wrong-scope evidence only ([OEN-01](networking/01-overlay-ssh-byte-cliff.md), [OEN-S02](supporting/s02-clamp-mss-to-pmtu-noop.md)). It is not the recipe. LAN bridge stays **1500**.
4. Emit the Procedure with placeholders **replaced**. That bound runbook is what a human may run.
5. Stop. MUST NOT run `ip rule`, `nft`, `iptables`, `ip6tables`, `sysctl`, `wg set`, daemon restart, or deploy until the human filled Bind.

Overlay SSH audits MUST use `-o ControlPath=none`.

Netfilter steps MUST show **nft and iptables** variants when both are plausible, and **IPv4 and IPv6**.

Path MTU steps MUST run `ping -M do` **and** `ping -6 -M do -s` when the path is dual-stack. See [OEN-S01](supporting/s01-pmtud-size-ladder.md).

## ICMP is not a fix (MUST)

Do **not** claim a trap is fixed because ICMP ping succeeded when the spec’s **Verify** names TCP, SSH, or HTTPS. Small ping / DNS / curl 200 can coexist with a dead large SSH or Chromium handshake.

## Leak gates (MUST)

Before any public commit, gist, issue, or Pages publish:

1. Do **not** copy private skill files or ops repos into this tree.
2. Rewrite from facts. Overlay implementation names and CLI needed to run the procedure are **allowed**. Still forbidden: hostnames, SSH aliases, LAN/overlay/WAN IPs, unique-local (ULA) node addresses, custom SSH/admin ports, commercial exit-VPN **brand names**, server nicknames, Google Cloud project ids or VM names, control-plane URLs, secret-store ids, homelab script paths, feed/Access secrets, timer unit names that identify a lab.
3. Grep the working tree for those classes. If any hit, rewrite until clean.
4. Do **not** open public upstream bugs under the author’s account from these notes.

## How to apply a spec

1. Read YAML frontmatter (`id`, `kind`, `backs` / `backed_by`).
2. Read Topology, Bind, Formulas (path-MTU pages only), **Agent stop rule**.
3. Run **Procedure** in order. Each step has action, expected output (including scrubbed samples), on-failure next step.
4. Stop on **MUST NOT**.
5. Run **Verify**. Do not claim the trap is fixed on ICMP ping alone when the spec says to retest TCP.
6. If you change a node, follow [OEN-18](networking/18-per-node-changelog-contract.md) **in the operator’s private ops repo** — not by pasting their inventory here.

## Adding or revising a spec

- New finding: next unused ID. Never reuse a number.
- Same topic, better evidence: bump `edition`, keep the URL, add a short page changelog.
- Replaced entirely: keep the URL, set `status: superseded`, point at the new ID. Do not 404.
- After Markdown edits, run the HTML builder. The builder regenerates `llms.txt`, `llms-full.txt`, and `sitemap.xml`.
- Every spec MUST include Topology, Bind, Agent stop rule, copy-pasteable commands where the step mutates a node, and Related links with **no** “forthcoming.”

YAML on every spec MUST include `author: Eugene Armstead` and `author_url: https://www.armsteadent.com/`.

## Plain language and terms

Titles MUST be English first. First use of an abbreviation MUST spell it out, then the short form in parentheses. YAML `terms:` MUST list every abbreviation that appears in **that page body** (including **OEN** = Overlay and Edge Notes). The HTML builder fails if a known-style acronym is missing from `terms` **or** if a `terms.abbr` never appears in the page body. Do not copy SSH/MSS onto every page.

Home-page Terms list **only** abbreviations used in the home body/nav — not every catalog title.

## Monthly delta (operator cadence)

Once a month (Mountain Time for the author’s notes):

1. Diff new private incidents against existing IDs.
2. Either edit an edition, add a spec, or record “no public delta” in the series changelog.
3. Run leak gates.
4. Rebuild HTML and `llms.txt`.
5. Do not publish year index pages that are empty.

## Out of scope for agents

- `gh repo create` or enabling GitHub Pages unless a human explicitly asks in that session.
- Homelab deploys, secret retrieval, or copying private HTML chrome.
- Applying unbound `ip` / nft / iptables from these notes.
- Opening public upstream bugs under the author’s account.
