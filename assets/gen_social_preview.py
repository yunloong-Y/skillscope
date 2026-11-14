#!/usr/bin/env python3
"""Build-time artwork generator for skillscope social preview cards.

This is a MAINTAINER-ONLY tool: it needs Pillow and macOS system fonts.
The skillscope CLI itself has zero third-party dependencies and never runs this.

    python3 assets/gen_social_preview.py

Outputs 1280x640 PNGs (GitHub social preview spec, 2:1, under 1 MB).
Text stays inside the center 1100x560 safe zone so it survives platform crops.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

S = 2  # supersample for antialiasing
W, H = 1280, 640
OUT = Path(__file__).resolve().parent

BG = (13, 17, 23)
PANEL = (22, 27, 34)
INK = (240, 246, 252)
MUTED = (139, 148, 158)
LINE = (38, 44, 54)
GRID = (26, 32, 42)
ACCENT = (88, 166, 255)
DANGER = (248, 81, 73)
OK = (63, 185, 80)

F_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
F_REG = "/System/Library/Fonts/Helvetica.ttc"
F_CJK = "/System/Library/Fonts/Hiragino Sans GB.ttc"


def blend(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def f(path, size):
    return ImageFont.truetype(path, size * S)


def p(*vals):
    return tuple(int(v * S) for v in vals)


class Card:
    def __init__(self):
        self.im = Image.new("RGB", (W * S, H * S), BG)
        self.d = ImageDraw.Draw(self.im)

    def rect(self, x, y, w, h, fill, outline=None, width=1, radius=0):
        box = p(x, y, x + w, y + h)
        if radius:
            self.d.rounded_rectangle(
                box, radius=radius * S, fill=fill,
                outline=outline, width=max(1, int(width * S)),
            )
        else:
            self.d.rectangle(box, fill=fill, outline=outline, width=max(1, int(width * S)))

    def line(self, points, fill, width=1):
        self.d.line([(int(x * S), int(y * S)) for x, y in points], fill=fill,
                    width=max(1, int(width * S)))

    def ellipse(self, x, y, w, h, outline=None, width=1, fill=None):
        self.d.ellipse(p(x, y, x + w, y + h), outline=outline,
                       width=max(1, int(width * S)), fill=fill)

    def text(self, x, y, s, font, fill):
        self.d.text((int(x * S), int(y * S)), s, font=font, fill=fill)

    def tracked(self, x, y, s, font, fill, spacing):
        cur = x
        for ch in s:
            self.text(cur, y, ch, font, fill)
            cur += self.d.textlength(ch, font=font) / S + spacing
        return cur

    def save(self, name):
        out = OUT / name
        self.im.resize((W, H), Image.Resampling.LANCZOS).save(out, "PNG", optimize=True)
        print(f"wrote {out.name}  {out.stat().st_size:,} bytes")


def chrome(c):
    # grid + accent wash
    for gx in range(0, W, 40):
        c.line([(gx, 0), (gx, H)], GRID, 1)
    for gy in range(0, H, 40):
        c.line([(0, gy), (W, gy)], GRID, 1)
    for gx in range(0, 780, 4):
        alpha = 0.16 * (1 - gx / 780) ** 1.4
        c.rect(gx, 0, 4, H, blend(BG, ACCENT, alpha))
    # circuit traces (kept clear of the eyebrow / footer text)
    c.line([(0, 26), (104, 26), (136, 58), (248, 58)], LINE, 2)
    c.line([(980, 0), (980, 36), (1012, 68), (1280, 68)], LINE, 2)
    c.line([(1140, 640), (1140, 608), (1108, 576), (1280, 576)], LINE, 2)
    for x, y in ((136, 58), (1012, 68), (1108, 576)):
        c.ellipse(x - 4, y - 4, 8, 8, fill=ACCENT)
    # context-window panel
    c.rect(692, 122, 506, 372, PANEL, outline=LINE, width=2, radius=18)
    c.tracked(720, 152, "CONTEXT WINDOW", f(F_REG, 14), MUTED, 2.6)
    for i in range(10):
        x = 720 + i * 38
        color = ACCENT if i < 7 else DANGER
        op = 0.30 + (i % 4) * 0.16
        c.rect(x, 210, 28, 66, blend(PANEL, color, op), radius=6)
    c.rect(1104, 210, 68, 66, blend(PANEL, OK, 0.14), outline=OK, width=1, radius=6)
    c.text(1116, 232, "FREE", f(F_BOLD, 15), OK)
    c.line([(720, 306), (1172, 306)], LINE, 2)
    c.text(720, 336, "10 skills loaded", f(F_REG, 20), MUTED)
    c.text(720, 372, "How many earn their place?", f(F_BOLD, 21), DANGER)
    c.line([(720, 416), (1172, 416)], LINE, 2)
    c.text(720, 440, "AUDIT  ·  SCORE  ·  BUDGET", f(F_REG, 15), ACCENT)
    # magnifier
    c.ellipse(1074, 522, 62, 62, outline=ACCENT, width=4)
    c.line([(1122, 570), (1152, 602)], ACCENT, 6)
    c.line([(1122, 570), (1152, 602)], ACCENT, 6)


def english():
    c = Card()
    chrome(c)
    c.tracked(64, 74, "AGENT SKILL AUDIT  /  2026", f(F_REG, 17), MUTED, 3.2)
    c.text(60, 168, "skillscope", f(F_BOLD, 100), INK)
    c.line([(64, 292), (640, 292)], LINE, 2)
    c.text(64, 320, "Your agent didn't get dumber.", f(F_REG, 36), MUTED)
    c.text(64, 372, "Its context window got eaten.", f(F_BOLD, 36), ACCENT)
    c.text(64, 470, "One command. 12 rules. A real number", f(F_REG, 26), INK)
    c.text(64, 506, "for what your skills actually cost.", f(F_REG, 26), INK)
    c.tracked(64, 576, "0 DEPENDENCIES  ·  0 NETWORK CALLS  ·  MIT", f(F_REG, 17), MUTED, 2.0)
    c.save("social-preview.png")
    return c


def chinese():
    c = Card()
    chrome(c)
    c.tracked(64, 74, "AGENT SKILL AUDIT  /  2026", f(F_REG, 17), MUTED, 3.2)
    c.text(60, 168, "skillscope", f(F_BOLD, 100), INK)
    c.line([(64, 292), (640, 292)], LINE, 2)
    c.text(64, 320, "你的 Agent 没变笨。", f(F_CJK, 42), MUTED)
    c.text(64, 380, "是 Skill 吃满了上下文。", f(F_CJK, 42), ACCENT)
    c.text(64, 474, "一条命令给 Skill 做体检：12 条规则 · 质量打分", f(F_CJK, 24), INK)
    c.text(64, 510, "上下文成本估算 · 可留存 HTML 报告", f(F_CJK, 24), INK)
    c.tracked(64, 576, "0 DEPENDENCIES  ·  0 NETWORK CALLS  ·  MIT", f(F_REG, 17), MUTED, 2.0)
    c.save("social-preview.zh.png")
    return c


if __name__ == "__main__":
    en, zh = english(), chinese()
    for card, name in ((en, "social-preview.thumb.png"), (zh, "social-preview.zh.thumb.png")):
        card.im.resize((400, 200), Image.Resampling.LANCZOS).save(OUT / name, "PNG", optimize=True)
        print(f"wrote {name} (400x200 readability check)")
