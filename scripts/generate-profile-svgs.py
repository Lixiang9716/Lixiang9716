#!/usr/bin/env python3
"""Generate the animated SVGs used by the profile README (neon hero banner +
telemetry panel). Committed output lives in assets/; re-run after the
snapshot numbers drift (uptime years, hourly commit shape).

Data sources (snapshot 2026-10-17):
- hourly commit shape: profile-summary-card-output/tokyonight/4-productive-time.svg
  (UTC hours converted to UTC+8 Hangzhou local time)
- repos / account age: api.github.com/users/Lixiang9716
"""

import argparse
import math
import os
import random

# ---------------------------------------------------------------- data

# commit weight per LOCAL hour (UTC+8), normalized 0-100 (peak 18:00 = 95.8)
HOURS = [75, 41.7, 16.7, 50, 20.8, 8.3, 0, 0,
         4.2, 12.5, 75, 20.8, 4.2, 37.5, 20.8, 12.5,
         16.7, 66.7, 95.8, 33.3, 41.7, 66.7, 45.8, 25]
PEAK_HOUR = 18

# tokyonight palette (matches profile-summary-card-output/tokyonight/*)
WELL = "#16161e"      # deep background
PANEL = "#1a1b27"     # panel background (same as stats cards)
BORDER = "#2a2e42"
TEXT = "#c0caf5"      # primary lavender-white
DIM = "#9aa8ce"       # secondary text
BLUE = "#70a5fd"      # prompts, titles
PURPLE = "#bf91f3"    # data, rain
TEAL = "#38bdae"      # success, rain heads
PINK = "#ff7edb"      # peak highlight, glitch channel
AMBER = "#e0af68"
GREEN_LED = "#9ece6a"

FONT = "'JetBrains Mono','Cascadia Code','SF Mono',Menlo,Consolas,'Courier New',monospace"
CYCLE = 12  # hero tagline loop, seconds

CHAR_W = 0.62  # em-per-char used for clip widths (generous on purpose)

RAIN_POOL = ("アイウエオカキクケコサシスセソタチツテトナニヌネノ"
             "ハヒフヘホマミムメモヤユヨラリルレロワヲン0123456789<>/#$=+*")


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ---------------------------------------------------------------- hero

def text_w(s, size):
    w = 0
    for ch in s:
        w += size * (1.0 if ord(ch) > 0x2E7F else CHAR_W)
    return w


def render_hero(tagline, static=False, seed=42):
    W, H = 880, 430
    rng = random.Random(seed)
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
         f'font-family="{FONT}">']
    p.append(f'''<defs>
<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#1a1b27"/><stop offset="1" stop-color="#0d0e17"/>
</linearGradient>
<filter id="glow" x="-40%" y="-40%" width="180%" height="180%">
  <feGaussianBlur stdDeviation="9" result="b"/>
  <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
</filter>
<filter id="soft" x="-60%" y="-60%" width="220%" height="220%">
  <feGaussianBlur stdDeviation="30"/>
</filter>
<pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse">
  <rect width="4" height="1" fill="#000" opacity="0.10"/>
</pattern>
</defs>''')
    p.append(f'<rect width="{W}" height="{H}" fill="url(#bg)"/>')

    # -- matrix rain ------------------------------------------------------
    p.append('<g opacity="0.85">')
    for col in range(15):
        x = 16 + col * 61
        n = 18
        chars = "".join(rng.choice(RAIN_POOL) for _ in range(n))
        dur = rng.uniform(7, 13)
        begin = -rng.uniform(0, dur)
        op = rng.uniform(0.14, 0.30)
        tspans = "".join(
            f'<tspan x="{x}" dy="{40 if i else 0}">{esc(c)}</tspan>'
            for i, c in enumerate(chars))
        head = f'<tspan x="{x}" dy="0" fill="{TEAL}">{esc(chars[0])}</tspan>'
        rest = "".join(
            f'<tspan x="{x}" dy="{40}">{esc(c)}</tspan>' for c in chars[1:])
        fade = "" if static else (
            f'<animate attributeName="opacity" values="0;{op};{op};0" '
            f'keyTimes="0;0.08;0.9;1" dur="{dur:.1f}s" begin="{begin:.1f}s" '
            f'repeatCount="indefinite"/>')
        run = "" if static else (
            f'<animateTransform attributeName="transform" type="translate" '
            f'from="0 -760" to="0 {H + 60}" dur="{dur:.1f}s" '
            f'begin="{begin:.1f}s" repeatCount="indefinite"/>')
        p.append(f'<g font-size="17" fill="{PURPLE}" opacity="{op}">'
                 f'{run}<text y="0">{head}{rest}</text></g>')
    p.append('</g>')

    # -- spotlight behind the identity, for readability -------------------
    p.append(f'<ellipse cx="{W/2}" cy="205" rx="400" ry="160" '
             f'fill="#0d0e17" opacity="0.72" filter="url(#soft)"/>')

    # -- neon name --------------------------------------------------------
    flick = "" if static else (
        f'<animate attributeName="opacity" '
        f'values="1;1;0.55;1;1;1;0.75;1;1" '
        f'keyTimes="0;0.62;0.63;0.645;0.83;0.9;0.91;0.925;1" '
        f'dur="6.5s" repeatCount="indefinite"/>')
    p.append(f'<text x="{W/2}" y="212" text-anchor="middle" font-size="108" '
             f'font-weight="700" fill="{BLUE}" filter="url(#glow)" '
             f'letter-spacing="10">{flick}李响</text>')
    p.append(f'<text x="{W/2}" y="258" text-anchor="middle" font-size="24" '
             f'letter-spacing="18" fill="{TEXT}">LIXIANG9716</text>')
    # chromatic glitch: two offset channel copies flicker on briefly
    for dx, color, phase in ((-3, PINK, 0.7), (3, TEAL, 2.9)):
        if static:
            continue
        p.append(f'<text x="{W/2 + dx}" y="258" text-anchor="middle" '
                 f'font-size="24" letter-spacing="18" fill="{color}" '
                 f'opacity="0">'
                 f'<animate attributeName="opacity" values="0;0;0.9;0;0" '
                 f'keyTimes="0;{phase/5:.2f};{(phase+0.12)/5:.2f};'
                 f'{(phase+0.2)/5:.2f};1" calcMode="discrete" '
                 f'dur="5s" repeatCount="indefinite"/></text>')
    # version chip
    p.append(f'<text x="{W-16}" y="26" text-anchor="end" font-size="13" '
             f'fill="{DIM}">[v8.3 beta]</text>')
    p.append(f'<text x="16" y="26" font-size="13" fill="{DIM}">'
             f'~/lixiang9716</text>')

    # -- tagline, typed once per cycle ------------------------------------
    ts = 19
    full = "> " + tagline
    tw = text_w(full, ts)
    x0 = W / 2 - tw / 2
    ty = 330
    p.append(f'<defs><clipPath id="tag"><rect x="{x0-4}" y="{ty-24}" '
             f'height="30" width="{tw+8 if static else 0}">')
    if not static:
        p.append(f'<animate attributeName="width" values="0;0;{tw+8};{tw+8}" '
                 f'keyTimes="0;0.06;0.26;1" dur="{CYCLE}s" '
                 f'repeatCount="indefinite"/>')
    p.append('</rect></clipPath></defs>')
    p.append(f'<g clip-path="url(#tag)"><text x="{x0}" y="{ty}" '
             f'font-size="{ts}"><tspan fill="{TEAL}">&gt; </tspan>'
             f'<tspan fill="{TEXT}">{esc(tagline)}</tspan></text></g>')
    cx = x0 + tw + 4
    blink = "" if static else (
        f'<animate attributeName="opacity" values="1;0" keyTimes="0;0.5" '
        f'calcMode="discrete" dur="1.1s" repeatCount="indefinite"/>')
    p.append(f'<rect x="{cx:.0f}" y="{ty-16}" width="11" height="20" '
             f'fill="{TEXT}">{blink}</rect>')

    # -- scanlines + HUD corners -------------------------------------------
    p.append(f'<rect width="{W}" height="{H}" fill="url(#scan)"/>')
    for cx_, cy_, dx, dy in ((12, 12, 26, 0), (12, 12, 0, 26),
                             (W-12, 12, -26, 0), (W-12, 12, 0, 26),
                             (12, H-12, 26, 0), (12, H-12, 0, -26),
                             (W-12, H-12, -26, 0), (W-12, H-12, 0, -26)):
        p.append(f'<line x1="{cx_}" y1="{cy_}" x2="{cx_+dx}" y2="{cy_+dy}" '
                 f'stroke="{BLUE}" opacity="0.5"/>')
    p.append('</svg>')
    return "".join(p)


# ------------------------------------------------------------ telemetry

def render_telemetry(static=False):
    W, H = 880, 236
    PW, PH, GAP = 272, 220, 24
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
             f'font-family="{FONT}">']
    parts.append(f'<rect width="{W}" height="{H}" fill="{WELL}" rx="8"/>')

    def panel(x, title):
        p = [f'<g><rect x="{x}" y="8" width="{PW}" height="{PH}" fill="{PANEL}" '
             f'rx="6" stroke="{BORDER}"/>']
        for cx, cy, dx, dy in ((x+4, 20, 10, 0), (x+4, 20, 0, 10),
                               (x+PW-4, 20, -10, 0), (x+PW-4, 20, 0, 10),
                               (x+4, 8+PH-12, 10, 0), (x+4, 8+PH-12, 0, -10),
                               (x+PW-4, 8+PH-12, -10, 0), (x+PW-4, 8+PH-12, 0, -10)):
            p.append(f'<line x1="{cx}" y1="{cy}" x2="{cx+dx}" y2="{cy+dy}" '
                     f'stroke="{BLUE}" opacity="0.35"/>')
        p.append(f'<text x="{x+16}" y="34" font-size="12" letter-spacing="2" '
                 f'fill="{BLUE}">{esc(title)}</text>')
        return p

    # -- panel 1: 24h commit clock --------------------------------------
    cx, cy, ro, ri = 8 + PW / 2, 128, 76, 34
    p = panel(8, "COMMIT CLOCK (UTC+8)")
    mx = max(HOURS)
    for h, v in enumerate(HOURS):
        ang = (h / 24) * 360 - 90
        rad = math.radians(ang)
        frac = 4 + (v / mx) * 40
        x1, y1 = cx + ri * math.cos(rad), cy + ri * math.sin(rad)
        x2, y2 = cx + (ri + frac) * math.cos(rad), cy + (ri + frac) * math.sin(rad)
        col = PINK if h == PEAK_HOUR else PURPLE
        op = 1.0 if v > 0 else 0.25
        p.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                 f'stroke="{col}" stroke-width="4" opacity="{op}" '
                 f'stroke-linecap="round"/>')
    for lab, ang in (("00", -90), ("06", 0), ("12", 90), ("18", 180)):
        rad = math.radians(ang)
        lx, ly = cx + (ro + 13) * math.cos(rad), cy + (ro + 13) * math.sin(rad)
        p.append(f'<text x="{lx:.1f}" y="{ly:.1f}" font-size="9" fill="{DIM}" '
                 f'text-anchor="middle" dominant-baseline="middle">{lab}</text>')
    rad = math.radians(PEAK_HOUR / 24 * 360 - 90)
    px, py = cx + (ri + 36) * math.cos(rad), cy + (ri + 36) * math.sin(rad)
    if static:
        p.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="5" fill="{PINK}"/>')
    else:
        p.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="4" fill="{PINK}">'
                 f'<animate attributeName="r" values="3;6;3" dur="2s" '
                 f'repeatCount="indefinite"/>'
                 f'<animate attributeName="opacity" values="1;.4;1" dur="2s" '
                 f'repeatCount="indefinite"/></circle>')
    if static:
        p.append(f'<line x1="{cx}" y1="{cy}" x2="{cx}" y2="{cy-ri+6}" '
                 f'stroke="{TEAL}" stroke-width="1.5" opacity="0.9"/>')
    else:
        p.append(f'<g><line x1="{cx}" y1="{cy}" x2="{cx}" y2="{cy-ri+6}" '
                 f'stroke="{TEAL}" stroke-width="1.5" opacity="0.9">'
                 f'</line><animateTransform attributeName="transform" '
                 f'type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" '
                 f'dur="60s" repeatCount="indefinite"/></g>')
    p.append(f'<circle cx="{cx}" cy="{cy}" r="3" fill="{TEAL}"/>')
    p.append("</g>")
    parts.extend(p)

    # -- panel 2: system uptime -----------------------------------------
    x2 = 8 + PW + GAP
    p = panel(x2, "SYSTEM UPTIME")
    p.append(f'<text x="{x2+16}" y="104" font-size="46" font-weight="700" '
             f'fill="{BLUE}">8y+</text>')
    cur_x = x2 + 16 + text_w("8y+", 46) + 6
    if static:
        p.append(f'<rect x="{cur_x:.0f}" y="74" width="12" height="30" '
                 f'fill="{TEXT}"/>')
    else:
        p.append(f'<rect x="{cur_x:.0f}" y="74" width="12" height="30" '
                 f'fill="{TEXT}"><animate attributeName="opacity" values="1;0" '
                 f'keyTimes="0;0.5" calcMode="discrete" dur="1.1s" '
                 f'repeatCount="indefinite"/></rect>')
    p.append(f'<text x="{x2+16}" y="132" font-size="13" fill="{DIM}">'
             f'since 2018-06-27</text>')
    led = ("" if static else
           f'<animate attributeName="opacity" values="1;.3;1" dur="1.6s" '
           f'repeatCount="indefinite"/>')
    p.append(f'<circle cx="{x2+22}" cy="158" r="4" fill="{GREEN_LED}">{led}</circle>')
    p.append(f'<text x="{x2+34}" y="162" font-size="13" fill="{TEAL}">'
             f'0 crashes, 0 reboots</text>')
    p.append(f'<text x="{x2+16}" y="186" font-size="12" fill="{DIM}">'
             f'kernel: coffee + curiosity</text>')
    p.append("</g>")
    parts.extend(p)

    # -- panel 3: sleep monitor ------------------------------------------
    x3 = 8 + 2 * (PW + GAP)
    p = panel(x3, "SLEEP MONITOR")
    p.append(f'<text x="{x3+16}" y="70" font-size="13" fill="{DIM}">status:</text>')
    p.append(f'<text x="{x3+78}" y="70" font-size="13" font-weight="700" '
             f'fill="{TEAL}">DETECTED</text>')
    p.append(f'<text x="{x3+16}" y="96" font-size="13" fill="{DIM}">'
             f'window: 06:00–07:00</text>')
    p.append(f'<text x="{x3+16}" y="122" font-size="13" fill="{DIM}">'
             f'evidence: 0 commits</text>')
    for i, (zx, zy, zs) in enumerate(((x3+204, 186, 18), (x3+226, 164, 24),
                                      (x3+248, 140, 30))):
        if static:
            p.append(f'<text x="{zx}" y="{zy}" font-size="{zs}" '
                     f'fill="{PURPLE}" opacity="{0.4+0.3*i}">z</text>')
        else:
            p.append(
                f'<text x="{zx}" y="{zy}" font-size="{zs}" fill="{PURPLE}">'
                f'<animate attributeName="opacity" values="0;1;0" '
                f'keyTimes="0;0.4;1" dur="3s" begin="{i*0.6}s" '
                f'repeatCount="indefinite"/>'
                f'<animateTransform attributeName="transform" type="translate" '
                f'values="0 8;0 -10" dur="3s" begin="{i*0.6}s" '
                f'repeatCount="indefinite"/>z</text>')
    p.append("</g>")
    parts.extend(p)
    parts.append("</svg>")
    return "".join(parts)


# ---------------------------------------------------------------- main

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--static", action="store_true",
                    help="render end-state frames (no loops) for preview")
    ap.add_argument("--out", default="assets")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    static = a.static
    open(os.path.join(a.out, "hero-terminal.svg"), "w").write(
        render_hero("building the governance layer for agent-driven development",
                    static))
    open(os.path.join(a.out, "hero-terminal.zh.svg"), "w").write(
        render_hero("为 agent 驱动的开发构建治理层", static, seed=7))
    open(os.path.join(a.out, "telemetry.svg"), "w").write(
        render_telemetry(static))
    open(os.path.join(a.out, "telemetry.zh.svg"), "w").write(
        render_telemetry(static))
    print("written to", a.out)
