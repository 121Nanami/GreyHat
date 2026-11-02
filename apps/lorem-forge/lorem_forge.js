#!/usr/bin/env node
/** Themed lorem generator for docs / PKGBUILD comments / UI fixtures. */
const themes = {
  classic: "lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor incididunt ut labore et dolore magna aliqua".split(" "),
  spin: "mirror checksum sysctl hardening firewall profile wallpaper pack first boot journalctl pacman keyring overlayfs squashfs grub cmdline".split(" "),
  ellen: "abyss harbor neon tide sonar grit chrome rain dock sodium grit blade reef dusk signal".split(" "),
};
const args = process.argv.slice(2);
let theme = "classic", n = 40;
for (let i = 0; i < args.length; i++) {
  if (args[i] === "--theme") theme = args[++i];
  else if (args[i] === "-n") n = parseInt(args[++i], 10);
  else if (args[i] === "-h" || args[i] === "--help") {
    console.log("Usage: lorem_forge.js [-n words] [--theme classic|spin|ellen]");
    process.exit(0);
  }
}
const bed = themes[theme];
if (!bed) {
  console.error("unknown theme", theme);
  process.exit(2);
}
const out = [];
for (let i = 0; i < n; i++) out.push(bed[i % bed.length]);
let s = out.join(" ");
s = s.charAt(0).toUpperCase() + s.slice(1) + ".";
console.log(s);
