# Submit instructions — urlguard → BlackArch

Do **not** open a PR from this agent environment unless you have push access to a fork you control. Prepare locally, then submit from your GitHub account.

## Prerequisites

1. Publish `urlguard` to a public GitHub repo you own (MIT), tag `v0.1.0`.
2. Update `packages/urlguard/PKGBUILD`:
   - set `url='https://github.com/<you>/urlguard'`
   - replace `sha512sums=('SKIP')` with a real checksum of the release tarball
3. Read:
   - https://github.com/BlackArch/blackarch/blob/master/docs/HOWTO-DEV.md
   - https://github.com/BlackArch/blackarch-pkgbuilds (use style; this simple single-file tool follows the hashcheck-style layout more than the venv standalone template)
   - Tool-request rules: no wrappers, no abandoned tools, no illegal tooling

## Local validation (on Arch/BlackArch)

```bash
# from the upstream repo
python urlguard.py -V
python -m unittest test_urlguard.py

# package build in a clean chroot (preferred by BA maintainers)
# https://wiki.archlinux.org/title/DeveloperWiki:Building_in_a_clean_chroot
extra-x86_64-build   # or makechrootpkg in a configured chroot

# smoke test
pacman -U urlguard-*-any.pkg.tar.zst
urlguard 'https://example.com'
urlguard 'https://user:pass@203.0.113.10/login'
```

## Open the BlackArch PR

```bash
# fork https://github.com/BlackArch/blackarch on GitHub, then:
git clone git@github.com:<you>/blackarch.git
cd blackarch
git checkout -b urlguard-add

mkdir -p packages/urlguard
cp /path/to/contribution/packages/urlguard/PKGBUILD packages/urlguard/

# required by HOWTO-DEV
echo urlguard >> lists/to-release

git add packages/urlguard lists/to-release
git commit -m 'urlguard: add consumer URL safety checker'
git push -u origin urlguard-add
```

Open a PR against `BlackArch/blackarch` with title:

`urlguard: add consumer URL safety checker`

PR body should state:

- Defensive / consumer protection only (offline heuristics)
- Groups: `blackarch-defensive`, `blackarch-misc`
- Built & installed in clean chroot
- Upstream URL + license (MIT)
- Optional: mention Matrix `#BlackArch:matrix.org` if you want review chatter

## Optional pre-PR: tool request issue

If you want maintainer signaling first, open a `type::tool-request` issue using their template, then link the PKGBUILD PR (maintainers prefer PRs over requests alone).

## Faster trust ladder (parallel)

While waiting on `urlguard` upstream polish:

1. Fix an outdated/broken package PKGBUILD (noraj’s suggested starter).
2. Small docs/typo PR to `BlackArch/blackarch-guide` or `blackarch-site`.
3. Triage open `type::tool-request` issues — comment with packaging feasibility notes.
