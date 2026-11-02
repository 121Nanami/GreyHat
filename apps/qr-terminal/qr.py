#!/usr/bin/env python3
"""
Minimal QR Code (byte mode, versions 1–3, ECC level L) for short terminal payloads.
Pure Python, no dependencies.
"""
from __future__ import annotations
import sys

# GF(256) tables for QR
_EXP = [0] * 512
_LOG = [0] * 256


def _init_gf() -> None:
    x = 1
    for i in range(255):
        _EXP[i] = x
        _LOG[x] = i
        x <<= 1
        if x & 0x100:
            x ^= 0x11D
    for i in range(255, 512):
        _EXP[i] = _EXP[i - 255]


_init_gf()


def _gf_mul(a: int, b: int) -> int:
    if a == 0 or b == 0:
        return 0
    return _EXP[_LOG[a] + _LOG[b]]


def _rs_generator(ec_len: int) -> list[int]:
    gen = [1]
    for i in range(ec_len):
        gen = [
            (gen[j] if j < len(gen) else 0)
            ^ (_gf_mul(gen[j - 1], _EXP[i]) if j > 0 else 0)
            for j in range(len(gen) + 1)
        ]
        # cleaner:
    gen = [1]
    for i in range(ec_len):
        nxt = [0] * (len(gen) + 1)
        for j, g in enumerate(gen):
            nxt[j] ^= g
            nxt[j + 1] ^= _gf_mul(g, _EXP[i])
        gen = nxt
    return gen


def _rs_encode(data: list[int], ec_len: int) -> list[int]:
    gen = _rs_generator(ec_len)
    res = data + [0] * ec_len
    for i in range(len(data)):
        coef = res[i]
        if coef == 0:
            continue
        for j, g in enumerate(gen):
            res[i + j] ^= _gf_mul(coef, g)
    return res[len(data) :]


# version: size, data codewords, ec codewords (ECC L, 1 block)
VERSIONS = {
    1: (21, 19, 7, []),
    2: (25, 34, 10, [6, 18]),
    3: (29, 55, 15, [6, 22]),
}


def _bitstream(data: bytes, version: int, capacity: int) -> list[int]:
    bits: list[int] = []

    def push(val: int, n: int) -> None:
        for i in range(n - 1, -1, -1):
            bits.append((val >> i) & 1)

    push(0b0100, 4)  # byte mode
    push(len(data), 8 if version <= 9 else 16)
    for b in data:
        push(b, 8)
    # terminator
    remaining = capacity * 8 - len(bits)
    push(0, min(4, remaining))
    while len(bits) % 8:
        bits.append(0)
    # pad bytes
    pads = [0xEC, 0x11]
    pi = 0
    codewords = []
    for i in range(0, len(bits), 8):
        byte = 0
        for j in range(8):
            byte = (byte << 1) | bits[i + j]
        codewords.append(byte)
    while len(codewords) < capacity:
        codewords.append(pads[pi % 2])
        pi += 1
    return codewords


def _place(version: int, codewords: list[int]) -> list[list[int]]:
    size, _, _, align = VERSIONS[version]
    m: list[list[int | None]] = [[None] * size for _ in range(size)]

    def set_mod(r: int, c: int, v: int, fixed: bool = True) -> None:
        if 0 <= r < size and 0 <= c < size:
            if m[r][c] is None or fixed:
                m[r][c] = v if not fixed else v  # store as int; track fixed separately
        # use parallel fixed map
    fixed = [[False] * size for _ in range(size)]

    def put(r: int, c: int, v: int, is_fixed: bool = True) -> None:
        if 0 <= r < size and 0 <= c < size:
            m[r][c] = v
            if is_fixed:
                fixed[r][c] = True

    def finder(r0: int, c0: int) -> None:
        for r in range(-1, 8):
            for c in range(-1, 8):
                rr, cc = r0 + r, c0 + c
                if not (0 <= rr < size and 0 <= cc < size):
                    continue
                if r in (-1, 7) or c in (-1, 7):
                    put(rr, cc, 0)
                elif r in (0, 6) or c in (0, 6):
                    put(rr, cc, 1)
                elif 2 <= r <= 4 and 2 <= c <= 4:
                    put(rr, cc, 1)
                else:
                    put(rr, cc, 0)

    finder(0, 0)
    finder(0, size - 7)
    finder(size - 7, 0)

    for i in range(8, size - 8):
        put(6, i, 1 if i % 2 == 0 else 0)
        put(i, 6, 1 if i % 2 == 0 else 0)

    put(size - 8, 8, 1)  # dark module

    for ar in align:
        for ac in align:
            if fixed[ar][ac]:
                continue
            for r in range(-2, 3):
                for c in range(-2, 3):
                    d = max(abs(r), abs(c))
                    put(ar + r, ac + c, 1 if d in (0, 2) else 0)

    # reserve format areas
    for i in range(9):
        if not fixed[8][i]:
            put(8, i, 0)
        if not fixed[i][8]:
            put(i, 8, 0)
    for i in range(8):
        if not fixed[8][size - 1 - i]:
            put(8, size - 1 - i, 0)
        if not fixed[size - 1 - i][8]:
            put(size - 1 - i, 8, 0)

    # data bits
    bits: list[int] = []
    for cw in codewords:
        for i in range(7, -1, -1):
            bits.append((cw >> i) & 1)

    bi = 0
    upward = True
    col = size - 1
    while col > 0:
        if col == 6:
            col = 5
        for i in range(size):
            row = (size - 1 - i) if upward else i
            for c in (col, col - 1):
                if fixed[row][c]:
                    continue
                bit = bits[bi] if bi < len(bits) else 0
                bi += 1
                put(row, c, bit, is_fixed=False)
        upward = not upward
        col -= 2

    # mask 0: (r+c) even → flip; apply only to non-fixed
    for r in range(size):
        for c in range(size):
            if fixed[r][c]:
                continue
            if (r + c) % 2 == 0:
                m[r][c] = 1 - int(m[r][c] or 0)

    # format info: ECC L (01) + mask 0 (000) → 0b00000, BCH → known pattern after mask
    # Precomputed format bits for (ecc=L, mask=0): 0x77C4 → binary
    fmt = 0b111011111000100
    coords_a = [
        (8, 0), (8, 1), (8, 2), (8, 3), (8, 4), (8, 5), (8, 7), (8, 8),
        (7, 8), (5, 8), (4, 8), (3, 8), (2, 8), (1, 8), (0, 8),
    ]
    coords_b = [
        (size - 1, 8), (size - 2, 8), (size - 3, 8), (size - 4, 8),
        (size - 5, 8), (size - 6, 8), (size - 7, 8),
        (8, size - 8), (8, size - 7), (8, size - 6), (8, size - 5),
        (8, size - 4), (8, size - 3), (8, size - 2), (8, size - 1),
    ]
    for i in range(15):
        bit = (fmt >> (14 - i)) & 1
        r, c = coords_a[i]
        put(r, c, bit)
        r, c = coords_b[i]
        put(r, c, bit)

    return [[int(v or 0) for v in row] for row in m]


def encode(text: str) -> list[list[int]]:
    data = text.encode("utf-8")
    for version, (size, data_cw, ec_cw, _) in VERSIONS.items():
        # capacity check: mode+len+data+term rough
        if 4 + 8 + len(data) * 8 + 4 <= data_cw * 8:
            cws = _bitstream(data, version, data_cw)
            ec = _rs_encode(cws, ec_cw)
            return _place(version, cws + ec)
    raise SystemExit("Text too long (max ~50 bytes for this mini encoder).")


def render(matrix: list[list[int]]) -> str:
    black, white = "\033[40m  \033[0m", "\033[47m  \033[0m"
    q = 2
    n = len(matrix)
    lines = []
    for r in range(-q, n + q):
        row = []
        for c in range(-q, n + q):
            on = 0 <= r < n and 0 <= c < n and matrix[r][c] == 1
            row.append(black if on else white)
        lines.append("".join(row))
    return "\n".join(lines)


def main() -> int:
    text = " ".join(sys.argv[1:]) or "https://greyhat.inc"
    matrix = encode(text)
    print(render(matrix))
    print(f"\n→ {text}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
