#!/usr/bin/env python3
"""Draw a 1024x1024 PNG infographic summing up Friday 27 November 2026.

Six verified world-news stories, drawn with a small built-in bitmap font.
Python 3.13 standard library only; no network; fully deterministic output.
"""

import os
import struct
import zlib

WIDTH = 1024
HEIGHT = 1024

# ---------------------------------------------------------------------------
# Colours
# ---------------------------------------------------------------------------
PAPER = (244, 241, 232)
INK = (18, 32, 54)
NAVY = (16, 35, 62)
GOLD = (198, 154, 52)
CARD = (255, 255, 255)
GREY = (90, 98, 110)
ACCENTS = [
    (178, 44, 38),    # story 1: red
    (24, 84, 130),    # story 2: steel blue
    (16, 122, 106),   # story 3: teal
    (104, 64, 150),   # story 4: purple
    (196, 110, 16),   # story 5: amber
    (28, 110, 44),    # story 6: green
]

# ---------------------------------------------------------------------------
# 5x7 bitmap font, drawn from a plain grid ('#' = on, '.' = off).
# Uppercase letters, digits and common punctuation; input is uppercased.
# ---------------------------------------------------------------------------
FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#..##", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "/": ("....#", "....#", "...#.", "...#.", "..#..", ".#...", "#...."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "%": ("##..#", "##.#.", "...#.", "..#..", ".#...", "#.#.#", "#..##"),
    "+": (".....", "..#..", "..#..", ".###.", "..#..", "..#..", "....."),
    "&": (".##..", "#..#.", "#..#.", ".#...", "#.#.#", "#..#.", ".##.#"),
    "=": (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
}

# ---------------------------------------------------------------------------
# Pixel canvas
# ---------------------------------------------------------------------------
class Canvas:
    def __init__(self, width, height, colour):
        self.width = width
        self.height = height
        self.pixels = bytearray(width * height * 3)
        r, g, b = colour
        for i in range(0, len(self.pixels), 3):
            self.pixels[i] = r
            self.pixels[i + 1] = g
            self.pixels[i + 2] = b

    def set_pixel(self, x, y, colour):
        if 0 <= x < self.width and 0 <= y < self.height:
            i = (y * self.width + x) * 3
            self.pixels[i], self.pixels[i + 1], self.pixels[i + 2] = colour

    def fill_rect(self, x, y, w, h, colour):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.width, x + w)
        y1 = min(self.height, y + h)
        r, g, b = colour
        for yy in range(y0, y1):
            base = (yy * self.width + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.pixels[i] = r
                self.pixels[i + 1] = g
                self.pixels[i + 2] = b

    def text_width(self, text, scale):
        return len(text) * 6 * scale - scale

    def draw_text(self, x, y, text, scale, colour):
        cx = x
        for ch in text.upper():
            glyph = FONT.get(ch, FONT[" "])
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == "#":
                        self.fill_rect(
                            cx + col * scale, y + row * scale, scale, scale, colour
                        )
            cx += 6 * scale

    def draw_text_centred(self, cx, y, text, scale, colour):
        x = cx - self.text_width(text, scale) // 2
        self.draw_text(x, y, text, scale, colour)


def wrap_text(text, max_chars):
    """Greedy word wrap into lines of at most max_chars characters."""
    words = text.split(" ")
    lines = []
    current = ""
    for word in words:
        trial = word if not current else current + " " + word
        if len(trial) <= max_chars:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


# ---------------------------------------------------------------------------
# PNG encoding (colour type 2, 8-bit RGB, filter 0 on every scanline)
# ---------------------------------------------------------------------------
def png_chunk(kind, data):
    chunk = struct.pack(">I", len(data)) + kind + data
    chunk += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return chunk


def encode_png(canvas):
    raw = bytearray()
    stride = canvas.width * 3
    for y in range(canvas.height):
        raw.append(0)
        start = y * stride
        raw += canvas.pixels[start:start + stride]
    ihdr = struct.pack(">IIBBBBB", canvas.width, canvas.height, 8, 2, 0, 0, 0)
    blob = b"\x89PNG\r\n\x1a\n"
    blob += png_chunk(b"IHDR", ihdr)
    blob += png_chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    blob += png_chunk(b"IEND", b"")
    return blob


# ---------------------------------------------------------------------------
# The day's news: six verified stories of Friday 27 November 2026.
# ---------------------------------------------------------------------------
STORIES = [
    {
        "headline": "TWO ITALIANS KILLED IN DRONE STRIKE IN KUWAIT",
        "fact": "Iran denies any role. The victims were Rheinmetall Italia "
                "technicians; two more people were wounded, a Kuwaiti and "
                "a Pakistani.",
        "source": "REUTERS",
    },
    {
        "headline": "ISRAEL KILLS 9 IN GAZA OVERNIGHT",
        "fact": "Strikes hit Deir Al-Balah and Gaza City. The dead include a "
                "Hamas-appointed deputy education minister; Netanyahu says "
                "about 80 militants were killed in the past month.",
        "source": "REUTERS",
    },
    {
        "headline": "THANKSGIVING STORM POSTPONES MACY'S PARADE",
        "fact": "More than 400,000 people lose power across several US "
                "states as the storm sweeps in over the holiday.",
        "source": "AP",
    },
    {
        "headline": "MUSK PLEDGES TWO SPACEX SHARES FOR EVERY US CHILD",
        "fact": "The giveaway is worth about $18 billion, Musk says, for "
                "every child in the United States.",
        "source": "THE HINDU",
    },
    {
        "headline": "DEPARDIEU TO STAND TRIAL ON RAPE CHARGE",
        "fact": "A French court rules the actor must face trial over an "
                "alleged assault in 2018.",
        "source": "BBC",
    },
    {
        "headline": "DIESEL TANKER CAPSIZES OFF IBIZA",
        "fact": "One person is killed as the tanker, carrying up to 7,000 "
                "tonnes of diesel, goes down off the island.",
        "source": "BBC",
    },
]


def draw_card(canvas, x, y, w, h, story, accent):
    canvas.fill_rect(x, y, w, h, CARD)
    canvas.fill_rect(x, y, w, 10, accent)
    # Thin outline so cards read on the paper background.
    canvas.fill_rect(x, y + h - 2, w, 2, (210, 204, 190))
    inner = x + 18
    text_w = w - 36
    # Headline, scale 3: 6 chars fit per 18 px of width.
    headline_lines = wrap_text(story["headline"], text_w // 18)
    hy = y + 26
    for line in headline_lines:
        canvas.draw_text(inner, hy, line, 3, INK)
        hy += 26
    # Fact, scale 2.
    fact_lines = wrap_text(story["fact"], text_w // 12)
    fy = hy + 10
    for line in fact_lines:
        canvas.draw_text(inner, fy, line, 2, (52, 60, 72))
        fy += 18
    # Source tag at the bottom of the card.
    canvas.draw_text(inner, y + h - 30, "SOURCE: " + story["source"], 2, accent)


def draw_infographic():
    canvas = Canvas(WIDTH, HEIGHT, PAPER)

    # Header band.
    canvas.fill_rect(0, 0, WIDTH, 150, NAVY)
    canvas.fill_rect(0, 150, WIDTH, 5, GOLD)
    canvas.draw_text_centred(WIDTH // 2, 28, "WORLD NEWS", 6, (255, 255, 255))
    canvas.draw_text_centred(
        WIDTH // 2, 96, "FRIDAY 27 NOVEMBER 2026", 3, (214, 182, 110)
    )

    # Standfirst, with a short gold rule beneath it.
    canvas.draw_text_centred(
        WIDTH // 2, 170, "SIX STORIES FROM AROUND THE WORLD", 2, GREY
    )
    canvas.fill_rect(WIDTH // 2 - 200, 194, 400, 2, GOLD)

    # Six cards: two columns, three rows.
    margin = 24
    gutter_x = 20
    gutter_y = 14
    card_w = (WIDTH - 2 * margin - gutter_x) // 2
    card_h = 250
    top = 200
    for i, story in enumerate(STORIES):
        col = i % 2
        row = i // 2
        cx = margin + col * (card_w + gutter_x)
        cy = top + row * (card_h + gutter_y)
        draw_card(canvas, cx, cy, card_w, card_h, story, ACCENTS[i])

    # Footer.
    canvas.draw_text_centred(
        WIDTH // 2,
        992,
        "REPORTED BY REUTERS, AP, BBC AND THE HINDU",
        2,
        GREY,
    )
    return canvas


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    canvas = draw_infographic()
    blob = encode_png(canvas)
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as fh:
        fh.write(blob)


if __name__ == "__main__":
    main()
