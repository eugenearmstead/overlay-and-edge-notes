#!/usr/bin/env python3
"""Generate paired HTML from Markdown specs. Markdown is source of truth."""

from __future__ import annotations

import html
import json
import re
import sys
from datetime import date
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("PyYAML is required: python3 -c 'import yaml'")

ROOT = Path(__file__).resolve().parent.parent

AUTHOR_NAME = "Eugene Armstead"
AUTHOR_URL = "https://www.armsteadent.com/"
AUTHOR_GITHUB = "https://github.com/eugenearmstead"
SITE_ORIGIN = "https://eugenearmstead.github.io/overlay-and-edge-notes"
SITE_NAME = "Overlay and Edge Notes"
LICENSE_NAME = "CC-BY-4.0"
LICENSE_URL = "https://creativecommons.org/licenses/by/4.0/"
GOOGLE_FONTS_HREF = (
    "https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700"
    "&family=Source+Sans+3:wght@400;500;600&display=swap"
)

# Planned living IDs. Only rows with a Markdown file on disk are real links.
# Titles are English first; a search token MAY follow in parentheses.
CATALOG = [
    # Networking originals
    ("OEN-01", "networking", "01-overlay-ssh-byte-cliff", "Overlay SSH stalls at a byte cliff"),
    ("OEN-02", "networking", "02-chromium-tls-pmtu", "Chromium TLS fails while curl returns 200"),
    ("OEN-03", "networking", "03-router-vpn-dns-hijack", "Router VPN DNS hijack looks like a path-MTU problem"),
    ("OEN-04", "networking", "04-exit-tcpmss-after-ts-forward", "Exit-node TCP maximum-segment-size clamp after ts-forward never runs"),
    ("OEN-05", "networking", "05-exit-peerapi-dns-stub", "Exit-node overlay peer-API DNS stub (loopback only)"),
    ("OEN-06", "networking", "06-netfilter-off-v6-return", "Netfilter-off IPv6 return-path blackhole"),
    ("OEN-07", "networking", "07-crowdsec-capi-403", "CrowdSec Central API HTTP 403 from native health probes"),
    ("OEN-12", "networking", "12-consumer-wg-phantom-bridge", "Consumer-router WireGuard FORWARD only on a phantom bridge"),
    ("OEN-13", "networking", "13-overlay-underlay-ula-layers", "Overlay ≠ underlay ≠ tunnel unique-local ≠ LAN unique-local"),
    ("OEN-14", "networking", "14-exit-dns-is-peerapi", "Exit app DNS is overlay peer-API, not coordinator Unbound"),
    ("OEN-15", "networking", "15-split-host-vs-overlay-resolver", "Split host vs overlay resolver views on the coordinator VPS"),
    ("OEN-16", "networking", "16-commercial-wg-endpoint-rotation", "Commercial WireGuard endpoint rotation (IPv6, shuffle bag, hub watch)"),
    ("OEN-17", "networking", "17-gcp-overlay-exit", "Google Cloud overlay exit (IP forwarding, listen port, Identity-Aware Proxy)"),
    ("OEN-18", "networking", "18-per-node-changelog-contract", "Per-node changelog contract (repo + hashed on-device copy)"),
    ("OEN-19", "networking", "19-unbound-refuses-rd0", "Local Unbound REFUSES overlay peer-API queries with Recursion Desired off"),
    ("OEN-20", "networking", "20-lan-ula-happy-eyeballs-leak", "LAN unique-local + remote exit: IPv4 takes the exit, IPv6 leaks"),
    ("OEN-21", "networking", "21-shared-vpn-nat-crowdsec-ban", "Shared commercial-VPN network address translation: CrowdSec bans the whole house"),
    ("OEN-22", "networking", "22-delayed-wg-forward-wipe", "Delayed WireGuard start wipes FORWARD with no restart event"),
    ("OEN-23", "networking", "23-cloud-exit-accept-dns", "Cloud-exit accept-dns=true pretty-prints, breaks overlay peer-API DNS"),
    # Web originals
    ("OEN-08", "web", "08-worker-html-localhost-debug", "Do not ship localhost debug beacons in Worker HTML"),
    ("OEN-09", "web", "09-git-merge-is-not-a-live-worker", "Git merge is not a live Worker (timed Wrangler fallback)"),
    ("OEN-10", "web", "10-one-blocking-stylesheet-variable-fonts", "One generated blocking stylesheet and variable fonts"),
    ("OEN-11", "web", "11-worker-chat-wrapper-turnstile", "Worker chat wrapper, Turnstile, sanitize large-language-model drift"),
    # Supporting
    ("OEN-S01", "supporting", "s01-pmtud-size-ladder", "Don't-fragment ping size ladder (path MTU discovery)"),
    ("OEN-S02", "supporting", "s02-clamp-mss-to-pmtu-noop", "clamp-mss-to-pmtu is a no-op when ICMP is dropped"),
    ("OEN-S03", "supporting", "s03-transfer-matrix-controlpath", "1 KB vs 1 MB transfer matrix + ControlPath=none"),
    ("OEN-S04", "supporting", "s04-purge-cdn-after-deploy", "Purge the content delivery network after deploy"),
    ("OEN-S05", "supporting", "s05-tunnel-preview-stale-hit", "Tunnel preview HIT with a stale body"),
    ("OEN-S06", "supporting", "s06-do-not-ship-html-only", "Do not ship HTML-only"),
    ("OEN-S07", "supporting", "s07-git-merge-405-pending", "Git merge 405 while mergeability is pending"),
    ("OEN-S08", "supporting", "s08-canonical-disk-tmpfs-origin", "Canonical disk + tmpfs RAM origin on a Pi"),
    ("OEN-S09", "supporting", "s09-playwright-desktop-iphone-pixel", "Playwright Desktop + iPhone + Pixel"),
    ("OEN-S10", "supporting", "s10-file-before-image-deploy", "file(1) before image deploy"),
    ("OEN-S11", "supporting", "s11-overlay-rdp-acl", "Overlay session-mirror remote desktop and access-control list without deny"),
    ("OEN-S12", "supporting", "s12-rocket-loader-off", "Rocket Loader Off"),
    ("OEN-S13", "supporting", "s13-restart-always-missing-unit", "Restart=always on a missing unit hung the workstation"),
    ("OEN-S14", "supporting", "s14-broadcom-wg-sunreclaim", "Broadcom in-kernel WireGuard SUnreclaim (flow-cache/runner A/B fail)"),
    ("OEN-S15", "supporting", "s15-router-squashfs-jffs", "Router squashfs is always 100%; Save settings misses persistent overlay"),
    ("OEN-S16", "supporting", "s16-never-nft-flush", "Never nft flush / never start stock nftables.service"),
    ("OEN-S17", "supporting", "s17-coordination-cli-sqlite-wal", "Coordination CLI blocks on SQLite write-ahead log while serve is up"),
    ("OEN-S18", "supporting", "s18-do-not-set-exit-on-agent-workstation", "Do not set exit-node on the agent workstation"),
    ("OEN-S19", "supporting", "s19-push-small-overlay-snapshots", "Push small overlay snapshots; do not copy-pull large JSON"),
    ("OEN-S20", "supporting", "s20-ssh-open-no-banner", "SSH TCP-open with no banner is userspace-sick"),
    ("OEN-S21", "supporting", "s21-cloud-exit-hairpin-lan", "Cloud exit hairpins home LAN HTTP while overlay SSH still works"),
    ("OEN-S22", "supporting", "s22-iap-break-glass-kex", "Identity-Aware Proxy is break-glass; overlay SSH key-exchange can fail on some cloud VMs"),
    ("OEN-S23", "supporting", "s23-vpc-41641-useless-while-port-0", "Cloud firewall UDP 41641 is useless while overlay PORT=0"),
    ("OEN-S24", "supporting", "s24-lan-dns-sinkhole-0-0-0-0", "LAN DNS returning 0.0.0.0 is a sinkhole, not a site bug"),
    ("OEN-S25", "supporting", "s25-chrony-nts-address-family", "Network Time Security chrony address-family flags need a newer chrony than the distro"),
    ("OEN-S26", "supporting", "s26-wifi-vs-cellular-underlay", "Wi-Fi underlay vs cellular underlay to the same cloud exit"),
    ("OEN-S27", "supporting", "s27-iptables-nft-mark-before-fib", "iptables-nft PREROUTING MARK does not win before the forwarding information base"),
    ("OEN-S28", "supporting", "s28-sticky-reconnect-during-peerapi-outage", "Reconnect during overlay peer-API outage sticks after heal"),
    ("OEN-S29", "supporting", "s29-peerapi-stub-event-loop", "Overlay peer-API stub event-loop blocks; UDP receive queue grows"),
    ("OEN-S30", "supporting", "s30-ts-debug-mtu-below-1280", "TS_DEBUG_MTU below 1280 disables overlay IPv6"),
    ("OEN-S31", "supporting", "s31-prefixes-v6-needs-backfillips", "prefixes.v6 needs nodes backfillips, not restart alone"),
    ("OEN-S32", "supporting", "s32-dns-leak-test-not-v6-dataplane", "DNS leak-test green is not IPv6 data-plane green"),
    ("OEN-S33", "supporting", "s33-router-cron-path-set-e", "Consumer-router cron PATH omits curl; watchdog log() + set -e exits"),
    ("OEN-S34", "supporting", "s34-crowdsec-capi-login-budget", "CrowdSec free-tier Central API login budget"),
]

# RFC 2119 keywords, date-format placeholders, and short English words.
ACRONYM_EXCLUDE = {
    "MUST",
    "NOT",
    "SHOULD",
    "MAY",
    "SHALL",
    "WILL",
    "REQUIRED",
    "RECOMMENDED",
    "OPTIONAL",
    "OK",
    "UP",
    "NO",
    "OR",
    "IF",
    "TO",
    "IN",
    "ON",
    "AT",
    "BY",
    "IT",
    "BE",
    "AS",
    "AN",
    "AM",
    "PM",
    "US",
    "UK",
    "EU",
    "ID",
    "A",
    "B",
    "THE",
    "AND",
    "FOR",
    "WITH",
    "FROM",
    "THIS",
    "THAT",
    "ARE",
    "WAS",
    "YYYY",
    "MM",
    "DD",
    "HH",
    "YYYY-MM-DD",
    "CHANGELOG",
    "LICENSE",
    "CC-BY-4",
    "DOWN",
    "EXISTING",
    "FAIL",
    "FIX",
    "LACKS",
    "LEAK",
    "NEW",
    "NON",
    "PUSH",
    "TOP",
    "TRAP",
    "WORKS",
    "ALLOW",
    "GA",
    "PAT",
    "QUERY",
    "HEADER",
    "NR",
    "CANONICAL",
    "AFTER",
    "BEFORE",
    "SCOPE",
    "WRONG",
    "PING",
    "NEVER",
    "PAYLOAD",
    "AGENTS",
    "ASCII",
}

# Mixed-case tokens that the ALL-CAPS scanner misses.
MIXED_TOKENS = (
    "IPv4",
    "IPv6",
    "DoH",
    "PeerAPI",
    "PMTUD",
    "OpenSSH",
    "TCPMSS",
    "NDJSON",
    "ControlPath",
    "canIpForward",
    "PersistentKeepalive",
    "ClientHello",
    "MASQUERADE",
    "PREROUTING",
    "Happy-Eyeballs",
    "JSON-LD",
    "ICMPv6",
    "CrowdSec",
    "Unbound",
    "chrony",
    "systemd",
    "Cloudflare",
    "Chromium",
    "Android",
    "Playwright",
    "Turnstile",
    "Wrangler",
    "GitLab",
    "SQLite",
    "nftables",
    "nftables",
    "dnsmasq",
    "Chromium",
    "ICMPv6",
)

HOME_TERMS = [
    {"abbr": "OEN", "expansion": "Overlay and Edge Notes (this series)"},
    {"abbr": "SSH", "expansion": "Secure Shell"},
    {"abbr": "HTML", "expansion": "HyperText Markup Language"},
    {"abbr": "TCPMSS", "expansion": "iptables/nft target that sets TCP Maximum Segment Size"},
]

HOME_KEYWORDS = [
    "overlay SSH hang 1KB",
    "curl 200 chrome ERR_CONNECTION_CLOSED",
    "cscli capi 403",
    "ts-forward TCPMSS 0 packets",
    "PeerAPI DNS",
    "canIpForward exit node",
    "path MTU",
    "Tailscale SSH",
    "Headscale",
    "WireGuard MTU",
    "CrowdSec CAPI",
    "Cloudflare Worker",
    "Identity-Aware Proxy",
    "ASUSWRT-Merlin DNSVPN2",
    "llms.txt",
    "don't-fragment ping",
]

HOME_DESCRIPTION = (
    "Named overlay and edge traps searchable by the failure string: "
    "curl 200 chrome ERR_CONNECTION_CLOSED, cscli capi 403, overlay SSH hang 1KB. "
    "By Eugene Armstead."
)

DISCLOSURE_TERMS = [
    {"abbr": "OEN", "expansion": "Overlay and Edge Notes (this series)"},
    {"abbr": "CC-BY-4.0", "expansion": "Creative Commons Attribution 4.0 International"},
    {"abbr": "VPS", "expansion": "Virtual Private Server"},
    {"abbr": "LAN", "expansion": "Local Area Network"},
    {"abbr": "VPN", "expansion": "Virtual Private Network"},
    {"abbr": "WG", "expansion": "WireGuard"},
    {"abbr": "SSH", "expansion": "Secure Shell"},
    {"abbr": "IP", "expansion": "Internet Protocol"},
    {"abbr": "IPv4", "expansion": "Internet Protocol version 4"},
    {"abbr": "IPv6", "expansion": "Internet Protocol version 6"},
    {"abbr": "MTU", "expansion": "Maximum Transmission Unit"},
    {"abbr": "MSS", "expansion": "Maximum Segment Size"},
    {"abbr": "GCP", "expansion": "Google Cloud Platform"},
    {"abbr": "HTML", "expansion": "HyperText Markup Language"},
    {"abbr": "URL", "expansion": "Uniform Resource Locator"},
    {"abbr": "KB", "expansion": "kilobyte"},
]


def css_href(from_html: Path) -> str:
    depth = len(from_html.relative_to(ROOT).parts) - 1
    return ("../" * depth) + "assets/spec.css"


def href_from(from_html: Path, to: str) -> str:
    """Relative href from an HTML file to a repo-root path like 'index.html'."""
    depth = len(from_html.relative_to(ROOT).parts) - 1
    return ("../" * depth) + to


def normalize_terms(raw) -> list[dict]:
    if not raw:
        return []
    out: list[dict] = []
    for item in raw:
        if isinstance(item, dict):
            abbr = str(item.get("abbr") or item.get("term") or "").strip()
            expansion = str(item.get("expansion") or item.get("def") or "").strip()
        else:
            continue
        if not abbr or not expansion:
            raise SystemExit(f"terms entry needs abbr and expansion: {item!r}")
        out.append({"abbr": abbr, "expansion": expansion})
    return out


def terms_section_html(terms: list[dict]) -> str:
    if not terms:
        raise SystemExit("terms list is empty")
    rows = []
    for t in terms:
        rows.append(
            f"<dt>{html.escape(t['abbr'])}</dt><dd>{html.escape(t['expansion'])}</dd>"
        )
    return (
        '<section class="terms" aria-labelledby="terms-heading">'
        '<h2 id="terms-heading">Terms used on this page</h2>'
        '<p class="terms-kicker">Abbreviations and short forms</p>'
        f'<dl class="terms-list">{"".join(rows)}</dl>'
        "</section>"
    )


def strip_markdown_terms_section(md: str) -> str:
    return re.sub(
        r"^## Terms used on this page\n.*?(?=^## |\Z)",
        "",
        md,
        count=1,
        flags=re.S | re.M,
    )


def inject_terms_html(article_html: str, terms_html: str) -> str:
    m = re.search(
        r'(<h2 id="context">.*?</h2>.*?)(?=<h2 )',
        article_html,
        re.S,
    )
    if m:
        return article_html[: m.end(1)] + "\n" + terms_html + "\n" + article_html[m.end(1) :]
    m1 = re.search(r"(</h1>.*?</p>)", article_html, re.S)
    if m1:
        return article_html[: m1.end(1)] + "\n" + terms_html + "\n" + article_html[m1.end(1) :]
    return terms_html + "\n" + article_html


def find_acronyms(text: str) -> set[str]:
    found: set[str] = set()
    for m in re.finditer(r"\b[A-Z]{2,}(?:-[A-Z0-9]+)*\b", text):
        tok = m.group(0)
        if tok in ACRONYM_EXCLUDE or re.fullmatch(r"P\d+", tok):
            continue
        if tok.startswith("OEN"):
            found.add("OEN")
            continue
        found.add(tok)
    for token in MIXED_TOKENS:
        if token in text:
            found.add(token)
    if re.search(r"\bPi\b", text):
        found.add("Pi")
    if "nft" in text and re.search(r"\bnft\b", text):
        found.add("nft")
    return found


def assert_terms_cover(label: str, text: str, terms: list[dict]) -> None:
    have = {t["abbr"] for t in terms}
    missing = sorted(tok for tok in find_acronyms(text) if tok not in have)
    if missing:
        raise SystemExit(f"{label}: abbreviations missing from terms: {', '.join(missing)}")


def parse_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    meta = yaml.safe_load(parts[1]) or {}
    return meta, parts[2].lstrip("\n")


def rewrite_md_links(md: str) -> str:
    def repl(match: re.Match[str]) -> str:
        label, url = match.group(1), match.group(2)
        if url.endswith(".md") and not url.startswith(("http://", "https://")):
            url = url[:-3] + ".html"
        return f"[{label}]({url})"

    return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", repl, md)


def inline_format(text: str) -> str:
    out: list[str] = []
    i = 0
    n = len(text)
    while i < n:
        if text.startswith("`", i):
            end = text.find("`", i + 1)
            if end != -1:
                out.append("<code>" + html.escape(text[i + 1 : end]) + "</code>")
                i = end + 1
                continue
        if text.startswith("**", i):
            end = text.find("**", i + 2)
            if end != -1:
                out.append("<strong>" + inline_format(text[i + 2 : end]) + "</strong>")
                i = end + 2
                continue
        if text.startswith("[", i):
            m = re.match(r"\[([^\]]+)\]\(([^)]+)\)", text[i:])
            if m:
                label, url = m.group(1), m.group(2)
                out.append(
                    f'<a href="{html.escape(url, quote=True)}">{inline_format(label)}</a>'
                )
                i += m.end()
                continue
        if text[i] == "*" and (i + 1 < n and text[i + 1] != " "):
            end = text.find("*", i + 1)
            if end != -1:
                out.append("<em>" + inline_format(text[i + 1 : end]) + "</em>")
                i = end + 1
                continue
        out.append(html.escape(text[i]))
        i += 1
    return "".join(out)


def md_to_html(md: str) -> str:
    md = rewrite_md_links(md)
    fences: list[str] = []

    def stash_fence(match: re.Match[str]) -> str:
        lang = match.group(1) or ""
        code = html.escape(match.group(2).rstrip("\n"))
        cls = f' class="language-{html.escape(lang)}"' if lang else ""
        fences.append(f"<pre><code{cls}>{code}</code></pre>")
        return f"\n\n<!--FENCE{len(fences) - 1}-->\n\n"

    md = re.sub(r"```(\w*)\n(.*?)```", stash_fence, md, flags=re.S)

    lines = md.splitlines()
    blocks: list[str] = []
    i = 0

    def flush_para(buf: list[str]) -> None:
        if buf:
            blocks.append("<p>" + inline_format(" ".join(buf)) + "</p>")
            buf.clear()

    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        fence_m = re.fullmatch(r"<!--FENCE(\d+)-->", line.strip())
        if fence_m:
            blocks.append(fences[int(fence_m.group(1))])
            i += 1
            continue
        if line.startswith("### "):
            blocks.append("<h3>" + inline_format(line[4:].strip()) + "</h3>")
            i += 1
            continue
        if line.startswith("## "):
            title = line[3:].strip()
            hid = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
            extra = ' class="must-not"' if title.upper().startswith("MUST NOT") else ""
            blocks.append(f'<h2 id="{html.escape(hid)}"{extra}>' + inline_format(title) + "</h2>")
            i += 1
            continue
        if line.startswith("# "):
            blocks.append("<h1>" + inline_format(line[2:].strip()) + "</h1>")
            i += 1
            continue
        if line.startswith(">"):
            q: list[str] = []
            while i < len(lines) and lines[i].startswith(">"):
                q.append(lines[i][1:].lstrip())
                i += 1
            blocks.append("<blockquote><p>" + inline_format(" ".join(q)) + "</p></blockquote>")
            continue
        if line.startswith("|") and i + 1 < len(lines) and re.match(r"^\|?\s*:?-+:?\s*\|", lines[i + 1]):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append(lines[i])
                i += 1
            header = [c.strip() for c in rows[0].strip("|").split("|")]
            body_rows = rows[2:]
            thead = "<tr>" + "".join(f"<th>{inline_format(c)}</th>" for c in header) + "</tr>"
            tbody = []
            for row in body_rows:
                cells = [c.strip() for c in row.strip("|").split("|")]
                tbody.append("<tr>" + "".join(f"<td>{inline_format(c)}</td>" for c in cells) + "</tr>")
            blocks.append("<table><thead>" + thead + "</thead><tbody>" + "".join(tbody) + "</tbody></table>")
            continue
        ol_m = re.match(r"^(\d+)\.\s+(.*)$", line)
        if ol_m or line.startswith("- ") or line.startswith("* "):
            ordered = bool(ol_m)
            tag = "ol" if ordered else "ul"
            items: list[str] = []
            while i < len(lines):
                cur = lines[i]
                if not cur.strip():
                    j = i + 1
                    while j < len(lines) and not lines[j].strip():
                        j += 1
                    if j < len(lines) and (
                        (ordered and re.match(r"^\d+\.\s+", lines[j]))
                        or (not ordered and lines[j].startswith(("- ", "* ")))
                    ):
                        i = j
                        continue
                    break
                mnum = re.match(r"^(\d+)\.\s+(.*)$", cur)
                if ordered and mnum:
                    item_bits = [mnum.group(2)]
                    i += 1
                    while i < len(lines) and (lines[i].startswith("   ") or lines[i].startswith("\t")):
                        item_bits.append(lines[i].strip())
                        i += 1
                    items.append("<li>" + "<br>\n".join(inline_format(b) for b in item_bits) + "</li>")
                    continue
                if not ordered and (cur.startswith("- ") or cur.startswith("* ")):
                    item_bits = [cur[2:]]
                    i += 1
                    while i < len(lines) and (lines[i].startswith("   ") or lines[i].startswith("\t")):
                        item_bits.append(lines[i].strip())
                        i += 1
                    items.append("<li>" + "<br>\n".join(inline_format(b) for b in item_bits) + "</li>")
                    continue
                break
            blocks.append(f"<{tag}>" + "".join(items) + f"</{tag}>")
            continue
        def is_block_start(s: str) -> bool:
            return bool(
                s.startswith(("## ", "### ", "# ", "> ", ">"))
                or s.startswith("|")
                or s.startswith("- ")
                or s.startswith("* ")
                or re.match(r"^\d+\.\s+", s)
                or re.fullmatch(r"<!--FENCE\d+-->", s.strip())
            )

        para = []
        while i < len(lines) and lines[i].strip() and not is_block_start(lines[i]):
            para.append(lines[i].strip())
            i += 1
        if para:
            flush_para(para)
        else:
            # Always advance: lines such as `**Author:**` or `---` used to stall here.
            blocks.append("<p>" + inline_format(lines[i].strip()) + "</p>")
            i += 1
        continue

    return "\n".join(blocks)


def extract_howto_steps(md: str) -> list[dict]:
    m = re.search(r"^## Procedure\n(.*?)(?=\n## |\Z)", md, re.S | re.M)
    if not m:
        return []
    block = m.group(1)
    steps = []
    for m2 in re.finditer(r"^\s*(\d+)\.\s+\*\*(.+?)\*\*\s*\n((?:[ \t]+.*\n)*)", block, re.M):
        name = m2.group(2).strip()
        body = m2.group(3)
        bits = []
        for ln in body.splitlines():
            ln = ln.strip()
            if not ln:
                continue
            ln = re.sub(r"^[-*]\s+\*\*(.+?)\*\*\s*", r"\1 ", ln)
            bits.append(ln)
        text = " ".join(bits)
        steps.append(
            {
                "@type": "HowToStep",
                "position": int(m2.group(1)),
                "name": name,
                "text": text[:500] or name,
            }
        )
    return steps


def person_ld() -> dict:
    return {
        "@type": "Person",
        "name": AUTHOR_NAME,
        "url": AUTHOR_URL,
        "sameAs": [AUTHOR_GITHUB],
    }


def keywords_list(meta: dict | None) -> list[str]:
    raw = (meta or {}).get("keywords") or []
    if isinstance(raw, str):
        raw = [p.strip() for p in raw.split(",")]
    out: list[str] = []
    seen: set[str] = set()
    for item in raw:
        k = str(item).strip()
        if not k or k.lower() in seen:
            continue
        seen.add(k.lower())
        out.append(k)
    return out


def keywords_joined(keywords: list[str]) -> str:
    return ", ".join(keywords)


def json_ld_spec(meta: dict, canonical: str, howto: list[dict]) -> str:
    desc = meta.get("description") or meta.get("title") or SITE_NAME
    article = {
        "@type": "TechArticle",
        "@id": canonical + "#article",
        "headline": meta.get("title"),
        "description": desc,
        "datePublished": str(meta.get("date_published") or ""),
        "author": person_ld(),
        "url": canonical,
        "identifier": meta.get("id"),
        "license": LICENSE_URL,
        "inLanguage": "en",
    }
    kws = keywords_list(meta)
    if kws:
        article["keywords"] = kws
    graph = [article]
    if howto:
        graph.append(
            {
                "@type": "HowTo",
                "name": meta.get("title"),
                "description": desc,
                "author": person_ld(),
                "step": howto,
            }
        )
    return json.dumps({"@context": "https://schema.org", "@graph": graph}, indent=2)


def json_ld_website(
    canonical: str, title: str, desc: str, keywords: list[str] | None = None
) -> str:
    data = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": SITE_NAME,
        "url": canonical,
        "description": desc,
        "author": person_ld(),
        "publisher": person_ld(),
        "license": LICENSE_URL,
    }
    if keywords:
        data["keywords"] = keywords
    return json.dumps(data, indent=2)


def author_head_tags() -> str:
    return f"""    <meta name="author" content="{html.escape(AUTHOR_NAME)}">
    <meta name="citation_author" content="{html.escape(AUTHOR_NAME)}">
    <meta name="dcterms.creator" content="{html.escape(AUTHOR_NAME)}">
    <link rel="author" href="{html.escape(AUTHOR_URL, quote=True)}">
    <meta property="article:author" content="{html.escape(AUTHOR_NAME)}">
    <meta property="og:see_also" content="{html.escape(AUTHOR_URL, quote=True)}">"""


def nav_html(page: Path) -> str:
    h = lambda p: href_from(page, p)
    return f"""    <nav class="site-nav" aria-label="Site">
      <a href="{h('index.html')}">Home</a>
      <a href="{h('DISCLOSURE.html')}">Disclosure</a>
      <a href="{h('changelog.html')}">Changelog</a>
      <a href="{h('editions/2026.html')}">2026</a>
      <a href="{h('AGENTS.md')}">AGENTS.md</a>
      <a href="{h('index.html')}#networking">Networking</a>
      <a href="{h('index.html')}#web">Web</a>
      <a href="{h('index.html')}#supporting">Supporting</a>
    </nav>"""


def footer_html() -> str:
    return f"""    <p class="byline">Written by <a href="{html.escape(AUTHOR_URL, quote=True)}">{html.escape(AUTHOR_NAME)}</a> · <a href="{html.escape(AUTHOR_URL, quote=True)}">{html.escape(AUTHOR_URL)}</a> · <a rel="license" href="{html.escape(LICENSE_URL, quote=True)}">{LICENSE_NAME}</a></p>
    <p class="license-line">Living field notes. Stable IDs. Do not copy private inventory into public text.</p>"""


def wrap_page(
    *,
    out_path: Path,
    title: str,
    description: str,
    canonical: str,
    body: str,
    json_ld: str,
    og_type: str = "article",
    published: str | None = None,
    crumbs: list[tuple[str, str | None]] | None = None,
    keywords: list[str] | None = None,
) -> str:
    css = css_href(out_path)
    llms = href_from(out_path, "llms.txt")
    pub = ""
    if published:
        pub = f'\n    <meta property="article:published_time" content="{html.escape(str(published))}">'
    kw_tags = ""
    if keywords:
        joined = html.escape(keywords_joined(keywords))
        kw_tags = (
            f'\n    <meta name="keywords" content="{joined}">'
            f'\n    <meta name="citation_keywords" content="{joined}">'
        )
    crumb_html = ""
    if crumbs:
        items = []
        for label, url in crumbs:
            if url:
                items.append(f'<li><a href="{html.escape(url, quote=True)}">{html.escape(label)}</a></li>')
            else:
                items.append(f"<li>{html.escape(label)}</li>")
        crumb_html = f'<nav class="breadcrumb" aria-label="Breadcrumb"><ol>{"".join(items)}</ol></nav>'
    return f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{html.escape(title)}</title>
    <meta name="description" content="{html.escape(description)}">{kw_tags}
    <link rel="canonical" href="{html.escape(canonical, quote=True)}">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link rel="stylesheet" href="{html.escape(GOOGLE_FONTS_HREF, quote=True)}">
    <link rel="stylesheet" href="{html.escape(css, quote=True)}">
    <link rel="describedby" href="{html.escape(llms, quote=True)}">
{author_head_tags()}
    <meta property="og:title" content="{html.escape(title)}">
    <meta property="og:description" content="{html.escape(description)}">
    <meta property="og:url" content="{html.escape(canonical, quote=True)}">
    <meta property="og:type" content="{html.escape(og_type)}">{pub}
    <script type="application/ld+json">
{json_ld}
    </script>
  </head>
  <body>
    <a class="skip-link" href="#main">Skip to content</a>
    <header class="site-header">
      <div class="site-header-inner">
        <p class="site-title"><a href="{href_from(out_path, 'index.html')}">{html.escape(SITE_NAME)}</a></p>
        <p class="site-tag">Public field notes by {html.escape(AUTHOR_NAME)}</p>
{nav_html(out_path)}
      </div>
    </header>
    {crumb_html}
    <main id="main">
{body}
    </main>
    <footer class="site-footer">
      <div class="site-footer-inner">
{footer_html()}
      </div>
    </footer>
  </body>
</html>
"""


def built_path(section: str, slug: str) -> Path:
    return ROOT / section / f"{slug}.md"


def is_built(section: str, slug: str) -> bool:
    return built_path(section, slug).is_file()


def render_spec(md_path: Path) -> None:
    meta, body = parse_frontmatter(md_path.read_text(encoding="utf-8"))
    for key in ("author", "author_url", "terms"):
        if key not in meta:
            raise SystemExit(f"{md_path}: missing YAML {key}")
    if meta.get("author") != AUTHOR_NAME:
        raise SystemExit(f"{md_path}: author must be {AUTHOR_NAME!r}")
    if meta.get("author_url") != AUTHOR_URL:
        raise SystemExit(f"{md_path}: author_url must be {AUTHOR_URL!r}")
    terms = normalize_terms(meta.get("terms"))
    if not terms:
        raise SystemExit(f"{md_path}: terms must list every abbreviation on the page")
    spec_id = meta.get("id", "")
    title = meta.get("title") or md_path.stem
    desc = meta.get("description") or title
    rel_html = md_path.relative_to(ROOT).with_suffix(".html")
    out_path = ROOT / rel_html
    canonical = meta.get("canonical") or f"{SITE_ORIGIN}/{rel_html.as_posix()}"
    body_for_html = strip_markdown_terms_section(body)
    scan_text = f"{title}\n{desc}\n{body_for_html}"
    assert_terms_cover(str(md_path.relative_to(ROOT)), scan_text, terms)
    article_html = md_to_html(body_for_html)
    # Drop duplicate H1 if markdown repeats the title
    article_html = re.sub(r"^<h1>.*?</h1>\n?", "", article_html, count=1)
    article_html = inject_terms_html(article_html, terms_section_html(terms))
    howto = extract_howto_steps(body_for_html)
    ident = f"{spec_id}: " if spec_id else ""
    page_title = f"{ident}{title} — {SITE_NAME}"
    crumbs = [
        ("Home", href_from(out_path, "index.html")),
        (md_path.parent.name.replace("-", " ").title(), href_from(out_path, "index.html") + "#" + md_path.parent.name),
        (spec_id or title, None),
    ]
    kind = meta.get("kind", "spec")
    meta_line = f'<p class="meta-line"><span>{html.escape(str(spec_id))}</span> · {html.escape(str(kind))} · edition {html.escape(str(meta.get("edition", 1)))} · {html.escape(str(meta.get("date_published", "")))}</p>'
    body_wrapped = f"""      <article>
        <h1>{html.escape(title)}</h1>
        {meta_line}
        {article_html}
      </article>"""
    html_out = wrap_page(
        out_path=out_path,
        title=page_title,
        description=desc,
        canonical=canonical,
        body=body_wrapped,
        json_ld=json_ld_spec(meta, canonical, howto),
        published=str(meta.get("date_published") or ""),
        crumbs=crumbs,
        keywords=keywords_list(meta),
    )
    out_path.write_text(html_out, encoding="utf-8")
    print(f"wrote {out_path.relative_to(ROOT)}")


def catalog_list_html(section: str, from_page: Path) -> str:
    items = []
    for spec_id, sec, slug, title in CATALOG:
        if sec != section:
            continue
        if is_built(sec, slug):
            href = href_from(from_page, f"{sec}/{slug}.html")
            items.append(
                f'<li><span class="id">{html.escape(spec_id)}</span><span><a href="{html.escape(href, quote=True)}">{html.escape(title)}</a></span></li>'
            )
        else:
            items.append(
                f'<li><span class="id">{html.escape(spec_id)}</span><span>{html.escape(title)} <span class="forthcoming">(forthcoming)</span></span></li>'
            )
    return '<ol class="catalog">' + "".join(items) + "</ol>"


def write_index() -> None:
    out_path = ROOT / "index.html"
    canonical = f"{SITE_ORIGIN}/"
    desc = HOME_DESCRIPTION
    home_prose = (
        f"{SITE_NAME}\n{desc}\n"
        "Named traps with replicable procedures. Stable IDs that do not reset by year. "
        "Markdown is the source of truth; HTML is generated. "
        "This edition ships original specs and supporting methods. "
        "Year pages are indexes, not copies of specs. "
        "Disclosure, changelog, agents, crawlers. "
        "How to find these notes. Search the error you hit, not a private lab name. "
        "Notes live on GitHub Pages. Agents start at llms.txt and optionally llms-full.txt. "
        "Example searches overlay SSH hang ts-forward TCPMSS 0 packets."
    )
    assert_terms_cover("index.html", home_prose, HOME_TERMS)
    terms_html = terms_section_html(HOME_TERMS)
    pages_url = html.escape(f"{SITE_ORIGIN}/", quote=True)
    body = f"""      <div class="page-body">
        <h1>{html.escape(SITE_NAME)}</h1>
        <p class="lede">Named traps with replicable procedures. Stable IDs that do not reset by year. Markdown is the source of truth; HTML is generated.</p>
        <p>This edition ships twenty-three original specs and thirty-four supporting methods. Year pages are indexes, not copies of specs.</p>
        {terms_html}
        <h2 id="find">How to find these notes</h2>
        <p>Search the error you hit, not a private lab name.</p>
        <ul>
          <li>Notes live at <a href="{pages_url}">{html.escape(SITE_ORIGIN)}/</a></li>
          <li>Agents start at <a href="{href_from(out_path, 'llms.txt')}"><code>llms.txt</code></a> (and optionally <a href="{href_from(out_path, 'llms-full.txt')}"><code>llms-full.txt</code></a>)</li>
          <li>Example searches: <code>curl 200 chrome ERR_CONNECTION_CLOSED</code>, <code>cscli capi 403</code>, overlay SSH hang / <code>ts-forward TCPMSS 0 packets</code></li>
        </ul>
        <h2 id="about">About</h2>
        <ul>
          <li><a href="{href_from(out_path, 'DISCLOSURE.html')}">Disclosure and license</a></li>
          <li><a href="{href_from(out_path, 'AGENTS.md')}">How agents should apply it (AGENTS.md)</a></li>
          <li><a href="{href_from(out_path, 'changelog.html')}">Series changelog</a></li>
          <li><a href="{href_from(out_path, 'llms.txt')}">llms.txt</a> for crawlers and coding agents</li>
        </ul>
        <h2 id="networking">Original specs — Networking</h2>
        {catalog_list_html("networking", out_path)}
        <h2 id="web">Original specs — Web and Cloudflare</h2>
        {catalog_list_html("web", out_path)}
        <h2 id="supporting">Supporting specs</h2>
        {catalog_list_html("supporting", out_path)}
        <h2 id="editions">Editions</h2>
        <p><a href="{href_from(out_path, 'editions/2026.html')}">2026 year index</a> — what first shipped this calendar year. Not a copy of the specs.</p>
      </div>"""
    html_out = wrap_page(
        out_path=out_path,
        title=f"{SITE_NAME} — {AUTHOR_NAME}",
        description=desc,
        canonical=canonical,
        body=body,
        json_ld=json_ld_website(canonical, SITE_NAME, desc, HOME_KEYWORDS),
        og_type="website",
        crumbs=[("Home", None)],
        keywords=HOME_KEYWORDS,
    )
    out_path.write_text(html_out, encoding="utf-8")
    print("wrote index.html")


def write_disclosure() -> None:
    md_path = ROOT / "DISCLOSURE.md"
    meta, body = parse_frontmatter(md_path.read_text(encoding="utf-8"))
    terms = normalize_terms(meta.get("terms") or DISCLOSURE_TERMS)
    out_path = ROOT / "DISCLOSURE.html"
    canonical = f"{SITE_ORIGIN}/DISCLOSURE.html"
    title = meta.get("title") or "Disclosure and license"
    desc = meta.get("description") or title
    body_for_html = strip_markdown_terms_section(body)
    assert_terms_cover("DISCLOSURE.md", f"{title}\n{desc}\n{body_for_html}", terms)
    inner = md_to_html(body_for_html)
    inner = re.sub(r"^<h1>.*?</h1>\n?", "", inner, count=1)
    inner = inject_terms_html(inner, terms_section_html(terms))
    body_wrapped = f"""      <article>
        <h1>{html.escape(title)}</h1>
        {inner}
      </article>"""
    html_out = wrap_page(
        out_path=out_path,
        title=f"{title} — {SITE_NAME}",
        description=desc,
        canonical=canonical,
        body=body_wrapped,
        json_ld=json_ld_website(canonical, title, desc, keywords_list(meta)),
        og_type="article",
        published=str(meta.get("date_published") or date.today().isoformat()),
        crumbs=[("Home", href_from(out_path, "index.html")), ("Disclosure", None)],
        keywords=keywords_list(meta),
    )
    out_path.write_text(html_out, encoding="utf-8")
    print("wrote DISCLOSURE.html")


def llm_one_line(md_path: Path, fallback: str) -> str:
    meta, _body = parse_frontmatter(md_path.read_text(encoding="utf-8"))
    blurb = str(meta.get("description") or fallback).strip()
    blurb = " ".join(blurb.split())
    if len(blurb) > 280:
        blurb = blurb[:277].rstrip() + "..."
    return blurb


def write_llms_txt() -> None:
    lines = [
        f"# {SITE_NAME}",
        "",
        f"> Field notes by {AUTHOR_NAME} ({AUTHOR_URL}). Living specs with stable IDs. CC-BY-4.0. Placeholders only: <cloud-vps>, <lan-pi>, <overlay-peer>, <exit-node>, <wg-iface>, <gcp-nic>. Search the failure string: curl 200 chrome ERR_CONNECTION_CLOSED; cscli capi 403; ts-forward TCPMSS 0 packets.",
        "",
        "## How to find a spec",
        "",
        "- Search the error you hit, not a private lab name.",
        f"- Notes live at [{SITE_ORIGIN}/]({SITE_ORIGIN}/).",
        f"- Agents start at this file and optionally [{SITE_ORIGIN}/llms-full.txt]({SITE_ORIGIN}/llms-full.txt).",
        "- Example searches: curl 200 chrome ERR_CONNECTION_CLOSED; cscli capi 403; overlay SSH hang / ts-forward TCPMSS 0 packets.",
        "",
        "## Original specs (built)",
        "",
    ]
    for spec_id, section, slug, title in CATALOG:
        if not is_built(section, slug):
            continue
        if not spec_id.startswith("OEN-S"):
            url = f"{SITE_ORIGIN}/{section}/{slug}.html"
            blurb = llm_one_line(ROOT / section / f"{slug}.md", title)
            lines.append(f"- [{spec_id} {title}]({url}): {blurb}")
    lines += ["", "## Supporting specs (built)", ""]
    for spec_id, section, slug, title in CATALOG:
        if not is_built(section, slug):
            continue
        if spec_id.startswith("OEN-S"):
            url = f"{SITE_ORIGIN}/{section}/{slug}.html"
            blurb = llm_one_line(ROOT / section / f"{slug}.md", title)
            lines.append(f"- [{spec_id} {title}]({url}): {blurb}")
    lines += [
        "",
        "## About",
        "",
        f"- [Disclosure and license]({SITE_ORIGIN}/DISCLOSURE.html): author, site, CC-BY-4.0",
        f"- [AGENTS.md]({SITE_ORIGIN}/AGENTS.md): how coding agents MUST apply these specs",
        f"- [Home]({SITE_ORIGIN}/): citation index of all living IDs",
        f"- [2026 edition]({SITE_ORIGIN}/editions/2026.html): what first shipped this year",
        f"- [Changelog]({SITE_ORIGIN}/changelog.html): monthly series log",
        "",
    ]
    (ROOT / "llms.txt").write_text("\n".join(lines), encoding="utf-8")
    print("wrote llms.txt")


def write_sitemap() -> None:
    urls = [
        f"{SITE_ORIGIN}/",
        f"{SITE_ORIGIN}/DISCLOSURE.html",
        f"{SITE_ORIGIN}/changelog.html",
        f"{SITE_ORIGIN}/editions/2026.html",
    ]
    for _spec_id, section, slug, _title in CATALOG:
        if is_built(section, slug):
            urls.append(f"{SITE_ORIGIN}/{section}/{slug}.html")
    chunks = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for loc in urls:
        chunks.append(f"  <url><loc>{html.escape(loc)}</loc></url>")
    chunks.append("</urlset>\n")
    (ROOT / "sitemap.xml").write_text("\n".join(chunks), encoding="utf-8")
    print("wrote sitemap.xml")


def write_robots() -> None:
    text = (
        "User-agent: *\n"
        "Allow: /\n"
        "\n"
        f"Sitemap: {SITE_ORIGIN}/sitemap.xml\n"
    )
    (ROOT / "robots.txt").write_text(text, encoding="utf-8")
    print("wrote robots.txt")


def write_frontmatter_page(md_path: Path, *, crumb: str) -> None:
    meta, body = parse_frontmatter(md_path.read_text(encoding="utf-8"))
    terms = normalize_terms(meta.get("terms"))
    if not terms:
        raise SystemExit(f"{md_path}: missing YAML terms")
    rel_html = md_path.relative_to(ROOT).with_suffix(".html")
    out_path = ROOT / rel_html
    out_path.parent.mkdir(parents=True, exist_ok=True)
    canonical = meta.get("canonical") or f"{SITE_ORIGIN}/{rel_html.as_posix()}"
    title = meta.get("title") or md_path.stem
    desc = meta.get("description") or title
    body_for_html = strip_markdown_terms_section(body)
    assert_terms_cover(str(md_path.relative_to(ROOT)), f"{title}\n{desc}\n{body_for_html}", terms)
    inner = md_to_html(body_for_html)
    inner = re.sub(r"^<h1>.*?</h1>\n?", "", inner, count=1)
    inner = inject_terms_html(inner, terms_section_html(terms))
    body_wrapped = f"""      <article>
        <h1>{html.escape(title)}</h1>
        {inner}
      </article>"""
    html_out = wrap_page(
        out_path=out_path,
        title=f"{title} — {SITE_NAME}",
        description=desc,
        canonical=canonical,
        body=body_wrapped,
        json_ld=json_ld_website(canonical, title, desc, keywords_list(meta)),
        og_type="article",
        published=str(meta.get("date_published") or date.today().isoformat()),
        crumbs=[("Home", href_from(out_path, "index.html")), (crumb, None)],
        keywords=keywords_list(meta),
    )
    out_path.write_text(html_out, encoding="utf-8")
    print(f"wrote {rel_html.as_posix()}")


def write_llms_full() -> None:
    chunks = [
        f"# {SITE_NAME} (full Markdown)",
        "",
        f"> Field notes by {AUTHOR_NAME} ({AUTHOR_URL}). CC-BY-4.0.",
        "",
    ]
    for _spec_id, section, slug, _title in CATALOG:
        md_path = ROOT / section / f"{slug}.md"
        if not md_path.is_file():
            continue
        chunks.append(f"\n\n---\n\n{md_path.read_text(encoding='utf-8').rstrip()}\n")
    (ROOT / "llms-full.txt").write_text("".join(chunks), encoding="utf-8")
    print("wrote llms-full.txt")


def main() -> None:
    for folder in ("networking", "web", "supporting"):
        d = ROOT / folder
        if not d.is_dir():
            continue
        for md_path in sorted(d.glob("*.md")):
            render_spec(md_path)
    if (ROOT / "DISCLOSURE.md").is_file():
        write_disclosure()
    if (ROOT / "CHANGELOG.md").is_file():
        write_frontmatter_page(ROOT / "CHANGELOG.md", crumb="Changelog")
        # Pages URL is changelog.html at repo root (CHANGELOG.md → CHANGELOG.html).
        # Copy/alias to changelog.html for nav.
        src = ROOT / "CHANGELOG.html"
        dst = ROOT / "changelog.html"
        if src.is_file():
            dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
            print("wrote changelog.html")
    ed = ROOT / "editions" / "2026.md"
    if ed.is_file():
        write_frontmatter_page(ed, crumb="2026")
    write_index()
    write_llms_txt()
    write_llms_full()
    write_sitemap()
    write_robots()


if __name__ == "__main__":
    main()
