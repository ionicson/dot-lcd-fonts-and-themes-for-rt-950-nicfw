#!/usr/bin/env python3
"""Turn a 16x16 nicFW symbols .rmsfont into a partially dotted version.

Outlines and thin lines stay solid; only solid filled areas get a 1px dot grid
(every 3rd row/column), so icons stay recognisable.
Usage: dot_symbols.py symbols.rmsfont symbols-dot.rmsfont
"""
import sys
src, dst = sys.argv[1], sys.argv[2]
d = open(src, "rb").read(); W = H = 16; n = 32
out = bytearray(d)
for i in range(len(d) // n):
    g = d[i*n:(i+1)*n]; cols = [int.from_bytes(g[x*2:x*2+2], "little") for x in range(W)]
    p = [[cols[x] >> y & 1 for x in range(W)] for y in range(H)]
    lit = lambda x, y: 0 <= x < W and 0 <= y < H and p[y][x]
    q = [r[:] for r in p]
    for y in range(H):
        for x in range(W):
            if p[y][x] and (x % 3 == 0 or y % 3 == 0) and all(lit(x+a, y+b) for a in (-1, 0, 1) for b in (-1, 0, 1)):
                q[y][x] = 0
    out[i*n:(i+1)*n] = b"".join(sum(q[y][x] << y for y in range(H)).to_bytes(2, "little") for x in range(W))
open(dst, "wb").write(bytes(out))
