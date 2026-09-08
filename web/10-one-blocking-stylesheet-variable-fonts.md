---
id: "OEN-10"
title: "One generated blocking stylesheet and variable fonts"
kind: "original"
status: "active"
edition: 2
date_published: "2026-09-08"
author: "Eugene Armstead"
author_url: "https://www.armsteadent.com/"
canonical: "https://eugenearmstead.github.io/overlay-and-edge-notes/web/10-one-blocking-stylesheet-variable-fonts.html"
keywords:
  - "render-blocking stylesheet PSI drop"
  - "variable font re-download woff2"
  - "one generated <site.css>"
  - "LCP preload media-split"
  - "Core Web Vitals fonts"
  - "per-weight variable filenames"
  - "PageSpeed mobile 77 to 72"
  - "preload at most two woff2"
  - "latin latin-ext only"
  - "defer decorative font"
  - "Cloudflare Worker CSS"
  - "LCP portrait preload"
backs:
  []
backed_by:
  - OEN-S06
  - OEN-S09
  - OEN-S10
description: "A new render-blocking stylesheet dropped mobile PageSpeed. Per-weight variable font filenames made Chrome re-download the same woff2. Generate one <site.css>; preload at most two matching variable files."
terms:
  - abbr: CSS
    expansion: Cascading Style Sheets
  - abbr: CWV
    expansion: Core Web Vitals
  - abbr: HTML
    expansion: HyperText Markup Language
  - abbr: HTTPS
    expansion: Hypertext Transfer Protocol Secure
  - abbr: JS
    expansion: JavaScript
  - abbr: LCP
    expansion: Largest Contentful Paint
  - abbr: OEN
    expansion: Overlay and Edge Notes
  - abbr: Pi
    expansion: single-board computer (Raspberry Pi class)
  - abbr: Playwright
    expansion: browser automation and test runner
  - abbr: PSI
    expansion: PageSpeed Insights
  - abbr: URL
    expansion: Uniform Resource Locator
---

# One generated blocking stylesheet and variable fonts

## Context

Static marketing Core Web Vitals (CWV): extracting home Cascading Style Sheets (CSS) into a **new** render-blocking `<link>` dropped mobile PageSpeed Insights (PSI) **77 → 72**. Self-hosting variable Inter/Playfair as **per-weight filenames** (identical bytes, different URLs) made Chrome re-download the same woff2 three to four times.

The live public example MAY cite `frontrangedoula.com`. MUST NOT describe the origin Pi, Access, or lead pipeline.

Largest Contentful Paint (LCP) portrait preload belongs immediately after viewport with **media-split** 300w vs 480w. Defer decorative hero background until the portrait has loaded. [OEN-S09](../supporting/s09-playwright-desktop-iphone-pixel.md) for layout gates. [OEN-S10](../supporting/s10-file-before-image-deploy.md) before image ship. [OEN-S06](../supporting/s06-do-not-ship-html-only.md).

## Topology

N/A — deploy

## Bind

Fill this table **before** any live change. Do **not** paste real values back into public notes.

| Placeholder | Operator fills | Class |
|-------------|----------------|-------|
| `<html-path>` | Files that become a Response body | Glob |
| `<live-url>` | Public HTTPS origin | URL |
| `<site.css>` | Origin stylesheet filename | Asset |

## Formulas

Proven failure: extra blocking stylesheet dropped mobile PSI 77→72. Self-hosting Inter/Playfair as per-weight filenames (identical bytes) caused 3–4 downloads. Public example site URL MAY be cited; do not describe origin Pi or Access.

## Decision

Generate `<site.css>` as concat of four **source** files (do not hand-merge). Defer decorative font and non-critical CSS with `media="print" onload`. Preload **at most two** variable files whose `href` matches `@font-face src`; latin + latin-ext only.

MUST NOT add a second blocking stylesheet to “clean up” home CSS.

## Consequences

- Mobile PSI stops regressing from an extra blocking link.
- Variable fonts download once.
- LCP portrait wins over decorative background.

## Agent stop rule

> MUST emit the stylesheet and font preload list with `<live-url>` / `<site.css>` filled.
> MUST NOT deploy until those URLs return 200 ([OEN-S06](../supporting/s06-do-not-ship-html-only.md)).
> MUST NOT add a second render-blocking stylesheet.
> MUST NOT apply netfilter from this page.

## Procedure


### Copy-paste commands (after Bind)

```bash
# From the site tree after Bind:
grep -n 'rel="stylesheet"' <html-path>
# Count distinct woff2 hrefs vs files on disk. Preload href MUST match @font-face src.
curl -sS -o /dev/null -w '%{http_code} %{url_effective}\n' --max-time 15 <live-url>/<site.css>
```

CSS/JS/images MUST 200 ([OEN-S06](../supporting/s06-do-not-ship-html-only.md)). Playwright three devices ([OEN-S09](../supporting/s09-playwright-desktop-iphone-pixel.md)).

1. **P1 — Count render-blocking CSS.**
   - **Action:** View-source the home HTML. Count blocking `<link rel=stylesheet>` without media=print trick.
   - **Expected:** At most one generated chrome stylesheet plus any required third-party you already accepted.
   - **On failure:** If a new home-only CSS link appeared, remove it and concat into <site.css>.
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
   - **On failure:** A CSS “bug” that is a 404 is S06, not a rewrite of <site.css>.

## Expected samples

```text
# Extra blocking stylesheet: LCP/PSI worse than inlined concat
```

## Verify

- One generated blocking <site.css>.
- At most two variable font preloads, href matches @font-face.
- Mobile PSI did not drop from an extra blocking link.
- Playwright three-device layout gate green for nav/hero changes.

## MUST NOT

- MUST NOT add a new render-blocking stylesheet to extract home CSS.
- MUST NOT ship per-weight filenames that are identical variable files.
- MUST NOT describe origin Pi, Access, or lead pipeline.
- MUST NOT skip file(1) on images.
- MUST NOT publish hostnames, addresses, ULAs, or custom ports.

## Page changelog

- Edition 2 (8 Sep 2026, Mountain Time): Trap-specific Bind and agent stop rule (review cleanup).

## Related specs

- [OEN-S06 Do not ship HTML-only](../supporting/s06-do-not-ship-html-only.md)
- [OEN-S09 Playwright Desktop + iPhone + Pixel](../supporting/s09-playwright-desktop-iphone-pixel.md)
- [OEN-S10 file before image deploy](../supporting/s10-file-before-image-deploy.md)
- [OEN-S12 Rocket Loader Off](../supporting/s12-rocket-loader-off.md)
- [OEN-09 Git merge is not a live Worker](09-git-merge-is-not-a-live-worker.md)

## Prior art (Not novel)

CWV and variable fonts are heavily blogged. This spec’s claim is the measured 77→72 extra link plus duplicate variable URLs plus LCP media-split contract.

