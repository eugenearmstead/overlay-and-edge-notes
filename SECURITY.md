# Security policy

**Overlay and Edge Notes** is public field notes and documentation. It is not a hosted product, not a login service, and not software-as-a-service.

**Author:** [Eugene Armstead](https://www.armsteadent.com/). That URL is for attribution. It is **not** a vulnerability inbox.

## How to report

Use **GitHub private vulnerability reporting only**.

1. Open this repository on GitHub.com.
2. Open the **Security** tab.
3. Choose **Report a vulnerability**.

That form is private. Maintainers see it. It is not a public Issue.

**MUST NOT** open a public Issue for a security report.  
**MUST NOT** expect a published email address. This project does not provide one.

Public Issues stay **open** for typos, documentation fixes, and questions. Those are not security reports.

## Scope

This repository is Markdown field notes plus a Python HTML builder. There is no production login, no customer data store, and no hosted application to take down.

**Out of scope for this project:**

- It is not software-as-a-service.
- Placeholders such as `<cloud-vps>`, `<lan-pi>`, `<overlay-peer>`, `<exit-node>`, `<wg-iface>`, and `<gcp-nic>` are **intentional**. They are not missing secrets.
- Do not file Tailscale, CrowdSec, Cloudflare, or Headscale bugs under the author’s GitHub account from these notes. The pages are rewritten field notes, not an upstream reproduction attached to the author.

**In scope:** a secret accidentally present in this tree or in git history; a defect in `scripts/` or GitHub Actions that could harm someone who clones the repository.

## What reporters may include

Reporters **MAY** include all technical detail they have: their commands, their addresses, their traces. That is allowed. Do not strip your own evidence to stay vague.

## Maintainer leak gate

Maintainers **MUST NOT** copy the author’s private hostnames, LAN/overlay/WAN IP addresses, or lab inventory into public issues, advisories, or GitHub Pages. Scrub before any public text.

This gate is **self-interest for the maintainer**. It is not a request that reporters stay vague.

## Secret scanning

GitHub **secret scanning** is enabled on this repository. This tree **MUST** never contain API tokens, keys, or passwords. If a reporter finds a secret in git history, report it privately (Security tab → Report a vulnerability).

## Dependabot

Dependabot alerts and Dependabot security updates are enabled.

[`.github/dependabot.yml`](.github/dependabot.yml) currently covers **GitHub Actions** on a weekly schedule. There is no Python package manifest (`requirements.txt` or `pyproject.toml`) in this repository. Dependabot will cover new ecosystems when those manifests appear. Do not invent a fake requirements file.

## Code scanning

CodeQL runs from [`.github/workflows/codeql.yml`](.github/workflows/codeql.yml) on the Python builder. Additional languages will be added when those sources exist.

## Bounty

There is **no bug bounty**. Optional public thanks or credit later if the maintainer chooses. There is no hall-of-fame list now.
