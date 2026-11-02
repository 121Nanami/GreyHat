#!/usr/bin/env node
/**
 * Minimal QR encoder for terminals (byte mode, version auto 1–4).
 * No dependencies — educational / small payloads.
 */
const RESET = "\x1b[0m";
const BLACK = "\x1b[40m  " + RESET;
const WHITE = "\x1b[47m  " + RESET;

function gfMul(x, y) {
  if (!x || !y) return 0;
  let r = 0;
  while (y) {
    if (y & 1) r ^= x;
    y >>= 1;
    x <<= 1;
    if (x & 0x100) x ^= 0x11d;
  }
  return r & 0xff;
}

function rsGenerate(ecLen) {
  let gen = [1];
  for (let i = 0; i < ecLen; i++) {
    const next = new Array(gen.length + 1).fill(0);
    const factor = 1 << i; // α^i — actually need proper α; use exp table
  }
  // Proper RS using exp/log
  const exp = new Array(512);
  const log = new Array(256);
  let x = 1;
  for (let i = 0; i < 255; i++) {
    exp[i] = x;
    log[x] = i;
    x <<= 1;
    if (x & 0x100) x ^= 0x11d;
  }
  for (let i = 255; i < 512; i++) exp[i] = exp[i - 255];
  gen = [1];
  for (let i = 0; i < ecLen; i++) {
    const next = new Array(gen.length + 1).fill(0);
    for (let j = 0; j < gen.length; j++) {
      next[j] ^= gen[j];
      next[j + 1] ^= exp[(log[gen[j]] + i) % 255];
    }
    gen = next;
  }
  return { gen, exp, log };
}

function rsEncode(data, ecLen) {
  const { gen, exp, log } = rsGenerate(ecLen);
  const res = data.concat(new Array(ecLen).fill(0));
  for (let i = 0; i < data.length; i++) {
    const coef = res[i];
    if (!coef) continue;
    for (let j = 0; j < gen.length; j++) {
      res[i + j] ^= exp[(log[coef] + log[gen[j]]) % 255];
    }
  }
  return res.slice(data.length);
}

// Simplified: use a dependency-free approach — print a matrix from a tiny known algorithm
// For reliability without deps, fall back to a URL-based block QR of fixed alphabet via
// bit packing for short strings using QR version 2-L tables.

function encodeByte(str) {
  const bytes = [...Buffer.from(str, "utf8")];
  // Version capacities for ECC level L (data codewords): V1=19, V2=34, V3=55, V4=80
  const versions = [
    { v: 1, size: 21, dataCW: 19, ecCW: 7, align: [] },
    { v: 2, size: 25, dataCW: 34, ecCW: 10, align: [6, 18] },
    { v: 3, size: 29, dataCW: 55, ecCW: 15, align: [6, 22] },
    { v: 4, size: 33, dataCW: 80, ecCW: 20, align: [6, 26] },
  ];
  // Mode byte(0100) + length(8 for v<=9) + data + terminator
  let ver = null;
  for (const cand of versions) {
    const bitsNeeded = 4 + 8 + bytes.length * 8 + 4;
    const capacityBits = cand.dataCW * 8;
    if (bitsNeeded <= capacityBits) {
      ver = cand;
      break;
    }
  }
  if (!ver) {
    console.error("Text too long for this no-dep encoder (max ~70 bytes).");
    process.exit(1);
  }
  const bits = [];
  const push = (val, n) => {
    for (let i = n - 1; i >= 0; i--) bits.push((val >> i) & 1);
  };
  push(0b0100, 4);
  push(bytes.length, 8);
  for (const b of bytes) push(b, 8);
  // terminator
  const capacityBits = ver.dataCW * 8;
  const term = Math.min(4, capacityBits - bits.length);
  push(0, term);
  while (bits.length % 8) bits.push(0);
  const data = [];
  for (let i = 0; i < bits.length; i += 8) {
    let b = 0;
    for (let j = 0; j < 8; j++) b = (b << 1) | bits[i + j];
    data.push(b);
  }
  // pad codewords
  const pads = [0xec, 0x11];
  let pi = 0;
  while (data.length < ver.dataCW) {
    data.push(pads[pi % 2]);
    pi++;
  }
  const ec = rsEncode(data, ver.ecCW);
  const all = data.concat(ec);
  return place(ver, all);
}

function place(ver, codewords) {
  const n = ver.size;
  const m = Array.from({ length: n }, () => Array(n).fill(null));
  const set = (r, c, v, f = true) => {
    if (r < 0 || c < 0 || r >= n || c >= n) return;
    m[r][c] = { v, f };
  };
  // finder
  function finder(r0, c0) {
    for (let r = -1; r <= 7; r++)
      for (let c = -1; c <= 7; c++) {
        const rr = r0 + r,
          cc = c0 + c;
        if (rr < 0 || cc < 0 || rr >= n || cc >= n) continue;
        const on =
          r === -1 || c === -1 || r === 7 || c === 7
            ? false
            : r === 0 || c === 0 || r === 6 || c === 6
              ? true
              : r >= 2 && r <= 4 && c >= 2 && c <= 4;
        set(rr, cc, on ? 1 : 0);
      }
  }
  finder(0, 0);
  finder(0, n - 7);
  finder(n - 7, 0);
  // timing
  for (let i = 8; i < n - 8; i++) {
    set(6, i, i % 2 === 0 ? 1 : 0);
    set(i, 6, i % 2 === 0 ? 1 : 0);
  }
  // dark module
  set(n - 8, 8, 1);
  // alignment
  for (const ar of ver.align) {
    for (const ac of ver.align) {
      if (m[ar][ac] && m[ar][ac].f) continue;
      for (let r = -2; r <= 2; r++)
        for (let c = -2; c <= 2; c++) {
          const on = Math.max(Math.abs(r), Math.abs(c)) !== 1;
          // actually: outer ring black, inner white, center black
          const d = Math.max(Math.abs(r), Math.abs(c));
          set(ar + r, ac + c, d === 0 || d === 2 ? 1 : 0);
        }
    }
  }
  // reserve format
  for (let i = 0; i < 9; i++) {
    if (!(m[8][i] && m[8][i].f)) set(8, i, 0);
    if (!(m[i][8] && m[i][8].f)) set(i, 8, 0);
  }
  for (let i = 0; i < 8; i++) {
    if (!(m[8][n - 1 - i] && m[8][n - 1 - i].f)) set(8, n - 1 - i, 0);
    if (!(m[n - 1 - i][8] && m[n - 1 - i][8].f)) set(n - 1 - i, 8, 0);
  }

  // data bits zigzag
  const bits = [];
  for (const cw of codewords) for (let i = 7; i >= 0; i--) bits.push((cw >> i) & 1);
  let bi = 0;
  let upward = true;
  for (let col = n - 1; col > 0; col -= 2) {
    if (col === 6) col = 5;
    for (let i = 0; i < n; i++) {
      const row = upward ? n - 1 - i : i;
      for (const c of [col, col - 1]) {
        if (m[row][c] !== null && m[row][c].f) continue;
        const bit = bi < bits.length ? bits[bi++] : 0;
        m[row][c] = { v: bit, f: false };
      }
    }
    upward = !upward;
  }

  // mask 0: (r+c)%2==0 → flip — apply and write format for mask 0 ECC L
  for (let r = 0; r < n; r++)
    for (let c = 0; c < n; c++) {
      if (m[r][c].f) continue;
      if ((r + c) % 2 === 0) m[r][c].v ^= 1;
    }
  // format bits for ECC L + mask 0 = 0b01_000 + BCH → known 0x77c4 pattern bits
  const format = 0b111011111000100; // mask0 + L after XOR with mask
  const formatCoords = [];
  // horizontal near finder
  const horiz = [0, 1, 2, 3, 4, 5, 7, 8];
  // We'll place standard format info
  const fmtBits = [...format.toString(2).padStart(15, "0")].map(Number);
  const pos1 = [
    [8, 0],[8,1],[8,2],[8,3],[8,4],[8,5],[8,7],[8,8],
    [7,8],[5,8],[4,8],[3,8],[2,8],[1,8],[0,8],
  ];
  const pos2 = [
    [n-1,8],[n-2,8],[n-3,8],[n-4,8],[n-5,8],[n-6,8],[n-7,8],
    [8,n-8],[8,n-7],[8,n-6],[8,n-5],[8,n-4],[8,n-3],[8,n-2],[8,n-1],
  ];
  for (let i = 0; i < 15; i++) {
    const [r, c] = pos1[i];
    m[r][c] = { v: fmtBits[i], f: true };
    const [r2, c2] = pos2[i];
    m[r2][c2] = { v: fmtBits[i], f: true };
  }
  return m.map((row) => row.map((cell) => (cell ? cell.v : 0)));
}

function render(matrix) {
  const quiet = 2;
  const n = matrix.length;
  const lines = [];
  for (let r = -quiet; r < n + quiet; r++) {
    let line = "";
    for (let c = -quiet; c < n + quiet; c++) {
      const on = r >= 0 && c >= 0 && r < n && c < n ? matrix[r][c] === 1 : 0;
      line += on ? BLACK : WHITE;
    }
    lines.push(line);
  }
  return lines.join("\n");
}

const text = process.argv.slice(2).join(" ") || "https://greyhat.inc";
const matrix = encodeByte(text);
console.log(render(matrix));
console.log(`\n→ ${text}`);
