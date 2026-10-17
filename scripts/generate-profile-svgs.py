#!/usr/bin/env python3
"""Generate the animated SVGs used by the profile README (hero terminal +
telemetry panel). Committed output lives in assets/; re-run after the
snapshot numbers drift (repos, uptime years, hourly commit shape).

Data sources (snapshot 2026-10-17):
- hourly commit shape: profile-summary-card-output/tokyonight/4-productive-time.svg
  (UTC hours converted to UTC+8 Hangzhou local time)
- repos / account age: api.github.com/users/Lixiang9716
- languages: profile-summary-card-output/tokyonight/2-most-commit-language.svg
"""

import argparse
import os

# ---------------------------------------------------------------- data

# commit weight per LOCAL hour (UTC+8), normalized 0-100 (peak 18:00 = 95.8)
HOURS = [75, 41.7, 16.7, 50, 20.8, 8.3, 0, 0,
         4.2, 12.5, 75, 20.8, 4.2, 37.5, 20.8, 12.5,
         16.7, 66.7, 95.8, 33.3, 41.7, 66.7, 45.8, 25]
PEAK_HOUR = 18

# tokyonight palette (matches profile-summary-card-output/tokyonight/*)
WELL = "#16161e"      # terminal well
PANEL = "#1a1b27"     # panel background (same as stats cards)
BORDER = "#2a2e42"
TEXT = "#c0caf5"      # primary lavender-white
DIM = "#9aa8ce"       # secondary text
BLUE = "#70a5fd"      # prompts, titles
PURPLE = "#bf91f3"    # data
TEAL = "#38bdae"      # success
PINK = "#ff7edb"      # peak highlight (sparing)
AMBER = "#e0af68"
GREEN_LED = "#9ece6a"

FONT = "'JetBrains Mono','Cascadia Code','SF Mono',Menlo,Consolas,'Courier New',monospace"
CYCLE = 14  # hero typewriter full loop, seconds

CHAR_W = 0.62  # em-per-char used for clip widths (generous on purpose)


def text_w(s, size):
    w = 0
    for ch in s:
        w += size * (1.0 if ord(ch) > 0x2E7F else CHAR_W)
    return w


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ---------------------------------------------------------------- hero

# (kind, text, color) — kind: cmd = typed live, out = printed after a beat
HERO_EN = [
    ("cmd", "whoami", TEXT),
    ("out", "Li Xiang, agent-native engineer, hangzhou CN", DIM),
    ("cmd", "uptime", TEXT),
    ("out", "up 8 years since 2018-06-27, 14 public repos, 0 crashes", DIM),
    ("cmd", "cat ~/stack.txt", TEXT),
    ("out", "python / c / rust, running on kubernetes", DIM),
    ("cmd", "tail -f ~/mission.log", TEXT),
    ("out", "[ok] govrail: governance plane for agent-driven development", TEAL),
    ("out", "[ok] agents write the code, gates hold the quality line", DIM),
    ("prompt", "", TEXT),
]

HERO_ZH = [
    ("cmd", "whoami", TEXT),
    ("out", "李响(Li Xiang),agent-native 工程师,坐标杭州", DIM),
    ("cmd", "uptime", TEXT),
    ("out", "已连续运行 8 年(自 2018-06-27),14 个公开仓库,0 次崩溃", DIM),
    ("cmd", "cat ~/stack.txt", TEXT),
    ("out", "python / c / rust,部署在 kubernetes 上", DIM),
    ("cmd", "tail -f ~/mission.log", TEXT),
    ("out", "[ok] govrail:面向 agent 驱动开发的治理平面", TEAL),
    ("out", "[ok] 让 agent 写代码,用 gates 守住质量线", DIM),
    ("prompt", "", TEXT),
]

# typewriter schedule as fractions of CYCLE: (cmd_start, cmd_end, out_at)
SCHED = [
    (0.010, 0.060, 0.065),
    (0.120, 0.170, 0.175),
    (0.220, 0.290, 0.300),
    (0.340, 0.430, 0.435),
]
OUT2_AT = 0.500          # second [ok] line
FADE_AT = 0.950          # whole session fades before the loop restarts


def render_hero(lines, title, static=False):
    W, H = 880, 436
    BAR = 44
    LH = 32
    X0, Y0 = 28, 92
    SIZE = 19
    n = len(lines)
    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'font-family="{FONT}">')
    parts.append(f'<rect width="{W}" height="{H}" fill="{PANEL}" rx="8"/>')
    parts.append(f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" '
                 f'fill="none" stroke="{BORDER}" rx="8"/>')
    # title bar
    for i, c in enumerate((PINK, AMBER, TEAL)):
        parts.append(f'<circle cx="{26+i*22}" cy="22" r="6" fill="{c}"/>')
    parts.append(
        f'<text x="{W/2}" y="27" text-anchor="middle" font-size="13" '
        f'fill="{DIM}">{esc(title)}</text>')
    parts.append(f'<line x1="0" y1="{BAR}" x2="{W}" y2="{BAR}" '
                 f'stroke="{BORDER}"/>')
    # CRT scanlines, barely there
    parts.append(
        f'<defs><pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse">'
        f'<rect width="4" height="1" fill="#000" opacity="0.10"/></pattern></defs>'
        f'<rect x="0" y="{BAR}" width="{W}" height="{H-BAR}" fill="url(#scan)"/>')

    parts.append('<g>')
    if not static:
        parts.append(
            f'<animate attributeName="opacity" values="1;1;0" '
            f'keyTimes="0;{FADE_AT};0.985" dur="{CYCLE}s" '
            f'repeatCount="indefinite"/>')

    # clipPaths: one per typed command line
    out = []
    cmd_idx = 0
    for i, (kind, s, color) in enumerate(lines):
        y = Y0 + i * LH
        x = X0 if kind != "out" else X0 + 14
        if kind == "cmd":
            full = "$ " + s
            cw = text_w(full, SIZE) + 8
            a, b, _ = SCHED[cmd_idx]
            cmd_idx += 1
            parts.append(
                f'<clipPath id="c{cmd_idx}"><rect x="{x-4}" y="{y-24}" '
                f'height="30" width="{cw if static else 0}">')
            if not static:
                parts.append(
                    f'<animate attributeName="width" values="0;0;{cw};{cw}" '
                    f'keyTimes="0;{a};{b};1" dur="{CYCLE}s" '
                    f'repeatCount="indefinite"/>')
            parts.append('</rect></clipPath>')
            dy_parts = esc(full[:2])
            rest = esc(full[2:])
            out.append(
                f'<g clip-path="url(#c{cmd_idx})">'
                f'<text x="{x}" y="{y}" font-size="{SIZE}" font-weight="600" '
                f'fill="{BLUE}">{dy_parts}</text>'
                f'<text x="{x + text_w("$ ", SIZE)}" y="{y}" font-size="{SIZE}" '
                f'fill="{TEXT}">{rest}</text></g>')
        elif kind == "out":
            k = (1.0 if static else
                 (SCHED[cmd_idx - 1][2] if i not in (8,) else OUT2_AT))
            disp = ("" if static else
                    f'<animate attributeName="opacity" values="0;1" '
                    f'keyTimes="0;{k}" calcMode="discrete" dur="{CYCLE}s" '
                    f'repeatCount="indefinite"/>')
            body = esc(s)
            if body.startswith("[ok]"):
                body = (f'<tspan fill="{TEAL}">[ok]</tspan>' + esc(s[4:]))
            out.append(f'<text x="{x}" y="{y}" font-size="{SIZE}" '
                       f'fill="{color}" opacity="{0 if not static else 1}">'
                       f'{disp}{body}</text>')
        else:  # trailing prompt with block cursor
            out.append(f'<text x="{x}" y="{y}" font-size="{SIZE}" '
                       f'font-weight="600" fill="{BLUE}">$</text>')
            cx, cwid = x + text_w("$ ", SIZE), SIZE * 0.62 * 1.6
            blink = ("" if static else
                     f'<animate attributeName="opacity" values="1;0" '
                     f'keyTimes="0;0.5" calcMode="discrete" dur="1.1s" '
                     f'repeatCount="indefinite"/>')
            out.append(f'<rect x="{cx}" y="{y-16}" width="{cwid}" height="20" '
                       f'fill="{TEXT}">{blink}</rect>')
    parts.extend(out)
    parts.append("</g></svg>")
    return "".join(parts)


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
        import math
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
        import math
        rad = math.radians(ang)
        lx, ly = cx + (ro + 13) * math.cos(rad), cy + (ro + 13) * math.sin(rad)
        p.append(f'<text x="{lx:.1f}" y="{ly:.1f}" font-size="9" fill="{DIM}" '
                 f'text-anchor="middle" dominant-baseline="middle">{lab}</text>')
    # peak pulse on 18:00 bar tip
    import math
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
    # sweep hand
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
             f'fill="{BLUE}">8y+'
             + ('' if static else
                f'<animate attributeName="opacity" values="1;1" dur="1s" '
                f'repeatCount="indefinite"/>')
             + '</text>')
    # echo cursor after the number
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
    # floating zzz, bottom-right free corner
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
        render_hero(HERO_EN, "lixiang@hangzhou ~ zsh", static))
    open(os.path.join(a.out, "hero-terminal.zh.svg"), "w").write(
        render_hero(HERO_ZH, "lixiang@hangzhou ~ zsh", static))
    open(os.path.join(a.out, "telemetry.svg"), "w").write(
        render_telemetry(static))
    open(os.path.join(a.out, "telemetry.zh.svg"), "w").write(
        render_telemetry(static))
    print("written to", a.out)
