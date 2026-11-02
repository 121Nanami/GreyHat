#!/usr/bin/env node
/** Markdown → single-file HTML slide deck (--- separated). */
const fs = require("fs");
const path = require("path");

const src = process.argv[2];
const out = process.argv[3] || "slides.html";
if (!src) {
  console.error("Usage: node slide.js input.md [out.html]");
  process.exit(1);
}

function esc(s) {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function inline(s) {
  return esc(s)
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
    .replace(/\*([^*]+)\*/g, "<em>$1</em>");
}

function mdToHtml(md) {
  const lines = md.replace(/\r\n/g, "\n").split("\n");
  const html = [];
  let inUl = false;
  const closeUl = () => {
    if (inUl) {
      html.push("</ul>");
      inUl = false;
    }
  };
  for (const line of lines) {
    if (/^### /.test(line)) {
      closeUl();
      html.push(`<h3>${inline(line.slice(4))}</h3>`);
    } else if (/^## /.test(line)) {
      closeUl();
      html.push(`<h2>${inline(line.slice(3))}</h2>`);
    } else if (/^# /.test(line)) {
      closeUl();
      html.push(`<h1>${inline(line.slice(2))}</h1>`);
    } else if (/^[-*] /.test(line)) {
      if (!inUl) {
        html.push("<ul>");
        inUl = true;
      }
      html.push(`<li>${inline(line.slice(2))}</li>`);
    } else if (line.trim() === "") {
      closeUl();
    } else {
      closeUl();
      html.push(`<p>${inline(line)}</p>`);
    }
  }
  closeUl();
  return html.join("\n");
}

const raw = fs.readFileSync(src, "utf8");
const slides = raw.split(/\n---\n/).map((s) => mdToHtml(s.trim()));
const html = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<title>${esc(path.basename(src))}</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600&family=IBM+Plex+Sans:wght@400;500&display=swap');
  :root { --bg:#0f1c18; --fg:#e8f5e9; --accent:#7CFFB2; }
  * { box-sizing:border-box; }
  body { margin:0; font-family:'IBM Plex Sans',sans-serif; background:radial-gradient(1200px 600px at 20% 0%,#1b3a2f,var(--bg)); color:var(--fg); height:100vh; overflow:hidden; }
  .slide { display:none; height:100vh; padding:8vh 10vw; }
  .slide.active { display:flex; flex-direction:column; justify-content:center; animation:in .35s ease; }
  @keyframes in { from{opacity:0; transform:translateY(12px);} to{opacity:1; transform:none;} }
  h1,h2,h3 { font-family:Fraunces,serif; font-weight:600; margin:0 0 .4em; letter-spacing:-.02em; }
  h1 { font-size:clamp(2.4rem,6vw,4.5rem); color:var(--accent); }
  h2 { font-size:clamp(1.8rem,4vw,3rem); }
  p,li { font-size:clamp(1.1rem,2.2vw,1.5rem); line-height:1.5; max-width:40ch; }
  code { background:#244438; padding:.1em .35em; border-radius:4px; }
  .hud { position:fixed; bottom:1.2rem; right:1.5rem; opacity:.55; font-size:.9rem; }
</style>
</head>
<body>
${slides.map((s, i) => `<section class="slide${i === 0 ? " active" : ""}" data-i="${i}">${s}</section>`).join("\n")}
<div class="hud"><span id="n">1</span> / ${slides.length} · ← →</div>
<script>
const slides=[...document.querySelectorAll('.slide')];
let i=0;
function show(k){ i=(k+slides.length)%slides.length; slides.forEach((s,j)=>s.classList.toggle('active',j===i)); document.getElementById('n').textContent=i+1; }
addEventListener('keydown',e=>{ if(e.key==='ArrowRight'||e.key===' ') show(i+1); if(e.key==='ArrowLeft') show(i-1); });
addEventListener('click',()=>show(i+1));
</script>
</body>
</html>
`;
fs.writeFileSync(out, html);
console.log(`Wrote ${out} (${slides.length} slides)`);
