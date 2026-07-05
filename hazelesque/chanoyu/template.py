pkgname = "chanoyu"
pkgver = "0.0.4_pre1"
pkgrel = 0
# Same monorepo-tarball arrangement as hazelesque/withy and
# hazelesque/flautist — chanoyu is a sibling Cargo workspace under
# scm-infra with path-deps crossing the boundary
# (../hazelesque-common/...).  This first package predates a
# pushed v0.0.4_pre1 tag: the cached tarball is a LOCAL
# `git archive` of main@91c2c83 (D42 — attested rehearsal gate),
# staged by hand into sources/chanoyu-0.0.4_pre1/.  When the tag
# lands on the remote, refresh-hazelesque-source.sh reproduces it.
build_wrksrc = "chanoyu"
build_style = "cargo"
# Ship the ceremony CLI plus the chanoyu-schsm hardware bins: the
# probe (read-only status) and the selftest (DESTRUCTIVE card
# acceptance — wanted on the ceremony host, guarded by its own
# --yes-wipe-card flag).
make_build_args = ["-p", "chanoyu-cli", "-p", "chanoyu-schsm"]
make_install_args = ["-p", "chanoyu-cli", "-p", "chanoyu-schsm"]
hostmakedepends = [
    "cargo-auditable",
    # pcsc-sys' build.rs locates libpcsclite via pkg-config.
    "pkgconf",
]
makedepends = [
    # Lint-time resolution of svc:* refs in the dinit subpackage's
    # service files (same as withy).
    "dinit-chimera",
    # hazelesque-piv's PC/SC transport → the pcsc crate links
    # libpcsclite.  Native APDU is the whole point (DESIGN D1: no
    # OpenSC, no PKCS#11 at runtime).
    "pcsc-lite-devel",
    "rust-std",
    # hazelesque-auth's audit log is rusqlite-backed → -lsqlite3
    # (same as withy).
    "sqlite-devel",
]
depends = [
    # libpcsclite.so.1 lives in pcsc-lite proper on Chimera (no
    # -libs split), and card access needs the running pcscd from
    # the same package anyway.  The CCID reader driver is a
    # deliberate NON-dep: which driver a host needs is a hardware
    # fact — the ceremony-host image recipe adds ccid explicitly.
    "pcsc-lite",
    "sqlite",
]
pkgdesc = "TLS CA ceremony automation for the hazelesque PKI"
license = "custom:hazelesque"
url = "https://github.com/hazelesque/scm-infra"
# PLACEHOLDER — private repo; see the tarball note above and
# refresh-hazelesque-source.sh one level above the cports tree.
source = f"https://github.com/hazelesque/scm-infra/archive/refs/tags/v{pkgver}.tar.gz>scm-infra-{pkgver}.tar.gz"
sha256 = "100619f7809e154c51cb34e0e6cdaa20546d3f2150500ebca3ecb3e1346d9f69"
# !check: chanoyu's tests run in the source tree (cargo test) and
#         the smoke needs openssl/step on PATH — not a
#         packaging-time job.
# !cross: not yet validated for this workspace.
# !distlicense: license installed explicitly (monorepo has no
#         top-level LICENSE yet; same interim as withy).
options = ["!check", "!cross", "!distlicense"]


def prepare(self):
    # Vendor from the workspace subdir — see withy/flautist
    # templates for the build_wrksrc rationale.
    self.cargo.vendor(wrksrc=build_wrksrc)


def install(self):
    # Workspace already built; copy the selected bins (the default
    # cargo install doesn't take our -p selectors).
    triplet = self.profile().triplet
    self.install_bin(f"target/{triplet}/release/chanoyu")
    self.install_bin(f"target/{triplet}/release/chanoyu-schsm-probe")
    self.install_bin(f"target/{triplet}/release/chanoyu-schsm-selftest")

    # Operator tooling from deploy/bin.  step-renew-daemon goes to
    # the exact path the dinit AND SMF service files exec
    # (/usr/libexec/step-renew-daemon); the monitoring trio +
    # trust-store package builder live under /usr/libexec/chanoyu.
    self.install_file("deploy/bin/step-renew-daemon", "usr/libexec", mode=0o755)
    for tool in (
        "chanoyu-verify-cron",
        "chanoyu-alert-watch",
        "chanoyu-soak-eval",
    ):
        self.install_file(
            f"deploy/bin/{tool}", "usr/libexec/chanoyu", mode=0o755
        )
    self.install_file(
        "deploy/apk/mkcaroot-apk.sh", "usr/libexec/chanoyu", mode=0o755
    )

    # dinit service files for the issuing tier (claimed by the
    # subpackage below).
    for svc in ("step-ca", "step-renew"):
        self.install_service(f"deploy/dinit.d/{svc}")


def post_install(self):
    self.install_license(self.files_path / "LICENSE")


@subpackage("chanoyu-issuing-dinit")
def _(self):
    self.subdesc = "issuing-tier dinit services (step-ca + step-renew)"
    self.pkgdesc = "Chanoyu issuing-host dinit services"
    self.depends = [
        f"{pkgname}={pkgver}-r{pkgrel}",
        "dinit-chimera",
        "step-ca",
        "step-cli",
    ]
    # NOT install_if-auto: an issuing host is a deliberate role,
    # not something every chanoyu install should sprout.
    return [
        "usr/lib/dinit.d/step-ca",
        "usr/lib/dinit.d/step-renew",
        "usr/libexec/step-renew-daemon",
    ]
