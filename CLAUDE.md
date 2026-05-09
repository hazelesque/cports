# Working on this cports tree

This is Hazel's fork of [chimera-linux/cports](https://github.com/chimera-linux/cports).
Hazelesque-specific packaging lives in `hazelesque/`; everything else mirrors
upstream and is rebased onto upstream `master` periodically.

The two upstream-authored references at the repo root are authoritative:

- `Packaging.md` — comprehensive template & API reference (~57 k tokens).
  Search it before guessing.
- `Usage.md` — `cbuild` command reference, sandbox model, bootstrap.

This file is the operator's manual for *agents* working on this tree —
the rakes that aren't in `Packaging.md` but bite anyway, the workflow
shortcuts, and the project-specific conventions Hazel cares about.

## Repo layout

```
cports/
├── main/         ← upstream main category (mirrored, rebased)
├── user/         ← upstream user category (mirrored, rebased)
├── contrib/     ← upstream contrib (mirrored)
├── hazelesque/   ← Hazel's personal category — new packaging goes here
├── packages/     ← local apk repo (built artefacts)
├── pkgstage/     ← staging area before promotion to packages/
├── bldroot/      ← the sandboxed build container (recreated by bootstrap-update)
├── sources/      ← downloaded tarball cache
├── cbuild_cache/ ← per-tool caches (apk, ccache, …)
├── etc/          ← config.ini, signing keys
├── src/cbuild/   ← the cbuild source code itself (Python)
├── Packaging.md
├── Usage.md
└── CLAUDE.md     ← you are here
```

A package is a directory under one of the category dirs containing:

```
hazelesque/foo/
├── template.py        ← required: build recipe
├── patches/*.patch    ← optional: applied alphabetically during patch phase
└── files/*            ← optional: referenced from template.py via self.files_path
```

## Quick command reference

Always run cbuild from the cports root:

```sh
cd /home/hazel/projects/chimera-cports/cports

./cbuild lint hazelesque/foo              # validate template (no build)
./cbuild fetch hazelesque/foo             # download sources only
./cbuild prepare-upgrade hazelesque/foo   # fetch + populate sha256 fields
./cbuild pkg hazelesque/foo               # full build → apk in packages/
./cbuild bootstrap-update                 # refresh bldroot from upstream apk
./cbuild bootstrap                        # recreate bldroot (after `zap`)
./cbuild zap                              # nuke bldroot
./cbuild chroot                           # interactive shell in bldroot

# Useful flags (combined with pkg):
#   -C   skip the check phase
#   -D   dirty-build (preserve builddir/destdir between runs)
#   -K   keep builddir on success
#   -f   force rebuild even if marker says done
```

`apk search` against the **host** uses Hazel's already-up-to-date cached
index — do *not* hit `--repository https://repo.chimera-linux.org/...
--no-cache`; it hammers the upstream repo and adds noise. If a search
needs refreshing, ask.

For git operations against this tree, use `git -C /home/hazel/projects/
chimera-cports/cports <subcmd>` rather than `cd && git`. Hazel can
bulk-approve `git -C` for read-only commands and `git add`; that
doesn't work with the `cd` chain.

## Template anatomy

A minimal template:

```python
pkgname = "foo"
pkgver = "1.2.3"
pkgrel = 0
build_style = "gnu_configure"
hostmakedepends = ["pkgconf"]      # tools used during build
makedepends = ["zlib-ng-compat-devel"]   # libs to link against
depends = []                              # runtime deps (auto-detected from
                                          #   shlibs in most cases)
pkgdesc = "Short description without trailing parens"   # ≤72 chars
license = "GPL-3.0-or-later"              # SPDX
url = "https://example.com/foo"
source = f"https://example.com/foo-{pkgver}.tar.gz"
sha256 = "0000…"                          # populate via prepare-upgrade
# Why check is disabled (lint requires this comment):
options = ["!check"]
```

### Field order

Lint enforces canonical ordering. The order roughly is:

1. `pkgname` / `pkgver` / `pkgrel`
2. `archs` / `build_style` / `configure_args` / `make_*_args`
3. `prepare_after_patch` (if needed)
4. `hostmakedepends` / `makedepends` / `checkdepends` / `depends` / `provides`
5. `pkgdesc` / `subdesc` / `maintainer` / `license` / `url`
6. `source` / `source_paths` / `sha256`
7. `options` / `hardening`

Fields after `options` (functions, etc.) come last. If lint says "X
should go after Y", swap them.

### Dependency lists must be sorted

Lint enforces alphabetical sorting within each list. Inline comments
between entries are OK but don't affect the sort.

### `pkgdesc` rules

- ≤72 characters.
- No trailing parenthesised "(subdescription)" — that's a separate
  `subdesc` field for subpackages.

### Why `!check` requires a comment

If `options = ["!check", ...]`, lint requires a comment line
*immediately above* the `options` line explaining why. Same for
`!cross`. Other `!`-flags don't require justification.

### Ruff format & check

Templates must pass `ruff format --check` and `ruff check`. cbuild
enforces both at the start of any `pkg` build. Just run `ruff format
hazelesque/foo/template.py` after edits and you'll be fine.

## Build phases & sandbox model

The full cbuild phase order:

```
fetch → extract → prepare → patch → setup → configure → build → check → install → pkg
```

If `prepare_after_patch = True`, the order becomes
`fetch → extract → patch → prepare → setup → ...`. Set this when
patches need to be in the source tree before your `prepare()`
function runs (e.g. when prepare() runs the actual build).

### Sandbox properties

- Each `self.do(...)` call is a fresh `bwrap` session.
- `/tmp`, `/var/tmp`, `/run` are tmpfs — wiped between sessions.
- `/builddir` (the source tree + cports working dir) is bind-mounted
  from outside; persistent across sessions.
- Network access is only allowed in `fetch` / `extract` / `prepare` /
  `patch` phases, and only when `self.do(..., allow_network=True)`.
- Network is **disabled in `build`**, `check`, `install`. If your
  build genuinely needs network (Coursier, bazel, Go module download),
  it must run in `prepare()` with `allow_network=True`.

### `bazel-bin/*`-style symlinks

If your tool produces symlinks pointing into a sandbox-internal path
(e.g. bazel's `bazel-bin → /builddir/.bazel-cache/...`), `install_file()`
runs *outside* the sandbox and can't follow them — the path naming
differs. Either:

- Copy the artifact to a workspace-relative path inside the sandbox
  during `prepare()` (`self.do("cp", "bazel-bin/foo", "foo")`), then
  `install_file("foo", ...)` works, or
- Use `--output_user_root=/builddir/.bazel-cache` so the output tree
  itself is on a path the host can see, and the symlink target works.

## Build styles

`build_style = "..."` picks a build automation:

- `gnu_configure` — autotools. Honors `configure_args`, `make_build_args`,
  `make_install_args`, `make_check_args`, `configure_gen` (default
  `["autoreconf", "-if", "-W", "none"]`).
- `cmake` — CMake (Ninja by default). `configure_args` forwards to
  `cmake -D...`; `make_build_target` switches to `--target` mode.
- `meson` — Meson + Ninja.
- `python_pep517` — `python -m build` then `python -m installer`.
  Requires `python-build`, `python-installer`, your build backend
  (`python-setuptools`, `python-flit-core`, etc.) in `hostmakedepends`.
- `go` — `go build` + `go install`. `make_build_args` is the package
  list (e.g. `["./cmd/foo"]`).
- `cargo` — Cargo with vendor-in-prepare/build-offline split.
- `makefile` — bare make.
- `meta` — empty package (metapackages).

For everything else: omit `build_style` and define `configure()` /
`build()` / `install()` directly.

## Idioms & gotchas

### Package names ≠ command names

- Use `python` (not `python3`) in deps.
- `chimerautils` provides `patch`, `which`, `ed`, etc.
- `pkgconf` is the pkg-config implementation.
- `gtk+3-devel` (with the `+`).

### `cmd:` virtual deps require `!provider`

`apk` exposes commands as virtual provides. Use `cmd:foo!providingpkg`:

```python
depends = [
    "cmd:bazel!bazel-7.4.0",   # NOT just "cmd:bazel" — lint will reject
]
```

Discover the provider with `apk query --match name,provides cmd:foo`.

### `gettext-devel` separately ships m4 macros

`gettext` alone lacks the autoconf macros (`AM_NLS`, `AM_GNU_GETTEXT`).
If `autoreconf` fails with "possibly undefined macro: AM_NLS", add
`gettext-devel` to `hostmakedepends`.

### `/usr/lib/locale` is forbidden

cports lints against `/usr/lib/locale` (legacy GNU autotools default).
Modern XDG places translations under `/usr/share/locale`. Old packages
may put .mo files in the wrong place via `aclocal.m4` macros that win
over `--localedir`; override at `make install` time:

```python
make_install_args = ["localedir=/usr/share/locale"]
```

### `/usr/share/pixmaps` lints with a warning

Lint prefers `/usr/share/icons/hicolor/<size>/apps/`. For one-off legacy
packages it's not worth migrating; suppress with `options += ["!lintpixmaps"]`
and a comment explaining why.

### Subpackages auto-split

cports automatically splits these from the destdir:

- `-doc` / `-man` — documentation
- `-locale` — translations
- `-bashcomp` / `-zshcomp` / `-fishcomp` — shell completions
- `-dbg` — debug symbols
- `-devel` — headers, .so symlinks, .pc files
- `-static` — static libs

You don't need to declare them unless you want to tweak metadata.

### Qt6 / Qt-plugin runtime deps

cports' shlib scanner can't see plugins loaded via `QPluginLoader`
(SVG, image formats, wayland integration). These must be explicit
runtime depends:

```python
depends = [
    "qt6-qtimageformats",   # PNG/JPEG/etc plugins
    "qt6-qtsvg",            # SVG icons in resource bundles
    "qt6-qtwayland",        # Wayland session integration
]
```

Symptom of forgetting: SVG icons render as plain solid-colour
fallbacks; tooltips still work because they're string lookups.

### Python: site-packages path

cports auto-populates `self.python_version` (e.g. `"3.13"`) when
`python` is in the build env (in `hostmakedepends` is enough). Use it
to construct paths:

```python
sp = f"usr/lib/python{self.python_version}/site-packages/foo"
self.install_file("foo.py", sp)
```

cports' `005_py_dep` hook then auto-rewrites `python` → `python3.13`
in the package's runtime depends, based on the destdir layout.

### Network on flaky connections

Mobile broadband, transient TLS errors during `bootstrap-update` or
the apk-update at the start of a build. Retry pattern:

```sh
for i in 1 2 3 4 5; do
  ./cbuild pkg hazelesque/foo > /tmp/foo-build.log 2>&1
  rc=$?
  if [ "$rc" = 0 ]; then echo "attempt $i: SUCCESS"; break; fi
  if grep -qE 'TLS: unspecified|DNS: transient|TLS connect error' /tmp/foo-build.log; then
    echo "attempt $i: network flake, retrying..."; sleep 5; continue
  fi
  echo "attempt $i: non-network failure, stopping"
  tail -10 /tmp/foo-build.log
  break
done
```

Differentiating network flake from real failure is mandatory — don't
just retry blindly.

## Patches

Patches live in `<category>/<pkgname>/patches/*.patch` and are applied
**alphabetically** during the patch phase. Naming conventions:

- `chimera-<short-description>.patch` for Chimera-specific fixes
  (musl, distro-specific).
- `<short-description>.patch` for upstream-applicable fixes you'd want
  to send back.
- `<NNNN-name>.patch` if order matters (rare).

### Patch format

`git diff` format with `--git a/path b/path` headers. A free-form
text preamble before the first `diff --git` is allowed and encouraged
for the *why*:

```
From: Hazel Smith <hazel@hazelesque.uk>
Subject: short summary

Multi-paragraph rationale explaining what the patch does, why it's
needed on Chimera specifically, and any cross-references (Alpine
APKBUILD, upstream PR, etc.).

diff --git a/foo b/foo
--- a/foo
+++ b/foo
@@ -10,7 +10,7 @@ context
 unchanged line
-old line
+new line
 unchanged line
```

### Hunk math must be exact

cports' patch tool runs with strict fuzz tolerance. If you craft a
patch by hand and the hunk header line numbers don't match exactly,
it fails. Easiest reliable approach: edit a copy of the file, then
`diff -u original.txt edited.txt` to generate the hunk headers.

For new files use:

```
diff --git a/path/to/new.file b/path/to/new.file
new file mode 100644
--- /dev/null
+++ b/path/to/new.file
@@ -0,0 +1,N @@
+content line 1
+content line 2
+...
```

where `N` matches the actual line count exactly (no padded spaces).

## Bazel notes

cports has no `bazel` build_style. The hazelesque tree builds bazel
itself (`bazel-7.4.0-bootstrap`, `bazel-7.4.0`) and downstream
bazel-driven packages (scip-clang, scip-lsp-bazel-generator) using
ad-hoc `prepare()`-as-build. Key constraints:

- bazel needs network → must run in `prepare()` with `allow_network=True`.
- Default bazel output ($HOME/.cache/bazel) lands in `/tmp` (tmpfs,
  wiped between sessions). Pass
  `--output_user_root=/builddir/.bazel-cache` so the output tree
  persists; the `bazel-bin/*` symlinks then resolve from outside the
  sandbox.
- bazel's nested `linux-sandbox` can't `mount /sys` inside cports'
  bwrap → pass `--spawn_strategy=local`. cports' bwrap is the only
  sandbox needed.
- For musl: `--copt=-D_GNU_SOURCE -D_LARGEFILE64_SOURCE` (and matching
  `--host_copt=` for exec-config compiles).
- For vendored LLVM on musl: `--copt=-UHAVE_BACKTRACE -UHAVE_MALLINFO`
  (and matching `--host_copt=`).
- For prebuilt-JDK avoidance: `--java_runtime_version=local_jdk
  --tool_java_runtime_version=local_jdk`, plus a
  `non_prebuilt_java_21_toolchain` patched into the workspace and
  registered via `common --extra_toolchains=...` in `.bazelrc`.
- For embedded version label: pass **both** `--stamp` and
  `--embed_label=...`. `--embed_label` alone is silently ignored;
  the resulting `bazel --version` reads `no_version` and downstream
  rules sets that key off `bazel_features` then explode on missing
  Starlark globals.

The four hazelesque/bazel-7.4.0 patches (musl-unix-jni,
musl-singlejar-port, module-bazel-bcr-versions,
chimera-java-toolchain) are the canonical example of what's needed
to get bazel to compile against musl. Mirror them on any new bazel
package.

## What NOT to do

- **Don't slap a binary blob into a package.** cports is a
  source-built distribution. Self-bootstrapping launchers shipped in
  upstream tarballs (e.g. scip-java's `bin/coursier`, gradle's
  `gradlew`) are OK — they're build infrastructure that came with the
  source. A standalone binary download from a GitHub release is not.
  If you find yourself reaching for "just install the prebuilt jar",
  stop and figure out the source build.

- **Don't manually patch builddir state to make a single run succeed.**
  If `install()` can't find a file because `prepare()` didn't put it
  there, fix the template and rebuild — even if that means re-running
  a long compile. Bazel/Go/sbt incremental caches make warm rebuilds
  fast. A working build that exists only because of a manual `cp` is
  not reproducible packaging.

- **Don't claim "compiles clean" without running the build.** The
  cbuild output is the truth; lint passing is necessary but not
  sufficient.

- **Don't `git add -A` or `git add .`** — the cports root has
  untracked working files (review notes, KEEP_ZPAGES captures, ad-hoc
  experiments). Always stage explicit paths.

- **Don't spray /tmp** — when extracting tarballs for inspection,
  `mkdir -p /tmp/<context>-extract && tar -C /tmp/<context>-extract
  -xzf ...`. Don't spread into the bare `/tmp/...` namespace; it's
  shared with Hazel's other work.

## Common error → fix index

| Symptom | Likely cause | Fix |
|---|---|---|
| `ERROR: dependency list 'X' is not sorted` | Manual sort drift | Alphabetise the list |
| `'Y' should go after 'X'` | Field-order violation | Swap them |
| `pkgdesc should not contain a (subdescription)` | Trailing parens in desc | Move detail to comment or `subdesc` |
| `lint failed: check disabled but no reason given` | `!check` without comment | Add a comment immediately above `options =` |
| `template is incorrectly formatted` | ruff format violation | `ruff format hazelesque/foo/template.py` |
| `failed to apply 'X.patch'` | Hunk math wrong / header malformed | Regenerate via `diff -u` against an edited copy |
| `forbidden path '/usr/lib/locale'` | Old gettext default | `make_install_args = ["localedir=/usr/share/locale"]` |
| `'/usr/share/pixmaps' exists, '/usr/share/icons' is preferred` | Legacy XDG | `options += ["!lintpixmaps"]` (with reason comment) |
| `unknown variable: python_version` | Set as top-level (it's auto-populated, read-only) | Drop the assignment, just use `self.python_version` in hooks |
| `bad python version (3.X)` | destdir Python version mismatches build-env Python | Build-env Python must match installed `python` package |
| `'cmd:X' has no specified provider` | Bare `cmd:X` virtual dep | Use `cmd:X!pkgname` form |
| `Cannot run program "...protoc-linux-x86_64-N.N.N"` | sbt-protoc downloaded glibc-linked protoc | Patch in a project-scope `PB.protocExecutable` autoplugin pointing at `/usr/bin/protoc`; add `protobuf-protoc` to hostmakedepends |
| `linux-sandbox-pid1.cc: "mount /sys": Operation not permitted` | bazel nested sandbox inside bwrap | `--spawn_strategy=local` |
| `Cannot run program ".../bin/javac"` (after Coursier fetch) | glibc-linked JDK on musl | Patch JavaToolchainPlugin + add chimera-java-toolchain target + use `--java_runtime_version=local_jdk` |
| `'execinfo.h' file not found` | musl has no libexecinfo | Either `__has_include`-guard the include, or use `-UHAVE_BACKTRACE` for vendored LLVM |
| `bazel --version` reads `no_version` | `--embed_label` without `--stamp` | Pass both |
| `WARNING: ...: TLS: unspecified error` during apk-update | Flaky network | Retry loop (see Network section) |

## Workflow norms

- **Commits**: explicit paths in `git add`, no `-A` / `.`. One logical
  unit per commit. Commit messages: ≤72 char title, free-form body
  with the *why*, end with `Co-Authored-By:` trailer.
- **WIP commits**: legitimate when batching mid-flight work across a
  rebase. Mark them as `WIP: ...` in the title; amend / split after
  the dust settles.
- **Rebases**: this fork rebases on `upstream/master` (`git fetch
  upstream && git rebase upstream/master`). Hazelesque commits should
  rebase cleanly because they're scoped to `hazelesque/`.
- **Stale `pkgrel`**: after upstream master moves, the bldroot might
  hold packages that don't match cports' tree pin (e.g. local llvm
  pinned at 22.1.3 but upstream apk has 22.1.4 only). Symptom:
  unexpected from-source rebuild of huge dep chains (LLVM, mesa, glib).
  Fix by `git fetch upstream && git rebase upstream/master && ./cbuild
  bootstrap-update`.

## When in doubt

1. **Read the relevant section of `Packaging.md`** — it's the
   authoritative reference. Use offset/limit on `Read` to navigate.
2. **Look for a similar package** — `grep -lE '"qt6-qtbase-devel"'
   main/*/template.py` finds prior art for any pattern.
3. **Check Alpine's APKBUILDs** for the same package — Alpine is
   musl-based too, so its workarounds often apply directly. URL
   pattern: `https://gitlab.alpinelinux.org/alpine/aports/-/raw/master/<repo>/<pkg>/APKBUILD`.
4. **Run `cbuild lint` first**, then `prepare-upgrade`, then `pkg`.
   Don't skip steps.
