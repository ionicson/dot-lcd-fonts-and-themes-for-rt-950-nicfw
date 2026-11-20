import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_fonts import VARIANTS, build
from PIL import Image, ImageDraw
text = "145.500 Hello mwg"; S = 2; rows = []
for style, sizes in VARIANTS.items():
    for size in sizes:
        W, H = map(int, size.split("x")); _, pix = build(style, size); rows.append((f"{style} {size}", W, H, pix))
width = 170 + max(W * len(text) for _, W, _, _ in rows) * S
height = sum((H + 6) * S for _, _, H, _ in rows) + 20
img = Image.new("RGB", (width, height), (0, 0, 0)); dr = ImageDraw.Draw(img); yy = 10
for label, W, H, pix in rows:
    dr.text((8, yy + H * S // 2 - 6), label, fill=(150, 150, 180))
    for i, ch in enumerate(text):
        for y in range(H):
            for x in range(W):
                if pix[ch][y][x]:
                    X = 170 + (i * W + x) * S; img.paste((125, 249, 255), (X, yy + y * S, X + S, yy + y * S + S))
    yy += (H + 6) * S
img.save(sys.argv[1])
