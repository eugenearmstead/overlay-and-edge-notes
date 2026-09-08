---
id: OEN-10
title: "One generated blocking stylesheet and variable fonts"
kind: original
status: active
edition: 1
date_published: 2026-09-08
author: Eugene Armstead
author_url: https://www.armsteadent.com/
canonical: https://eugenearmstead.github.io/overlay-and-edge-notes/web/10-one-blocking-stylesheet-variable-fonts.html
keywords:
  - core-web-vitals
  - css
  - fonts
  - lcp
backs: []
backed_by:
  - OEN-S06
  - OEN-S09
  - OEN-S10
description: "A new render-blocking stylesheet dropped mobile PageSpeed. Per-weight variable font filenames made Chrome re-download the same woff2. Generate one chrome.css; preload at most two matching variable files."
terms:
  - abbr: OEN
    expansion: Overlay and Edge Notes
  - abbr: SSH
    expansion: Secure Shell
  - abbr: TCP
    expansion: Transmission Control Protocol
  - abbr: ICMP
    expansion: Internet Control Message Protocol
  - abbr: HTTPS
    expansion: Hypertext Transfer Protocol Secure
  - abbr: HTML
    expansion: HyperText Markup Language
  - abbr: CSS
    expansion: Cascading Style Sheets
  - abbr: JS
    expansion: JavaScript
  - abbr: nft
    expansion: nftables (Linux packet filter)
  - abbr: LCP
    expansion: Largest Contentful Paint
  - abbr: CWV
    expansion: Core Web Vitals
  - abbr: PSI
    expansion: PageSpeed Insights
  - abbr: URL
    expansion: Uniform Resource Locator
  - abbr: UI
    expansion: user interface
  - abbr: Pi
    expansion: single-board computer (Raspberry Pi class)
  - abbr: Playwright
    expansion: browser automation and test runner
  - abbr: Inter
    expansion: variable sans-serif font family
  - abbr: Playfair
    expansion: variable serif font family
  - abbr: Rocket
    expansion: Cloudflare Rocket Loader
---

# One generated blocking stylesheet and variable fonts

## Context

Static marketing Core Web Vitals (CWV): extracting home Cascading Style Sheets (CSS) into a **new** render-blocking `<link>` dropped mobile PageSpeed Insights (PSI) **77 → 72**. Self-hosting variable Inter/Playfair as **per-weight filenames** (identical bytes, different URLs) made Chrome re-download the same woff2 three to four times.

The live public example MAY cite `frontrangedoula.com`. MUST NOT describe the origin Pi, Access, or lead pipeline.

Largest Contentful Paint (LCP) portrait preload belongs immediately after viewport with **media-split** 300w vs 480w. Defer decorative hero background until the portrait has loaded. [OEN-S09](../supporting/s09-playwright-desktop-iphone-pixel.md) for layout gates. [OEN-S10](../supporting/s10-file-before-image-deploy.md) before image ship. [OEN-S06](../supporting/s06-do-not-ship-html-only.md).

## Topology

```text
[HTML] --blocking <link stylesheet>--> extra round trip  (PSI drop when a NEW blocking sheet is added)
[variable font] one woff2 file, many @font-face URLs  --> Chrome re-downloads the same bytes
Contract: one generated chrome.css; preload at most two variable files; LCP portrait media-split
```

## Bind

Fill this table **before** any live change. Do **not** paste real values back into public notes.

| Placeholder | Operator fills | Class |
|-------------|----------------|-------|
| `<worker-root>` | Worker / UI source tree | Directory on the workstation |
| `<live-url>` | Public HTTPS origin | URL the browser loads |
| `<preview-url>` | Preview origin if used | URL |
| `<html-path>` | Path that becomes a Response body | File glob |


## Formulas

Proven failure: extra blocking stylesheet dropped mobile PSI 77→72. Self-hosting Inter/Playfair as per-weight filenames (identical bytes) caused 3–4 downloads. Public example site URL MAY be cited; do not describe origin Pi or Access.

## Decision

Generate `chrome.css` as concat of four **source** files (do not hand-merge). Defer decorative font and non-critical CSS with `media="print" onload`. Preload **at most two** variable files whose `href` matches `@font-face src`; latin + latin-ext only.

MUST NOT add a second blocking stylesheet to “clean up” home CSS.

## Consequences

- Mobile PSI stops regressing from an extra blocking link.
- Variable fonts download once.
- LCP portrait wins over decorative background.

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
# From the site tree after Bind:
grep -n 'rel="stylesheet"' <html-path>
# Count distinct woff2 hrefs vs files on disk. Preload href MUST match @font-face src.
curl -sS -o /dev/null -w '%{http_code} %{url_effective}\n' --max-time 15 <live-url>/chrome.css
```

CSS/JS/images MUST 200 ([OEN-S06](../supporting/s06-do-not-ship-html-only.md)). Playwright three devices ([OEN-S09](../supporting/s09-playwright-desktop-iphone-pixel.md)).

1. **P1 — Count render-blocking CSS.**
   - **Action:** View-source the home HTML. Count blocking `<link rel=stylesheet>` without media=print trick.
   - **Expected:** At most one generated chrome stylesheet plus any required third-party you already accepted.
   - **On failure:** If a new home-only CSS link appeared, remove it and concat into chrome.css.
2. **P2 — Match preload href to @font-face src.**
   - **Action:** Preload at most two variable woff2 URLs. They MUST equal the `src` in CSS. No per-weight duplicate filenames for the same bytes.
   - **Expected:** Network panel: each variable file once.
   - **On failure:** If Chrome fetches the same bytes under four URLs, collapse to one filename.
3. **P3 — LCP portrait preload media-split.**
   - **Action:** Preload the LCP portrait immediately after viewport: 300w vs 480w media split. Defer decorative hero background until the portrait `load`.
   - **Expected:** LCP element is the portrait, not the background.
   - **On failure:** Do not preload both portrait and huge background.
4. **P4 — Do not ship HTML-only; file(1) images.**
   - **Action:** CSS/JS/images 200 ([OEN-S06](../supporting/s06-do-not-ship-html-only.md)). `file` before image deploy ([OEN-S10](../supporting/s10-file-before-image-deploy.md)). Playwright Desktop + iPhone + Pixel ([OEN-S09](../supporting/s09-playwright-desktop-iphone-pixel.md)).
   - **Expected:** No layout-destroying 404. Image bytes match the extension’s real type.
   - **On failure:** A CSS “bug” that is a 404 is S06, not a rewrite of chrome.css.

## Expected samples

```text
# Extra blocking stylesheet: LCP/PSI worse than inlined concat
```

## Verify

- One generated blocking chrome.css.
- At most two variable font preloads, href matches @font-face.
- Mobile PSI did not drop from an extra blocking link.
- Playwright three-device layout gate green for nav/hero changes.
- ICMP / small ping success was **not** used as the pass criterion when this spec names TCP, SSH, or HTTPS.
- Bind table was filled by a human before any live `ip` / nft / iptables change.

## MUST NOT

- MUST NOT add a new render-blocking stylesheet to extract home CSS.
- MUST NOT ship per-weight filenames that are identical variable files.
- MUST NOT describe origin Pi, Access, or lead pipeline.
- MUST NOT skip file(1) on images.
- MUST NOT apply live network or firewall changes until Bind is filled by a human.
- MUST NOT claim a fix on ICMP ping alone when Verify names TCP, SSH, or HTTPS.
- MUST NOT publish hostnames, addresses, ULAs, or custom ports.

## Related specs

- [OEN-S06 Do not ship HTML-only](../supporting/s06-do-not-ship-html-only.md)
- [OEN-S09 Playwright Desktop + iPhone + Pixel](../supporting/s09-playwright-desktop-iphone-pixel.md)
- [OEN-S10 file before image deploy](../supporting/s10-file-before-image-deploy.md)
- [OEN-S12 Rocket Loader Off](../supporting/s12-rocket-loader-off.md)
- [OEN-09 Git merge is not a live Worker](09-git-merge-is-not-a-live-worker.md)

## Prior art (Not novel)

CWV and variable fonts are heavily blogged. This spec’s claim is the measured 77→72 extra link plus duplicate variable URLs plus LCP media-split contract.

