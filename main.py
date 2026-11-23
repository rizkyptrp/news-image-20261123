#!/usr/bin/env python3
"""news-image-20261123: a newspaper front page summing up the world news of
Monday 23 November 2026, drawn as a 1024x1024 PNG.

Everything is drawn by this program with the Python standard library only:
a tiny PNG writer (struct + zlib), a 5x7 bitmap font written out below, and
small vector-style scene drawings for each story. No network, no files read,
no randomness, no time: two runs write byte-identical output.

Run:  mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (247, 242, 230)      # newsprint cream
CARD = (255, 253, 247)       # card white
INK = (24, 24, 24)
NAVY = (20, 36, 60)
NAVY2 = (32, 54, 86)
RED = (178, 36, 28)
GOLD = (214, 162, 62)
RULE = (205, 198, 180)
GREY = (88, 88, 84)
WHITE = (255, 255, 255)
SKY = (214, 230, 242)
SEA = (196, 222, 235)
LEAF = (74, 140, 84)
FLAME = (238, 118, 34)
FLAME2 = (250, 198, 60)

# ---------------------------------------------------------------- 5x7 font
# Glyphs as 7 rows of 5 cells; '#' is ink, '.' is blank.
FONT = {
    'A': (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'B': ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    'C': (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    'D': ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    'E': ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    'F': ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    'G': (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    'H': ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'I': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    'J': ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    'K': ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    'L': ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    'M': ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    'N': ("#...#", "##..#", "#.#.#", "#.#.#", "#..##", "#..##", "#...#"),
    'O': (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'P': ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    'Q': (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    'R': ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    'S': (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    'T': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    'U': ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'V': ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'W': ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    'X': ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    'Y': ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    'Z': ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    'a': (".....", ".....", ".###.", "....#", ".####", "#...#", ".####"),
    'b': ("#....", "#....", "####.", "#...#", "#...#", "#...#", "####."),
    'c': (".....", ".....", ".####", "#....", "#....", "#....", ".####"),
    'd': ("....#", "....#", ".####", "#...#", "#...#", "#...#", ".####"),
    'e': (".....", ".....", ".###.", "#...#", "#####", "#....", ".###."),
    'f': ("..##.", ".#..#", ".#...", "####.", ".#...", ".#...", ".#..."),
    'g': (".....", ".....", ".####", "#...#", "#...#", ".####", "....#"),
    'h': ("#....", "#....", "####.", "#...#", "#...#", "#...#", "#...#"),
    'i': (".....", "..#..", ".....", ".##..", "..#..", "..#..", ".###."),
    'j': ("...#.", ".....", "..##.", "...#.", "...#.", "...#.", ".##.."),
    'k': ("#....", "#....", "#..#.", "#.#..", "##...", "#.#..", "#..#."),
    'l': (".##..", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    'm': (".....", ".....", "##.#.", "#.#.#", "#.#.#", "#.#.#", "#.#.#"),
    'n': (".....", ".....", "####.", "#...#", "#...#", "#...#", "#...#"),
    'o': (".....", ".....", ".###.", "#...#", "#...#", "#...#", ".###."),
    'p': (".....", ".....", "####.", "#...#", "#...#", "####.", "#...."),
    'q': (".....", ".....", ".####", "#...#", "#...#", ".####", "....#"),
    'r': (".....", ".....", "#.##.", "##..#", "#....", "#....", "#...."),
    's': (".....", ".....", ".####", "#....", ".###.", "....#", "####."),
    't': (".#...", ".#...", "####.", ".#...", ".#...", ".#...", "..##."),
    'u': (".....", ".....", "#...#", "#...#", "#...#", "#..##", ".##.#"),
    'v': (".....", ".....", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'w': (".....", ".....", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#."),
    'x': (".....", ".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#"),
    'y': (".....", ".....", "#...#", "#...#", ".####", "....#", ".###."),
    'z': (".....", ".....", "#####", "...#.", "..#..", ".#...", "#####"),
    '0': (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    '1': ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    '2': (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    '3': ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    '4': ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    '5': ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    '6': (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    '7': ("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."),
    '8': (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    '9': (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    ' ': (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    '.': (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ',': (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ':': (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ';': (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    "'": ("..#..", "..#..", "..#..", ".....", ".....", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."),
    '-': (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    '(': ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ')': (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    '/': ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    '&': (".###.", "#...#", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    '$': ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    '%': ("##..#", "##.#.", "...#.", "..#..", ".#...", "#.##.", "#..##"),
    '!': ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    '?': (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    '=': (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    '+': (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
}

# ---------------------------------------------------------------- canvas
class Page:
    """A 1024x1024 RGB canvas with simple drawing helpers."""

    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.buf = bytearray(w * h * 3)
        self.box(0, 0, w, h, bg)

    def px(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i], self.buf[i + 1], self.buf[i + 2] = c

    def box(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.buf[i], self.buf[i + 1], self.buf[i + 2] = c

    def frame(self, x, y, w, h, c, t=2):
        self.box(x, y, w, t, c)
        self.box(x, y + h - t, w, t, c)
        self.box(x, y, t, h, c)
        self.box(x + w - t, y, t, h, c)

    def hline(self, x0, x1, y, c, t=1):
        self.box(min(x0, x1), y, abs(x1 - x0) + 1, t, c)

    def vline(self, x, y0, y1, c, t=1):
        self.box(x, min(y0, y1), t, abs(y1 - y0) + 1, c)

    def dline(self, x0, y0, x1, y1, c, t=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            for a in range(t):
                for b in range(t):
                    self.px(x0 + a, y0 + b, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, r, c):
        for yy in range(-r, r + 1):
            dx = int((r * r - yy * yy) ** 0.5)
            for xx in range(-dx, dx + 1):
                self.px(cx + xx, cy + yy, c)

    def ring(self, cx, cy, r, c, t=3):
        for yy in range(-r, r + 1):
            for xx in range(-r, r + 1):
                d2 = xx * xx + yy * yy
                if (r - t) * (r - t) <= d2 <= r * r:
                    self.px(cx + xx, cy + yy, c)

    def oval(self, cx, cy, rx, ry, c):
        for yy in range(-ry, ry + 1):
            dx = int(rx * (1 - (yy / ry) ** 2) ** 0.5) if ry else 0
            for xx in range(-dx, dx + 1):
                self.px(cx + xx, cy + yy, c)

    def poly(self, pts, c):
        ys = [p[1] for p in pts]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) / (y1 - y0) * (x1 - x0))
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                for x in range(int(xs[k]), int(xs[k + 1]) + 1):
                    self.px(x, y, c)

    def tri(self, x0, y0, x1, y1, x2, y2, c):
        self.poly([(x0, y0), (x1, y1), (x2, y2)], c)

    # ---- text ----
    @staticmethod
    def tw(s, sc):
        return len(s) * 6 * sc

    def put(self, x, y, s, sc, c):
        cx = x
        for ch in s:
            gl = FONT.get(ch)
            if gl is None:
                cx += 6 * sc
                continue
            for r, row in enumerate(gl):
                for col, bit in enumerate(row):
                    if bit == '#':
                        self.box(cx + col * sc, y + r * sc, sc, sc, c)
            cx += 6 * sc
        return cx

    def centre(self, cx, y, s, sc, c):
        self.put(cx - self.tw(s, sc) // 2, y, s, sc, c)

    def wrap(self, s, sc, width):
        lines, cur = [], ""
        for word in s.split(" "):
            trial = (cur + " " + word).strip()
            if self.tw(trial, sc) <= width:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines

    def para(self, x, y, s, sc, width, c, lh=None):
        if lh is None:
            lh = 8 * sc
        for line in self.wrap(s, sc, width):
            self.put(x, y, line, sc, c)
            y += lh
        return y

# ---------------------------------------------------------------- PNG
def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    return out + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)


def write_png(path, pg):
    raw = b"".join(b"\x00" + bytes(pg.buf[y * W * 3:(y + 1) * W * 3])
                   for y in range(H))
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    data = (b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr)
            + _chunk(b"IDAT", zlib.compress(raw, 9)) + _chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(data)

# ---------------------------------------------------------------- scenes
# Each scene draws a small illustration inside a (x, y, w, h) box.

def scene_climate(pg, x, y, w, h):
    """Lead: COP31 fails - a warming globe under a harsh sun."""
    pg.box(x, y, w, h, SKY)
    cx, cy = x + w // 2 - 20, y + h // 2 + 8
    # sun, top right
    sx, sy = x + w - 42, y + 34
    for dx, dy in ((0, -22), (0, 22), (-22, 0), (22, 0),
                   (-16, -16), (16, -16), (-16, 16), (16, 16)):
        pg.dline(sx, sy, sx + dx, sy + dy, FLAME2, 3)
    pg.disc(sx, sy, 15, FLAME)
    pg.disc(sx, sy, 10, FLAME2)
    # globe
    pg.disc(cx, cy, 70, (52, 110, 180))
    pg.ring(cx, cy, 70, NAVY2, 3)
    pg.oval(cx - 30, cy - 20, 30, 16, LEAF)
    pg.oval(cx + 24, cy + 8, 26, 18, LEAF)
    pg.oval(cx - 8, cy + 38, 20, 11, LEAF)
    pg.disc(cx - 38, cy - 38, 11, WHITE)
    pg.disc(cx + 38, cy + 40, 9, WHITE)


def scene_tanker(pg, x, y, w, h):
    """Hormuz: a tanker on fire."""
    pg.box(x, y, w, h, SEA)
    # sky smoke
    pg.disc(x + 40, y + 26, 12, (120, 120, 116))
    pg.disc(x + 62, y + 20, 15, (140, 140, 134))
    pg.disc(x + 86, y + 28, 11, (120, 120, 116))
    # flames on the deck
    fx = x + w // 2
    pg.tri(fx - 34, y + 84, fx + 34, y + 84, fx, y + 30, FLAME)
    pg.tri(fx - 18, y + 84, fx + 18, y + 84, fx, y + 48, FLAME2)
    # hull
    pg.box(x + 8, y + 84, w - 16, 30, (40, 44, 52))
    pg.box(x + 8, y + 84, w - 16, 5, RED)
    # bridge tower
    pg.box(x + w - 44, y + 52, 30, 32, WHITE)
    for r in range(2):
        pg.box(x + w - 40, y + 58 + r * 11, 22, 6, NAVY2)
    # waves
    for wy in (y + h - 16, y + h - 8):
        for wx in range(x + 4, x + w - 4, 22):
            pg.dline(wx, wy, wx + 11, wy - 5, (90, 150, 180), 2)


def scene_kyiv(pg, x, y, w, h):
    """Ukraine: a drone over a damaged apartment block."""
    pg.box(x, y, w, h, (226, 228, 232))
    base = y + h - 14
    # damaged block, jagged roofline
    pg.poly([(x + 8, base), (x + 8, y + 52), (x + 24, y + 38),
             (x + 34, y + 54), (x + 50, y + 34), (x + 66, y + 52),
             (x + 66, base)], (110, 100, 88))
    for wy in (y + 70, y + 92, y + 114):
        pg.box(x + 17, wy, 10, 12, (52, 48, 42))
        pg.box(x + 41, wy, 10, 12, (52, 48, 42))
    # rubble
    pg.tri(x + 22, base, x + 40, base, x + 31, base - 12, (140, 130, 116))
    pg.tri(x + 46, base, x + 58, base, x + 52, base - 8, (160, 150, 136))
    # drone top right
    dx, dy = x + w - 34, y + 30
    pg.box(dx - 14, dy - 3, 28, 6, INK)
    pg.box(dx - 3, dy - 8, 6, 16, INK)
    pg.disc(dx - 16, dy - 6, 5, (90, 90, 90))
    pg.disc(dx + 16, dy - 6, 5, (90, 90, 90))
    pg.hline(dx - 26, dx - 6, dy - 8, INK, 2)
    pg.hline(dx + 6, dx + 26, dy - 8, INK, 2)
    pg.disc(dx, dy + 4, 3, RED)


def scene_cartel(pg, x, y, w, h):
    """Mexico: a sheriff's star badge over handcuffs."""
    pg.box(x, y, w, h, (238, 232, 214))
    cx, cy = x + w // 2, y + h // 2 - 14
    # star badge
    import math
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        r = 46 if i % 2 == 0 else 19
        pts.append((int(cx + r * math.cos(ang)), int(cy + r * math.sin(ang))))
    pg.poly(pts, GOLD)
    pg.disc(cx, cy, 20, NAVY2)
    pg.ring(cx, cy, 20, WHITE, 2)
    pg.put(cx - 6, cy - 8, "$", 2, WHITE)
    # handcuffs below
    hy = y + h - 34
    pg.ring(x + 34, hy, 13, INK, 4)
    pg.ring(x + w - 34, hy, 13, INK, 4)
    pg.dline(x + 34, hy, x + w - 34, hy, INK, 4)


def scene_robot(pg, x, y, w, h):
    """UN AI weapons: a robot head with a red 'no' ring."""
    pg.box(x, y, w, h, (220, 236, 236))
    cx, cy = x + w // 2, y + h // 2
    # antenna
    pg.vline(cx, cy - 62, cy - 40, INK, 3)
    pg.disc(cx, cy - 66, 5, RED)
    # head
    pg.box(cx - 34, cy - 40, 68, 52, (160, 170, 178))
    pg.frame(cx - 34, cy - 40, 68, 52, INK, 3)
    pg.disc(cx - 16, cy - 18, 7, (40, 180, 220))
    pg.disc(cx + 16, cy - 18, 7, (40, 180, 220))
    pg.box(cx - 12, cy + 2, 24, 4, INK)
    # ears
    pg.box(cx - 42, cy - 26, 8, 16, INK)
    pg.box(cx + 34, cy - 26, 8, 16, INK)
    # red prohibition ring over the head
    pg.ring(cx, cy - 12, 56, RED, 6)
    pg.dline(cx - 40, cy + 28, cx + 40, cy - 52, RED, 6)


def scene_factory(pg, x, y, w, h):
    """Indonesia: a factory on fire."""
    pg.box(x, y, w, h, (248, 230, 205))
    base = y + h - 14
    # sawtooth factory
    pg.poly([(x + 10, base), (x + 10, y + 70), (x + 34, y + 48),
             (x + 58, y + 70), (x + 82, y + 48), (x + 106, y + 70),
             (x + 106, base)], (96, 88, 76))
    for wx in (x + 20, x + 46, x + 72):
        pg.box(wx, y + 92, 12, 12, (250, 200, 60))
    # chimney with smoke
    pg.box(x + w - 30, y + 34, 16, base - y - 48, (70, 66, 60))
    pg.disc(x + w - 22, y + 22, 9, (150, 150, 144))
    pg.disc(x + w - 12, y + 12, 11, (170, 170, 162))
    # flame at the roof
    fx = x + 58
    pg.tri(fx - 20, y + 52, fx + 20, y + 52, fx, y + 16, FLAME)
    pg.tri(fx - 10, y + 52, fx + 10, y + 52, fx, y + 30, FLAME2)
    # warning triangle
    tx, ty = x + 18, y + 18
    pg.tri(tx, ty + 22, tx + 24, ty + 22, tx + 12, ty, GOLD)
    pg.put(tx + 9, ty + 10, "!", 1, INK)


def scene_cricket(pg, x, y, w, h):
    """Also today: cricket bat and ball."""
    pg.box(x, y, w, h, (216, 238, 210))
    cx, cy = x + w // 2, y + h // 2
    # bat, leaning: flat blade with a handle
    pg.poly([(cx - 2, cy - 40), (cx + 14, cy - 34), (cx + 22, cy + 34),
             (cx + 6, cy + 40)], (210, 170, 110))
    pg.dline(cx - 2, cy - 40, cx - 12, cy - 62, INK, 5)
    # ball
    pg.disc(cx + 42, cy + 30, 13, RED)
    pg.ring(cx + 42, cy + 30, 13, WHITE, 2)
    # stumps
    for sx in (cx - 52, cx - 40, cx - 28):
        pg.vline(sx, cy + 18, cy + 52, GOLD, 4)
    pg.hline(cx - 54, cx - 26, cy + 16, GOLD, 3)


# ---------------------------------------------------------------- content
LEAD = ("LEAD STORY  |  CLIMATE",
        "CLIMATE TALKS COLLAPSE IN TURKIYE",
        "COP31 ends with no deal on fossil fuels. Australia's PM calls "
        "the failure a sign of difficult geopolitical times.",
        scene_climate)

STORIES = [
    ("IRAN WAR", "TANKERS ABLAZE IN HORMUZ",
     "Iran sets tankers ablaze as the war widens; Saudi and Bahrain are hit.",
     scene_tanker),
    ("UKRAINE", "DRONE HITS FLATS NEAR KYIV",
     "At least 14 missing; a Russian cargo ship still burns off Finland.",
     scene_kyiv),
    ("MEXICO", "CARTEL BOSS CAUGHT IN SINALOA",
     "FBI's most-wanted 'El Chapo Isidro' seized; 11 killed in gun battles.",
     scene_cartel),
    ("UNITED NATIONS", "NO RULES YET FOR AI WEAPONS",
     "Geneva talks on killer robots run two more years, no binding rules.",
     scene_robot),
    ("INDONESIA", "FACTORY FIRE: DOZENS MISSING",
     "Rescuers search the ruins as the toll climbs and many remain missing.",
     scene_factory),
]

ALSO = [
    "Seoul minister quits over AI exam cheating",
    "Nepal PM meets Modi in New Delhi",
    "India posts record 720/9 in Wellington Test",
]


def draw(pg):
    # ---- masthead ----
    pg.box(0, 0, W, 150, NAVY)
    pg.box(0, 150, W, 6, RED)
    pg.centre(W // 2, 24, "THE WORLD TODAY", 6, WHITE)
    pg.centre(W // 2, 96, "MONDAY 23 NOVEMBER 2026", 4, GOLD)
    pg.hline(24, W - 24, 84, (64, 84, 114), 1)

    # ---- lead story ----
    lx, ly, lw, lh = 24, 170, W - 48, 250
    pg.box(lx, ly, lw, lh, CARD)
    pg.frame(lx, ly, lw, lh, RULE, 2)
    pg.box(lx, ly, lw, 6, RED)
    kicker, headline, sub, scene = LEAD
    scene(pg, lx + 14, ly + 20, 300, lh - 34)
    tx = lx + 330
    tw = lw - 346
    pg.put(tx, ly + 26, kicker, 2, RED)
    y = pg.para(tx, ly + 56, headline, 4, tw, INK, lh=34)
    y = pg.para(tx, y + 12, sub, 2, tw, (58, 58, 56), lh=18)
    pg.hline(tx, tx + 120, y + 10, RED, 3)

    # ---- grid: five stories + also today ----
    gx, gy = 24, 436
    cw, ch, gap = 480, 172, 16
    cells = STORIES + [None]
    for i, story in enumerate(cells):
        cx = gx + (i % 2) * (cw + gap)
        cy = gy + (i // 2) * (ch + 12)
        pg.box(cx, cy, cw, ch, CARD)
        pg.frame(cx, cy, cw, ch, RULE, 2)
        if story is None:
            scene_cricket(pg, cx + 12, cy + 12, 138, ch - 24)
            tx2 = cx + 162
            pg.put(tx2, cy + 14, "ALSO TODAY", 2, RED)
            y2 = cy + 42
            for item in ALSO:
                y2 = pg.para(tx2, y2, item, 2, cw - 174, INK, lh=16)
                y2 += 6
            continue
        kicker, headline, sub, scene = story
        scene(pg, cx + 12, cy + 12, 138, ch - 24)
        tx2 = cx + 162
        pg.put(tx2, cy + 14, kicker, 2, RED)
        y2 = pg.para(tx2, cy + 40, headline, 3, cw - 174, INK, lh=24)
        pg.para(tx2, y2 + 6, sub, 2, cw - 174, GREY, lh=16)

    # ---- footer ----
    pg.hline(24, W - 24, 984, RULE, 2)
    pg.centre(W // 2, 996, "ALL STORIES REPORTED ON MONDAY 23 NOVEMBER 2026",
              2, GREY)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "./out")
    os.makedirs(out_dir, exist_ok=True)
    pg = Page(W, H, PAPER)
    draw(pg)
    write_png(os.path.join(out_dir, "entry.png"), pg)


if __name__ == "__main__":
    main()
