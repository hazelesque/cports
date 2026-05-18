pkgname = "withy"
pkgver = "0.0.1_pre1"
pkgrel = 0
# Sources are the whole scm-infra monorepo tarball — withy
# (and flautist) live as sibling workspaces under it, with
# Cargo.toml path-deps crossing the boundary
# (e.g. `../hazelesque-common/...`, `../zpages/...`).  Both
# the `withy` and `flautist` cports packages reference the
# same tarball; cports dedupes via `sources/by_sha256/`.
build_wrksrc = "withy"  # cargo runs in withy-VER/withy/
# (cports' extract hook auto-renames the tarball's single
#  top-level dir — `scm-infra-VER/` — to `{pkgname}-{pkgver}/`,
#  so the post-extract path is `withy-VER/withy/`, not
#  `scm-infra-VER/withy/`.)
build_style = "cargo"
# Workspace has many crates; only `wy` (from withy-cli) is the
# install target.  cports' cargo style installs all bins by
# default but we restrict to wy explicitly so we don't ship
# stray test binaries or future dev-only CLIs.
make_build_args = ["-p", "withy-cli"]
make_install_args = ["-p", "withy-cli"]
hostmakedepends = [
    "cargo-auditable",
    "protobuf-protoc",  # withy-proto's build.rs invokes prost-build → protoc.
]
makedepends = [
    # Needed at lint-time so cports can resolve `svc:local.target`
    # (and any other dinit-provided svc:* refs) in the dinit
    # subpackages' service files — not a build-time link dep.
    "dinit-chimera",
    "rust-std",
    "sqlite-devel",  # rusqlite (withy-store) links against -lsqlite3
]
depends = [
    # rusqlite is linked dynamically against libsqlite3.so; the
    # runtime `sqlite` package ships the .so.
    "sqlite",
]
# TODO(mallocz parity): withy-cli does NOT currently wire up
# `flautist-mimalloc` + the `mallocz` feature flag the way
# flautist-cli does, so the /mallocz zpage on withy is inert.
# When we close that gap (add mallocz feature to withy-cli +
# build.rs that emits the variant-libc rustflags on Chimera),
# add `musl-mimalloc-introspectable` to both makedepends +
# depends, AND pass `--features mallocz` via make_build_args.
pkgdesc = "Homelab Trello-shaped board tracker"
license = "custom:hazelesque"
url = "https://github.com/hazelesque/scm-infra"
# PLACEHOLDER — cports' fetcher is HTTP/HTTPS-only and the
# scm-infra monorepo is private.  Operator runs
# `refresh-hazelesque-source.sh v{pkgver}` (one level up from
# the cports tree) to git-clone + tar + drop the archive into
# `sources/{pkgname}-{pkgver}/` so cbuild's fetcher sees it
# pre-cached.  The URL below is the "where this would come
# from if the monorepo were public" placeholder; cbuild only
# falls back to it on cache miss.
source = f"https://github.com/hazelesque/scm-infra/archive/refs/tags/v{pkgver}.tar.gz>scm-infra-{pkgver}.tar.gz"
sha256 = "8ae13ec5e5e1c231ce7929a185a83b60a834116b95e68b0314801d1346aaf1d7"
# hazelesque-service-mgmt's /tokioz page calls tokio runtime-metrics
# methods (spawned_tasks_count, worker_local_queue_depth, etc.) that
# are gated behind `--cfg=tokio_unstable`.  The same flag is set in
# the source tree's `.cargo/config.toml` files for dev.sh, but cports
# exports RUSTFLAGS as an env var — and the env var wins over
# `[build] rustflags` in config.toml (cargo picks one, no merge).
# So we have to lift the cfg here too.
tool_flags = {"RUSTFLAGS": ["--cfg=tokio_unstable"]}
# !check: workspace tests need the full dev.sh stack (flautist,
#         withy-server, dev CA, ...) wired up — not a packaging-time job.
# !cross: rust-std cross builds are doable but haven't been validated
#         against the withy workspace's mix of native + protoc-bound deps.
# !distlicense: license install handled explicitly in post_install.
options = ["!check", "!cross", "!distlicense"]


def prepare(self):
    # cports' default cargo build_style runs `cargo vendor` from
    # `tmpl.cwd`, which during the prepare phase is reset to
    # `srcdir` (not `srcdir/build_wrksrc`).  Our Cargo.toml lives
    # at `srcdir/withy/Cargo.toml` — pass `build_wrksrc`
    # explicitly so vendor descends into the right workspace.
    # See `user/gopls/template.py` for the same pattern for go.
    self.cargo.vendor(wrksrc=build_wrksrc)


def install(self):
    # Override the default cargo install (it doesn't accept the
    # `-p` selector we use in make_build_args).  Workspace is
    # already built — just copy the binary out.  See flautist
    # template for the longer rationale.
    triplet = self.profile().triplet
    self.install_bin(f"target/{triplet}/release/wy")


def post_install(self):
    # LICENSE shipped via cports' files/ for now — scm-infra
    # doesn't yet have a top-level LICENSE.  Will switch to the
    # in-tree one once a release adds it, at which point this
    # line becomes `self.install_license("LICENSE")`.
    self.install_license(self.files_path / "LICENSE")

    # Shared bwrap wrapper — referenced by both demo + staging
    # dinit subpackages.  Stays in the main package so the bare
    # binary + sandbox launcher install together (operator
    # picks instance flavour by also installing one of the
    # *-dinit subpackages).
    self.install_file(
        self.files_path / "wrap-bwrap.sh",
        "usr/libexec/withy",
        mode=0o755,
    )

    # Stage all the dinit / sysusers / tmpfiles files into the
    # main install tree.  The @subpackage decorators below
    # claim the demo-* / staging-* slices respectively.
    for inst in ("demo", "staging"):
        for role in ("server", "web"):
            self.install_service(self.files_path / f"withy-{inst}-{role}")
        self.install_sysusers(
            self.files_path / f"withy-{inst}-sysusers.conf",
            name=f"withy-{inst}",
        )
        self.install_tmpfiles(
            self.files_path / f"withy-{inst}-tmpfiles.conf",
            name=f"withy-{inst}",
        )


@subpackage("withy-demo-dinit")
def _(self):
    self.subdesc = "dinit service + bwrap sandbox (demo instance)"
    self.pkgdesc = "Withy demo-instance dinit + bwrap sandbox"
    self.depends = [
        f"{pkgname}={pkgver}-r{pkgrel}",
        "bubblewrap",
        "dinit-chimera",
    ]
    # Auto-installed when the operator has both the parent
    # AND dinit-chimera — i.e. on a Chimera host running
    # dinit.  Not a hard dep of the parent so the bare binary
    # is install-able for ad-hoc CLI use (`wy login`, etc.)
    # without dragging in the service tree.
    self.install_if = [f"{pkgname}={pkgver}-r{pkgrel}", "dinit-chimera"]
    return [
        "usr/lib/dinit.d/withy-demo-server",
        "usr/lib/dinit.d/withy-demo-web",
        "usr/lib/sysusers.d/withy-demo.conf",
        "usr/lib/tmpfiles.d/withy-demo.conf",
    ]


@subpackage("withy-staging-dinit")
def _(self):
    self.subdesc = "dinit service + bwrap sandbox (staging instance)"
    self.pkgdesc = "Withy staging-instance dinit + bwrap sandbox"
    self.depends = [
        f"{pkgname}={pkgver}-r{pkgrel}",
        "bubblewrap",
        "dinit-chimera",
    ]
    self.install_if = [f"{pkgname}={pkgver}-r{pkgrel}", "dinit-chimera"]
    return [
        "usr/lib/dinit.d/withy-staging-server",
        "usr/lib/dinit.d/withy-staging-web",
        "usr/lib/sysusers.d/withy-staging.conf",
        "usr/lib/tmpfiles.d/withy-staging.conf",
    ]
