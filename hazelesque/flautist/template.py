pkgname = "flautist"
pkgver = "0.0.3_pre1"
pkgrel = 0
# Sources are the scm-infra monorepo tarball — shared with
# the `withy` cports package.  See that template + the
# refresh-hazelesque-source.sh helper for the source-pulling
# story.
build_wrksrc = "flautist"  # cargo runs in flautist-VER/flautist/
# (cports' extract hook auto-renames the tarball's single
#  top-level dir — `scm-infra-VER/` — to `{pkgname}-{pkgver}/`,
#  so the post-extract path is `flautist-VER/flautist/`, not
#  `scm-infra-VER/flautist/`.)
build_style = "cargo"
# Post-#218-binary-split layout: the old multi-call `f7` binary
# was split into per-daemon binaries so server-side changes don't
# trigger CLI LTO rebuilds.  The flautist workspace now produces:
#
#   f7            flautist-cli           operator CLI; `f7 serve`
#                                        et al exec-passthrough to
#                                        the per-daemon binaries
#   f7repod       flautist-server        central repo server
#   f7nfsd        flautist-daemon        workspace NFS daemon
#   f7webd        flautist-codebrowser   read-only web UI
#   f7xrefd       flautist-xref-daemon   SCIP xref indexer daemon
#   f7cid         flautist-ci-daemon     CI run executor
#   f7buildd      flautist-build-daemon  build-artifact daemon
#   scip-f7-bazel flautist-scip-bazel    SCIP indexer wrapper
#
# `f7 serve` literally execs /usr/bin/f7repod, so the dinit
# services break unless the per-daemon binaries install alongside
# the CLI.  f7-agent moved OUT of this workspace — it now builds
# from the sibling `hazelesque-common` workspace (crate
# `hazelesque-agent`); see the build() override below.
make_build_args = [
    "-p",
    "flautist-cli",
    "-p",
    "flautist-server",
    "-p",
    "flautist-daemon",
    "-p",
    "flautist-codebrowser",
    "-p",
    "flautist-xref-daemon",
    "-p",
    "flautist-ci-daemon",
    "-p",
    "flautist-build-daemon",
    "-p",
    "flautist-scip-bazel",
]
make_install_args = list(make_build_args)
hostmakedepends = [
    "cargo-auditable",
    "protobuf-protoc",  # flautist-proto's build.rs invokes prost-build → protoc.
]
makedepends = [
    # Needed at lint-time so cports can resolve `svc:local.target`
    # (and any other dinit-provided svc:* refs) in the dinit
    # subpackages' service files — not a build-time link dep.
    "dinit-chimera",
    "musl-mimalloc-introspectable",
    "rust-std",
    "sqlite-devel",  # rusqlite links against -lsqlite3 (system lib, not vendored)
]
depends = [
    # flautist-cli's `mallocz` feature (default-enabled) links
    # against /usr/lib/musl-mimalloc-introspectable/lib at run
    # time — so the variant-libc has to be present on target.
    "musl-mimalloc-introspectable",
    # rusqlite is linked dynamically against libsqlite3.so; the
    # runtime `sqlite` package ships the .so.
    "sqlite",
]
pkgdesc = "Source-control-aware code review backend"
license = "custom:hazelesque"
url = "https://github.com/hazelesque/scm-infra"
# PLACEHOLDER — same monorepo source as the `withy` package.
# Operator runs `refresh-hazelesque-source.sh v{pkgver}` (one
# level up from the cports tree) to git-clone + tar + drop
# the archive in `sources/{pkgname}-{pkgver}/`.  The URL
# below is a "where this would be if scm-infra were public"
# placeholder; cbuild falls back to it only on cache miss.
source = f"https://github.com/hazelesque/scm-infra/archive/refs/tags/v{pkgver}.tar.gz>scm-infra-{pkgver}.tar.gz"
sha256 = "e72381e97b6c6f33ec29badf0c38db832124bf37218aa3bde230249627e2bc43"
# hazelesque-service-mgmt's /tokioz page calls tokio runtime-metrics
# methods (spawned_tasks_count, worker_local_queue_depth, etc.) that
# are gated behind `--cfg=tokio_unstable`.  The same flag is set in
# the source tree's `.cargo/config.toml` files for dev.sh, but cports
# exports RUSTFLAGS as an env var — and the env var wins over
# `[build] rustflags` in config.toml (cargo picks one, no merge).
# So we have to lift the cfg here too.
tool_flags = {"RUSTFLAGS": ["--cfg=tokio_unstable"]}
# !check: workspace tests need the full dev.sh stack (server, daemon,
#         agent, NFS mount, dev CA, ...) wired up — not a packaging-time job.
# !cross: rust-std cross builds haven't been validated for the flautist
#         workspace; defer until aarch64 demand actually appears.
# !distlicense: license install handled explicitly in post_install.
options = ["!check", "!cross", "!distlicense"]


def prepare(self):
    # cports' default cargo build_style runs `cargo vendor` from
    # `tmpl.cwd`, which during the prepare phase is reset to
    # `srcdir` (not `srcdir/build_wrksrc`).  Our Cargo.toml lives
    # at `srcdir/flautist/Cargo.toml` — pass `build_wrksrc`
    # explicitly so vendor descends into the right workspace.
    # See `user/gopls/template.py` for the same pattern for go.
    self.cargo.vendor(wrksrc=build_wrksrc)
    # Second workspace: `hazelesque-common` produces f7-agent
    # (crate `hazelesque-agent`).  Separate Cargo workspace =
    # separate Cargo.lock = separate vendor pass; each vendor()
    # writes its own .cargo/config.toml next to its workspace
    # root, so the two builds resolve their own vendored trees.
    self.cargo.vendor(wrksrc="hazelesque-common")


def build(self):
    # Default workspace build (flautist; cwd is already
    # srcdir/build_wrksrc here, and make_build_args carries the
    # per-daemon -p list).
    self.cargo.build()
    # f7-agent from the sibling workspace.  Use invoke() rather
    # than build() so make_build_args (flautist crate names)
    # doesn't leak into the hazelesque-common invocation.
    # `--offline` comes from invoke()'s offline default; the
    # vendor pass in prepare() makes that resolvable.  PIV
    # transport stays feature-gated OFF (default features) —
    # the demo instance doesn't need hardware-token signing and
    # enabling it would drag in pcsc-lite at build + runtime.
    self.cargo.invoke(
        "build",
        args=["--release", "-p", "hazelesque-agent"],
        wrksrc="../hazelesque-common",
    )


def install(self):
    # Override the default cargo build_style install.  That one runs
    # `cargo install --path . --no-track $make_install_args`, and we
    # have `-p crate1 -p crate2 ...` in make_install_args (the
    # `-p` flags are valid for `cargo build` but NOT `cargo install`,
    # which insists on a single package via --path / --bin selectors).
    # The workspaces are already built; just copy the binaries out.
    triplet = self.profile().triplet
    release = f"target/{triplet}/release"
    for binary in (
        "f7",
        "f7repod",
        "f7nfsd",
        "f7webd",
        "f7xrefd",
        "f7cid",
        "f7buildd",
        "scip-f7-bazel",
    ):
        self.install_bin(f"{release}/{binary}")
    # f7-agent built in the sibling workspace's own target dir
    # (no shared target-dir override in the committed
    # .cargo/config.toml files — the dev tree's shared root
    # target/ comes from dev.sh env, not config).
    self.install_bin(f"../hazelesque-common/{release}/f7-agent")


def post_install(self):
    # LICENSE shipped via cports' files/ for now — scm-infra
    # doesn't yet have a top-level LICENSE.  Will switch to the
    # in-tree one once a release adds it, at which point this
    # line becomes `self.install_license("LICENSE")`.
    self.install_license(self.files_path / "LICENSE")

    # Shared bwrap wrapper — both demo + staging dinit
    # subpackages reference it.  Stays in the main package
    # so the binaries + sandbox launcher install together.
    self.install_file(
        self.files_path / "wrap-bwrap.sh",
        "usr/libexec/flautist",
        mode=0o755,
    )

    # Reference auth-acl.toml the operator copies into a
    # per-instance etc dir + edits.  Stays in /usr/share so
    # `apk fix flautist` doesn't clobber operator edits in
    # /etc/ or /srv/.
    self.install_file(
        self.files_path / "auth-acl.toml.example",
        "usr/share/flautist",
    )

    for inst in ("demo", "staging"):
        self.install_service(self.files_path / f"flautist-{inst}-server")
        self.install_sysusers(
            self.files_path / f"flautist-{inst}-sysusers.conf",
            name=f"flautist-{inst}",
        )
        self.install_tmpfiles(
            self.files_path / f"flautist-{inst}-tmpfiles.conf",
            name=f"flautist-{inst}",
        )


@subpackage("flautist-demo-dinit")
def _(self):
    self.subdesc = "dinit service + bwrap sandbox (demo instance)"
    self.pkgdesc = "Flautist demo-instance dinit + bwrap sandbox"
    self.depends = [
        f"{pkgname}={pkgver}-r{pkgrel}",
        "bubblewrap",
        "dinit-chimera",
    ]
    self.install_if = [f"{pkgname}={pkgver}-r{pkgrel}", "dinit-chimera"]
    # TODO(extra services): only `f7 serve` is brought up here.
    # When/if the operator wants `f7 daemon` (mTLS submission
    # proxy), `f7 codebrowser` (web UI), `f7-agent`, or
    # `xref-daemon` running per instance, add the matching
    # files + extend this glob list.  The codebrowser + daemon
    # bring in extra port + NFS-mount considerations not
    # covered tonight.
    return [
        "usr/lib/dinit.d/flautist-demo-server",
        "usr/lib/sysusers.d/flautist-demo.conf",
        "usr/lib/tmpfiles.d/flautist-demo.conf",
    ]


@subpackage("flautist-staging-dinit")
def _(self):
    self.subdesc = "dinit service + bwrap sandbox (staging instance)"
    self.pkgdesc = "Flautist staging-instance dinit + bwrap sandbox"
    self.depends = [
        f"{pkgname}={pkgver}-r{pkgrel}",
        "bubblewrap",
        "dinit-chimera",
    ]
    self.install_if = [f"{pkgname}={pkgver}-r{pkgrel}", "dinit-chimera"]
    return [
        "usr/lib/dinit.d/flautist-staging-server",
        "usr/lib/sysusers.d/flautist-staging.conf",
        "usr/lib/tmpfiles.d/flautist-staging.conf",
    ]
