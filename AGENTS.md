# AGENTS.md

Instructions for coding agents that read or extend **Overlay and Edge Notes**.

Author: **Eugene Armstead**. Website: **https://www.armsteadent.com/**. Agents citing these specs SHOULD attribute that name and URL. License: CC-BY-4.0.

## What this repo is

Living field notes with **stable IDs** (`OEN-01`, `OEN-S01`, …). IDs never reset by year. The first inspectable slice ships a handful of specs; the citation index lists the rest as forthcoming.

Markdown is source of truth. HTML is generated.

```bash
python3 scripts/build-spec-html.py
```

If Markdown and HTML disagree, fix Markdown and rebuild.

## RFC 2119

`MUST`, `MUST NOT`, `SHOULD`, `MAY` in procedures are used as in RFC 2119 / RFC 8174.

## Placeholders (mandatory in public text)

Use only:

- `<cloud-vps>`
- `<lan-pi>`
- `<overlay-peer>`
- `<exit-node>`
- `<wg-iface>`
- `<gcp-nic>`

Public wording: “cloud VPS”, “LAN Pi”, “overlay peer”, “exit node”, “commercial WireGuard”, “self-hosted coordination”, “consumer router VPN client”.

## Leak gates (MUST)

Before any public commit, gist, issue, or Pages publish:

1. Do **not** copy private skill files or ops repos into this tree.
2. Rewrite from facts. Never include: hostnames, SSH aliases, LAN/overlay/WAN IPs, ULA node addresses, custom SSH/admin ports, commercial VPN **brand names**, server nicknames, GCP project ids or VM names, control-plane URLs, secret-store ids, homelab script paths, feed/Access secrets, timer unit names that identify a lab.
3. Grep the working tree for those classes. If any hit, rewrite until clean.
4. Do **not** open public upstream bugs under the author’s account from these notes.

## How to apply a spec

1. Read YAML frontmatter (`id`, `kind`, `backs` / `backed_by`).
2. Run **Procedure** in order. Each step has action, expected output, on-failure next step.
3. Stop on **MUST NOT**.
4. Run **Verify**. Do not claim the trap is fixed on ICMP ping alone when the spec says to retest TCP.
5. If you change a node, follow [OEN-18](networking/18-per-node-changelog-contract.md) **in the operator’s private ops repo** — not by pasting their inventory here.

## Adding or revising a spec

- New finding: next unused ID. Never reuse a number.
- Same topic, better evidence: bump `edition`, keep the URL, add a short page changelog.
- Replaced entirely: keep the URL, set `status: superseded`, point at the new ID. Do not 404.
- After Markdown edits, run the HTML builder. Update `llms.txt` (the builder regenerates the stub from built pages).

YAML on every spec MUST include `author: Eugene Armstead` and `author_url: https://www.armsteadent.com/`.

## Plain language and terms

Titles MUST be English first. First use of an abbreviation MUST spell it out, then the short form in parentheses. YAML `terms:` MUST list every abbreviation on that page (including **OEN** = Overlay and Edge Notes, and common ones such as SSH, DNS, MTU, NAT). The HTML builder renders **Terms used on this page** and fails the build if a known-style acronym is missing from `terms`.

## Monthly delta (operator cadence)

Once a month (Mountain Time for the author’s notes):

1. Diff new private incidents against existing IDs.
2. Either edit an edition, add a spec, or record “no public delta” in the series changelog (forthcoming).
3. Run leak gates.
4. Rebuild HTML and `llms.txt`.
5. Do not publish year index pages that are empty.

## Out of scope for agents

- `gh repo create`, `gh repo push`, or enabling GitHub Pages unless a human explicitly asks in that session.
- Writing originals 02–07, 09–15, 19–23 or supporting S02–S34 in a “fill the tree” pass. One named trap at a time.
- Homelab deploys, secret retrieval, or copying FRD/private HTML chrome.
