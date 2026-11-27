#!/usr/bin/env python3
"""news-image-20261127 -- one image summing up 27 November 2026 world news.

Pure Python standard library, no network, fully deterministic.
Draws a 1024x1024 PNG with six verified stories and writes it to
/output/entry.png (MAKEFUN_OUTPUT_DIR overrides the directory).

Stories (all verified against real reporting on 27 Nov 2026):
  1. Two Italians killed in a drone strike in Kuwait; Iran denies role
     (Reuters / NYT)
  2. Israel kills 9 in Gaza overnight; Hamas weighs response (Reuters)
  3. Thanksgiving storm postpones the Macy's parade; 400,000 lose power
     (Associated Press)
  4. Musk pledges two SpaceX shares for every US child, about $18bn
     (The Hindu)
  5. Gerard Depardieu to stand trial on a rape charge (BBC)
  6. Diesel tanker capsizes off Ibiza, 1 killed, up to 7,000 tonnes
     (BBC)
"""

import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
BG      = (15, 27, 45)     # deep navy page
PANEL   = (22, 39, 62)     # panel fill
PANEL2  = (28, 48, 76)     # icon box fill
INK     = (242, 245, 249)  # headline white
MUTED   = (159, 176, 195)  # secondary grey-blue
RULE    = (58, 82, 116)    # hairlines

ACCENTS = [
    (224, 82, 82),    # 1 diplomacy  - red
    (76, 154, 255),   # 2 space      - blue
    (63, 185, 127),   # 3 labour     - green
    (43, 179, 163),   # 4 pacific    - teal
    (232, 163, 61),   # 5 ukraine    - amber
    (155, 126, 222),  # 6 ship      - violet
]

# ---------------------------------------------------------------- 5x7 font
# Glyphs are 7 rows of 5 bits, '#' = on. Uppercase + digits + punctuation.
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '+': ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
}

BLANK = ("00000",) * 7


def char_advance(scale):
    return 5 * scale + max(1, scale // 2)


def text_width(text, scale):
    if not text:
        return 0
    return len(text) * char_advance(scale) - max(1, scale // 2)


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg) * (w * h)

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(color)

    def rect(self, x, y, w, h, color):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, color)

    def hline(self, x, y, w, color):
        self.rect(x, y, w, 1, color)

    def vline(self, x, y, h, color):
        self.rect(x, y, 1, h, color)

    def line(self, x0, y0, x1, y1, color, thick=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            self.rect(x0 - thick // 2, y0 - thick // 2, thick, thick, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, color, filled=True):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d = (xx - cx) ** 2 + (yy - cy) ** 2
                if filled and d <= r * r:
                    self.set(xx, yy, color)
                elif not filled and r * r - 2 * r <= d <= r * r:
                    self.set(xx, yy, color)

    def triangle(self, pts, color):
        (x0, y0), (x1, y1), (x2, y2) = pts
        ymin, ymax = min(y0, y1, y2), max(y0, y1, y2)
        for yy in range(ymin, ymax + 1):
            xs = []
            for (ax, ay), (bx, by) in (((x0, y0), (x1, y1)),
                                       ((x1, y1), (x2, y2)),
                                       ((x2, y2), (x0, y0))):
                if ay == by:
                    continue
                if min(ay, by) <= yy <= max(ay, by):
                    xs.append(ax + (bx - ax) * (yy - ay) / (by - ay))
            if len(xs) >= 2:
                for xx in range(int(min(xs)), int(max(xs)) + 1):
                    self.set(xx, yy, color)

    def text(self, x, y, s, scale, color):
        cx = x
        for ch in s.upper():
            glyph = FONT.get(ch, BLANK)
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == '1':
                        self.rect(cx + col * scale, y + row * scale,
                                  scale, scale, color)
            cx += char_advance(scale)
        return cx

    def text_centred(self, cx, y, s, scale, color):
        self.text(cx - text_width(s, scale) // 2, y, s, scale, color)


def wrap(text, max_chars):
    """Greedy word wrap; returns a list of lines, each <= max_chars."""
    lines, cur = [], ""
    for word in text.split(" "):
        if cur and len(cur) + 1 + len(word) > max_chars:
            lines.append(cur)
            cur = word
        else:
            cur = (cur + " " + word).strip()
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- stories
STORIES = [
    dict(num="01", tag="KUWAIT", source="REUTERS",
         accent=ACCENTS[0], icon="drone",
         head=["2 ITALIANS KILLED IN", "KUWAIT DRONE STRIKE"],
         sub="IRAN DENIES ROLE AS KUWAIT BLAMES TEHRAN; "
             "2 MORE WOUNDED"),
    dict(num="02", tag="GAZA", source="REUTERS",
         accent=ACCENTS[1], icon="blast",
         head=["ISRAEL KILLS 9 IN", "GAZA OVERNIGHT"],
         sub="STRIKES HIT DEIR AL-BALAH AND GAZA CITY; "
             "HAMAS WEIGHS ITS RESPONSE"),
    dict(num="03", tag="THANKSGIVING", source="ASSOCIATED PRESS",
         accent=ACCENTS[2], icon="storm",
         head=["MACY'S PARADE", "POSTPONED BY STORM"],
         sub="THANKSGIVING STORM BRINGS FLOODS AND "
             "400,000 POWER CUTS"),
    dict(num="04", tag="SPACEX", source="THE HINDU",
         accent=ACCENTS[3], icon="rocket",
         head=["MUSK PLEDGES SPACEX", "SHARES FOR US KIDS"],
         sub="TWO SHARES FOR EVERY US CHILD IN A PLEDGE "
             "PUT AT ABOUT $18 BILLION"),
    dict(num="05", tag="FRANCE", source="BBC",
         accent=ACCENTS[4], icon="gavel",
         head=["DEPARDIEU TO STAND", "TRIAL ON RAPE CHARGE"],
         sub="FRENCH COURT RULES ACTOR WILL FACE TRIAL "
             "OVER ALLEGED 2018 ASSAULT"),
    dict(num="06", tag="IBIZA", source="BBC",
         accent=ACCENTS[5], icon="ship",
         head=["TANKER CAPSIZES", "OFF IBIZA, 1 KILLED"],
         sub="DIESEL TANKER CARRYING UP TO 7,000 TONNES "
             "SINKS; ONE DEAD"),
]


# ---------------------------------------------------------------- icons
def draw_icon(cv, kind, x, y, s, color):
    """Draw a simple pictogram inside a square of side s at (x, y)."""
    if kind == "drone":  # quadcopter: body + 4 rotors
        cv.rect(x + 30, y + 34, 24, 16, color)           # body
        cv.circle(x + 42, y + 42, 4, BG)                 # lens
        cv.line(x + 14, y + 26, x + 30, y + 38, color, 3)
        cv.line(x + 70, y + 26, x + 54, y + 38, color, 3)
        cv.line(x + 14, y + 58, x + 30, y + 46, color, 3)
        cv.line(x + 70, y + 58, x + 54, y + 46, color, 3)
        for (rx, ry) in ((14, 22), (70, 22), (14, 62), (70, 62)):
            cv.hline(rx - 10, ry, 20, color)
            cv.circle(rx, ry, 3, color)
        cv.hline(x + 34, y + 66, 16, color)
    elif kind == "blast":  # explosion starburst
        cx, cy = x + s // 2, y + s // 2 - 4
        cv.circle(cx, cy, 12, color)
        for dx, dy in ((0, -26), (18, -18), (26, 0), (18, 18),
                       (0, 26), (-18, 18), (-26, 0), (-18, -18)):
            cv.line(cx, cy, cx + dx, cy + dy, color, 4)
        cv.circle(cx, cy, 5, BG)
        cv.hline(x + 14, y + 68, 56, color)
    elif kind == "storm":  # cloud + rain + lightning
        cv.circle(x + 30, y + 32, 12, color)
        cv.circle(x + 46, y + 26, 14, color)
        cv.circle(x + 58, y + 34, 11, color)
        cv.rect(x + 20, y + 34, 48, 10, color)
        for rx in (24, 36, 48, 60):
            cv.vline(rx, y + 52, 10, color)
        cv.line(x + 44, y + 58, x + 36, y + 74, (232, 163, 61), 3)
        cv.line(x + 36, y + 74, x + 44, y + 74, (232, 163, 61), 3)
        cv.line(x + 44, y + 74, x + 38, y + 82, (232, 163, 61), 3)
    elif kind == "rocket":  # nose up, flame below
        cv.triangle([(x + s // 2, y + 6), (x + s // 2 - 10, y + 30),
                     (x + s // 2 + 10, y + 30)], color)
        cv.rect(x + s // 2 - 10, y + 30, 20, 26, color)
        cv.triangle([(x + s // 2 - 10, y + 44), (x + s // 2 - 22, y + 58),
                     (x + s // 2 - 10, y + 56)], color)
        cv.triangle([(x + s // 2 + 10, y + 44), (x + s // 2 + 22, y + 58),
                     (x + s // 2 + 10, y + 56)], color)
        cv.triangle([(x + s // 2, y + 56), (x + s // 2 - 6, y + 72),
                     (x + s // 2 + 6, y + 72)], (232, 163, 61))
        cv.circle(x + s // 2, y + 42, 4, BG)
        cv.set(x + 10, y + 12, color)
        cv.set(x + s - 12, y + 20, color)
    elif kind == "gavel":  # judge's gavel + sounding block
        cv.line(x + 22, y + 24, x + 58, y + 48, color, 8)
        cv.rect(x + 14, y + 14, 16, 16, color)
        cv.rect(x + 54, y + 42, 16, 16, color)
        cv.line(x + 20, y + 52, x + 48, y + 70, color, 5)
        cv.hline(x + 16, y + 76, 52, color)
    elif kind == "ship":  # tanker hull + waves
        cv.rect(x + 10, y + 30, 64, 10, color)          # deck
        cv.triangle([(x + 10, y + 40), (x + 74, y + 40),
                     (x + 62, y + 58)], color)          # hull
        cv.rect(x + 52, y + 14, 8, 16, color)           # funnel
        cv.rect(x + 52, y + 14, 8, 4, (232, 163, 61))
        cv.rect(x + 24, y + 20, 18, 10, color)          # bridge
        cv.hline(x + 8, y + 66, 68, color)
        cv.hline(x + 16, y + 72, 52, color)


# ---------------------------------------------------------------- layout
def draw_header(cv):
    cv.text_centred(W // 2, 26, "THE WORLD IN ONE DAY", 6, INK)
    cv.text_centred(W // 2, 84, "27 NOVEMBER 2026", 4, ACCENTS[1])
    cv.text_centred(W // 2, 124, "SIX STORIES FROM AROUND THE GLOBE",
                    2, MUTED)
    cv.hline(16, 152, W - 32, RULE)


def draw_panel(cv, st, x0, y0, w, h):
    acc = st["accent"]
    cv.rect(x0, y0, w, h, PANEL)
    cv.rect(x0, y0, w, 6, acc)
    # number chip, top right
    cv.rect(x0 + w - 52, y0 + 16, 36, 26, PANEL2)
    cv.text(x0 + w - 45, y0 + 23, st["num"], 2, acc)
    # category tag
    cv.text(x0 + 18, y0 + 22, st["tag"], 2, acc)
    # icon box
    cv.rect(x0 + 18, y0 + 52, 84, 84, PANEL2)
    draw_icon(cv, st["icon"], x0 + 18, y0 + 52, 84, acc)
    # headline, two lines, scale 3
    hy = y0 + 58
    for line in st["head"]:
        cv.text(x0 + 118, hy, line, 3, INK)
        hy += 30
    # subline, wrapped, scale 2
    sy = y0 + 156
    for line in wrap(st["sub"], 41):
        cv.text(x0 + 18, sy, line, 2, MUTED)
        sy += 18
    # hairline above the source tag, then the tag bottom right
    cv.hline(x0 + 18, y0 + h - 46, w - 36, RULE)
    src = "SOURCE: " + st["source"]
    cv.text(x0 + w - 18 - text_width(src, 2), y0 + h - 30, src, 2, acc)


def draw_footer(cv):
    cv.text_centred(W // 2, 988,
                    "SOURCES: REUTERS - AP - BBC - NYT - THE HINDU", 2, MUTED)


def build():
    cv = Canvas(W, H, BG)
    draw_header(cv)
    px, py = 16, 168
    pw, ph = 492, 254
    for i, st in enumerate(STORIES):
        x = px + (i % 2) * (pw + 16)
        y = py + (i // 2) * (ph + 16)
        draw_panel(cv, st, x, y, pw, ph)
    draw_footer(cv)
    return cv


# ---------------------------------------------------------------- PNG out
def write_png(cv, path):
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(ctype, data):
        out = struct.pack(">I", len(data)) + ctype + data
        out += struct.pack(">I", zlib.crc32(ctype + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
           + chunk(b"IDAT", comp) + chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    size = write_png(build(), path)
    print(f"wrote {path} ({size} bytes, {W}x{H})")


if __name__ == "__main__":
    main()
