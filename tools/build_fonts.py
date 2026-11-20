#!/usr/bin/env python3
"""Build all Dot LCD .rmsfont variants for nicFW (RT-950 Pro / RT-880) from glyphs.py.

.rmsfont format (as used by nicFW RMS): 95 glyphs (ASCII 32..126), no header.
Each glyph is stored column by column, left to right; each column is H/8 bytes,
little-endian, bit 0 = top pixel.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from glyphs import load, OVR

GLYPHS = load()

def bold(ch):
    """Bold variant: every vertical stroke 2 dots wide, gaps between strokes kept."""
    if ch in OVR:
        return [[c == "#" for c in row] for row in OVR[ch]]
    L = GLYPHS[ch]
    B = [[L[r][k] if k < 5 else False for k in range(6)] for r in range(8)]
    return [[B[r][k] or (k > 0 and L[r][k-1] and not B[r][k] and not (k+1 < 6 and B[r][k+1]))
             for k in range(6)] for r in range(8)]

# style -> size -> (dot_w, dot_h, pitch_x, pitch_y, offset_y, bold)
VARIANTS = {
    "dot":       {"16x16": (2,1,3,2,1,0), "16x24": (2,2,3,3,1,0), "24x24": (3,2,4,3,1,0), "24x32": (3,3,4,4,1,0)},
    "dot-bold":  {"24x24": (2,2,3,3,1,1), "24x32": (2,3,3,4,1,1)},
    "scan":      {"8x16": (1,1,1,2,0,0), "16x16": (2,1,2,2,1,0), "16x24": (2,2,2,3,1,0),
                  "24x24": (3,2,3,3,1,0), "24x32": (3,3,3,4,1,0)},
    "scan-bold": {"8x16": (1,1,1,2,0,1), "16x16": (2,1,2,2,0,1), "16x24": (2,2,2,3,1,1),
                  "24x24": (3,2,3,3,1,1), "24x32": (3,3,3,4,1,1)},
    "solid":     {"8x8": (1,1,1,1,0,0), "8x16": (1,2,1,2,0,0), "16x16": (2,2,2,2,0,0), "16x24": (2,3,2,3,0,0)},
    "solid-bold":{"8x8": (1,1,1,1,0,1)},
}

def render(B, W, H, dw, dh, px, py, oy):
    w = len(B[0]); ox = (W - ((w - 1) * px + dw)) // 2
    p = [[0] * W for _ in range(H)]
    for r in range(8):
        for k in range(w):
            if B[r][k]:
                for y in range(oy + r*py, oy + r*py + dh):
                    for x in range(ox + k*px, ox + k*px + dw):
                        p[y][x] = 1
    return p

def encode(p, W, H):
    return b"".join(sum(p[y][x] << y for y in range(H)).to_bytes(H // 8, "little") for x in range(W))

def build(style, size):
    W, H = map(int, size.split("x")); dw, dh, px, py, oy, b = VARIANTS[style][size]
    pix = {}
    data = b""
    for c in range(32, 127):
        ch = chr(c); B = bold(ch) if b else GLYPHS[ch]
        p = render(B, W, H, dw, dh, px, py, oy); pix[ch] = p; data += encode(p, W, H)
    assert len(data) == 95 * W * H // 8
    return data, pix

def preview(pix, W, H, path, scale=3):
    from PIL import Image
    lines = ["145.5000 MHz", "Repeater WiFi", "Hello mwg MNW"]
    img = Image.new("RGB", (W * 13 * scale + 20, len(lines) * (H + 4) * scale + 20), (0, 0, 0)); yy = 10
    for t in lines:
        for i, ch in enumerate(t):
            for y in range(H):
                for x in range(W):
                    if pix[ch][y][x]:
                        X = 10 + (i * W + x) * scale
                        img.paste((125, 249, 255), (X, yy + y * scale, X + scale, yy + y * scale + scale))
        yy += (H + 4) * scale
    img.save(path)

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "fonts"
    for style, sizes in VARIANTS.items():
        d = os.path.join(out, style); os.makedirs(d, exist_ok=True)
        for size in sizes:
            data, pix = build(style, size)
            open(os.path.join(d, f"DotLCD-{style}-{size}.rmsfont"), "wb").write(data)
            W, H = map(int, size.split("x"))
            preview(pix, W, H, os.path.join(d, f"preview-{style}-{size}.png"), 2 if W >= 24 else 3)
            print(style, size, len(data))
