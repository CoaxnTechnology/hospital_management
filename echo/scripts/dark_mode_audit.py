#!/usr/bin/env python3
"""
Dark Mode Audit & Auto-Fix Script
==================================
Scans all HTML templates and hospital-theme.css to:
  1. Detect hardcoded colors not covered by dark mode
  2. Auto-generate missing CSS overrides into hospital-theme.css
  3. Print a per-file report of remaining manual fixes needed

Usage:
  python scripts/dark_mode_audit.py          # report only
  python scripts/dark_mode_audit.py --fix    # report + auto-apply CSS fixes
"""

import os
import re
import sys
import argparse
from pathlib import Path
from collections import defaultdict

# ── Paths ────────────────────────────────────────────────────────────────────
BASE      = Path(__file__).resolve().parent.parent
TEMPLATES = BASE / "templates"
CSS_FILE  = BASE / "public/static/css/core/hospital-theme.css"

# ── Colour detection ─────────────────────────────────────────────────────────
HEX_RE   = re.compile(r'#([0-9a-fA-F]{3,8})\b')
RGB_RE   = re.compile(r'rgba?\(\s*\d+\s*,\s*\d+\s*,\s*\d+')
NAMED_RE = re.compile(
    r'\b(white|black|silver|gray|grey|red|blue|green|yellow|orange|purple|pink|brown|navy)\b',
    re.I
)

# Bootstrap / Keenthemes classes that hardcode light backgrounds
LIGHT_BG_CLASSES = {
    "bg-white":            ("var(--hp-card-bg)",                   "Background"),
    "bg-light":            ("rgba(255,255,255,0.04)",               "Background"),
    "bg-gray-100":         ("rgba(255,255,255,0.04)",               "Background"),
    "bg-gray-200":         ("rgba(255,255,255,0.06)",               "Background"),
    "bg-light-primary":    ("rgba(74,158,255,0.12)",                "Background"),
    "bg-light-success":    ("rgba(45,212,191,0.12)",                "Background"),
    "bg-light-danger":     ("rgba(248,113,113,0.12)",               "Background"),
    "bg-light-warning":    ("rgba(251,146,60,0.12)",                "Background"),
    "bg-light-info":       ("rgba(167,139,250,0.12)",               "Background"),
    "bg-light-secondary":  ("rgba(255,255,255,0.06)",               "Background"),
    "bg-secondary":        ("rgba(255,255,255,0.08)",               "Background"),
}

# ── CSS dark-block parser ─────────────────────────────────────────────────────
DARK_SELECTOR_RE = re.compile(
    r'html\[data-hp-theme=["\']dark["\']\]\s+([^{,\n]+)',
    re.M
)

def load_existing_dark_selectors(css_text: str) -> set:
    """Return set of selectors already covered in the dark block."""
    return {m.group(1).strip() for m in DARK_SELECTOR_RE.finditer(css_text)}


# ── Inline-style scanner ──────────────────────────────────────────────────────
INLINE_STYLE_RE = re.compile(r'style\s*=\s*["\']([^"\']+)["\']', re.I)
STYLE_BLOCK_RE  = re.compile(r'<style[^>]*>(.*?)</style>', re.S | re.I)
CSS_PROP_RE     = re.compile(
    r'(background(?:-color)?|color|border(?:-color)?)\s*:\s*([^;}\n]+)',
    re.I
)

def has_hardcoded_color(value: str) -> bool:
    v = value.strip()
    if "var(--" in v:          return False   # already using a variable
    if HEX_RE.search(v):       return True
    if RGB_RE.search(v):       return True
    if NAMED_RE.search(v):     return True
    return False


def scan_inline_styles(html: str, filepath: str):
    """Return list of (line_no, snippet, suggestion) for inline style= attrs."""
    issues = []
    lines  = html.splitlines()
    for i, line in enumerate(lines, 1):
        for m in INLINE_STYLE_RE.finditer(line):
            style_val = m.group(1)
            for prop_m in CSS_PROP_RE.finditer(style_val):
                prop, val = prop_m.group(1), prop_m.group(2)
                if has_hardcoded_color(val):
                    issues.append({
                        "line": i,
                        "type": "inline-style",
                        "prop": prop.strip(),
                        "value": val.strip(),
                        "raw": line.strip()[:120],
                        "fix": "MANUAL — add a CSS class with var(--hp-*) override",
                    })
    return issues


def scan_style_blocks(html: str, filepath: str):
    """Return list of issues inside <style> blocks."""
    issues = []
    for block_m in STYLE_BLOCK_RE.finditer(html):
        block    = block_m.group(1)
        block_start = html[:block_m.start()].count('\n') + 1
        block_lines = block.splitlines()
        # Check if a dark override already exists in this block
        dark_overrides = set(re.findall(r'html\[data-hp-theme=["\']dark["\']\][^{]+', block))
        for j, bline in enumerate(block_lines, 1):
            for prop_m in CSS_PROP_RE.finditer(bline):
                prop, val = prop_m.group(1), prop_m.group(2)
                if has_hardcoded_color(val) and 'dark' not in bline:
                    issues.append({
                        "line": block_start + j,
                        "type": "style-block",
                        "prop": prop.strip(),
                        "value": val.strip(),
                        "raw": bline.strip()[:120],
                        "fix": "Add html[data-hp-theme='dark'] override in same <style> block",
                    })
    return issues


def scan_bg_classes(html: str):
    """Return list of (line_no, class) for hardcoded bg- utility classes."""
    issues = []
    lines = html.splitlines()
    for i, line in enumerate(lines, 1):
        class_attr = re.search(r'class\s*=\s*["\']([^"\']+)["\']', line)
        if not class_attr:
            continue
        classes = class_attr.group(1).split()
        for cls in classes:
            if cls in LIGHT_BG_CLASSES:
                issues.append({
                    "line": i,
                    "type": "bg-class",
                    "class": cls,
                    "dark_value": LIGHT_BG_CLASSES[cls][0],
                    "fix": f"Already covered by .{cls} dark rule in hospital-theme.css",
                })
    return issues


# ── CSS file scanner ──────────────────────────────────────────────────────────
CSS_RULE_RE = re.compile(
    r'([.#][^{/@\n][^{]*)\{[^}]*?(background(?:-color)?|color)\s*:\s*([^;}\n]+)',
    re.M
)

def scan_css_missing_dark(css_text: str, dark_selectors: set):
    """Find CSS selectors with hardcoded colors that lack a dark counterpart."""
    issues = []
    in_dark_block = False
    for m in CSS_RULE_RE.finditer(css_text):
        selector = m.group(1).strip()
        prop     = m.group(2).strip()
        val      = m.group(3).strip()
        if 'data-hp-theme' in selector:
            continue   # already a dark rule
        if not has_hardcoded_color(val):
            continue
        # Check if any dark selector covers this
        covered = any(selector in ds or selector.split()[-1] in ds
                      for ds in dark_selectors)
        if not covered:
            issues.append({
                "selector": selector,
                "prop": prop,
                "value": val,
            })
    return issues


# ── Auto-fix generator ────────────────────────────────────────────────────────
DARK_COLOR_MAP = {
    # near-whites / light greys → dark card bg
    r'#f[0-9a-f]{5}': "var(--hp-card-bg)",
    r'#e[0-9a-f]{5}': "var(--hp-card-bg)",
    r'#fff(fff)?':     "var(--hp-card-bg)",
    r'white':          "var(--hp-card-bg)",
    # near-blacks → var(--hp-text)
    r'#[01][0-9a-f]{5}': "var(--hp-text)",
    r'black':             "var(--hp-text)",
    # mid greys
    r'#[89a-c][0-9a-f]{5}': "var(--hp-text-secondary)",
    r'silver|#c0c0c0':       "var(--hp-text-muted)",
}

def suggest_dark_value(val: str) -> str:
    val_l = val.lower().strip()
    for pattern, dark_val in DARK_COLOR_MAP.items():
        if re.fullmatch(pattern, val_l):
            return dark_val
    # Fallback heuristics by luminance bucket
    hex_m = HEX_RE.search(val_l)
    if hex_m:
        h = hex_m.group(1).ljust(6, '0')[:6]
        try:
            r, g, b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
            lum = 0.299*r + 0.587*g + 0.114*b
            if lum > 200: return "var(--hp-card-bg)"
            if lum > 128: return "var(--hp-text-secondary)"
            if lum > 60:  return "var(--hp-text-muted)"
            return "var(--hp-text)"
        except Exception:
            pass
    return "var(--hp-text)"   # safe fallback


def build_auto_css(issues: list) -> str:
    """Build a CSS block of auto-generated dark overrides."""
    lines  = ["/* AUTO-GENERATED dark overrides — review before committing */"]
    groups = defaultdict(list)
    for issue in issues:
        dark_val = suggest_dark_value(issue["value"])
        groups[(issue["selector"], issue["prop"])].append(dark_val)

    for (selector, prop), dark_vals in groups.items():
        dark_val = dark_vals[0]
        prop_css = "background-color" if "background" in prop.lower() else "color"
        lines.append(
            f'html[data-hp-theme="dark"] {selector} '
            f'{{ {prop_css}: {dark_val} !important; }}'
        )
    return "\n".join(lines)


# ── Report printer ────────────────────────────────────────────────────────────
RESET  = "\033[0m"
RED    = "\033[91m"
YELLOW = "\033[93m"
GREEN  = "\033[92m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
DIM    = "\033[2m"

def c(text, color): return f"{color}{text}{RESET}"

def print_report(template_issues: dict, css_issues: list, auto_css: str, apply_fix: bool):
    print(f"\n{BOLD}{'='*70}{RESET}")
    print(f"{BOLD}  DARK MODE AUDIT REPORT{RESET}")
    print(f"{'='*70}")

    total_template = sum(len(v) for v in template_issues.values())

    # ── Template issues ──
    print(f"\n{BOLD}{CYAN}[ TEMPLATES — {total_template} issues ]{RESET}")
    for filepath, issues in sorted(template_issues.items()):
        if not issues:
            continue
        rel = os.path.relpath(filepath, BASE)
        inline  = [i for i in issues if i["type"] == "inline-style"]
        blocks  = [i for i in issues if i["type"] == "style-block"]
        covered = [i for i in issues if i["type"] == "bg-class"]
        print(f"\n  {BOLD}{rel}{RESET}  ({len(issues)} issues)")
        for issue in inline:
            print(f"    {c('MANUAL','RED')} line {issue['line']:>4} | inline style | "
                  f"{c(issue['prop'], YELLOW)}: {c(issue['value'], RED)}")
            print(f"           {DIM}{issue['fix']}{RESET}")
        for issue in blocks:
            print(f"    {c('FIX','YELLOW')}    line {issue['line']:>4} | <style> block | "
                  f"{c(issue['prop'], YELLOW)}: {c(issue['value'], RED)}")
            print(f"           {DIM}{issue['fix']}{RESET}")
        for issue in covered:
            print(f"    {c('OK','GREEN')}     line {issue['line']:>4} | .{issue['class']} → already covered by CSS")

    # ── CSS issues ──
    print(f"\n{BOLD}{CYAN}[ CSS — {len(css_issues)} selectors missing dark override ]{RESET}")
    if css_issues:
        for issue in css_issues[:40]:
            print(f"    {c(issue['selector'][:60], YELLOW)}  "
                  f"| {issue['prop']}: {c(issue['value'], RED)}")
        if len(css_issues) > 40:
            print(f"    {DIM}... and {len(css_issues)-40} more{RESET}")
    else:
        print(f"    {c('All CSS selectors have dark coverage!', GREEN)}")

    # ── Auto-fix summary ──
    print(f"\n{BOLD}{CYAN}[ AUTO-FIX ]{RESET}")
    if apply_fix:
        print(f"  {c('Appended auto-generated overrides to hospital-theme.css', GREEN)}")
        print(f"  {DIM}Review the AUTO-GENERATED block at the end of the file.{RESET}")
    else:
        print(f"  {c(len(css_issues), BOLD)} CSS rules would be auto-fixed with --fix")
        print(f"  {DIM}Run with --fix to apply{RESET}")

    manual = sum(1 for issues in template_issues.values()
                 for i in issues if i["type"] == "inline-style")
    print(f"\n{BOLD}Summary:{RESET}")
    print(f"  CSS auto-fixable  : {c(len(css_issues), GREEN)}")
    print(f"  Template manual   : {c(manual, RED)}")
    print(f"  Template auto-ok  : {c(sum(1 for issues in template_issues.values() for i in issues if i['type']=='bg-class'), GREEN)}")
    print(f"\n{'='*70}\n")


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Dark mode audit tool")
    parser.add_argument("--fix",    action="store_true", help="Auto-append CSS overrides")
    parser.add_argument("--css-only", action="store_true", help="Only scan CSS file")
    parser.add_argument("--html-only", action="store_true", help="Only scan templates")
    parser.add_argument("--template", default=None, help="Scan a single template file")
    args = parser.parse_args()

    css_text = CSS_FILE.read_text(encoding="utf-8")
    dark_selectors = load_existing_dark_selectors(css_text)

    template_issues = {}
    css_issues      = []

    # ── Scan templates ──
    if not args.css_only:
        if args.template:
            files = [Path(args.template)]
        else:
            files = list(TEMPLATES.rglob("*.html"))

        for fpath in sorted(files):
            try:
                html = fpath.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            issues  = scan_inline_styles(html, str(fpath))
            issues += scan_style_blocks(html, str(fpath))
            issues += scan_bg_classes(html)
            if issues:
                template_issues[str(fpath)] = issues

    # ── Scan CSS ──
    if not args.html_only:
        css_issues = scan_css_missing_dark(css_text, dark_selectors)
        # Deduplicate
        seen = set()
        deduped = []
        for i in css_issues:
            key = (i["selector"], i["prop"])
            if key not in seen:
                seen.add(key)
                deduped.append(i)
        css_issues = deduped

    # ── Build auto-fix CSS ──
    auto_css = build_auto_css(css_issues) if css_issues else ""

    # ── Apply fix ──
    if args.fix and auto_css:
        with open(CSS_FILE, "a", encoding="utf-8") as f:
            f.write("\n\n" + auto_css + "\n")
        print(f"\n{GREEN}✓ Appended {len(css_issues)} dark overrides to {CSS_FILE.name}{RESET}")

    # ── Print report ──
    print_report(template_issues, css_issues, auto_css, args.fix)


if __name__ == "__main__":
    main()
