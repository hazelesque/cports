pkgname = "pkg6depotd"
pkgver = "0.5.3_pre2"
pkgrel = 0
build_style = "cargo"
# Workspace root; the depot is one member.  pkg6recv/pkg6repo are
# deliberately NOT built: pkg6recv re-hashes payloads to SHA-256
# and re-compresses, which 404s classic clients fetching
# file/1/<sha1> — the mirror PULL side stays pkg5 pkgrecv (see
# scm-infra/kajiya/spikes/pkg-depot-investigation.md for the
# verified end-to-end pairing).
make_build_args = ["-p", "pkg6depotd"]
make_install_args = list(make_build_args)
hostmakedepends = [
    "cargo-auditable",
    "cmake",  # aws-lc-sys (rustls via jsonwebtoken/axum-server)
    "pkgconf",  # zstd-sys probes libzstd via pkg-config
]
makedepends = [
    "dinit-chimera",  # lint-time svc resolution for the service file
    # openssl-sys: cports forces OPENSSL_NO_VENDOR=1 (system
    # lib; Chimera packages OpenSSL 3 as openssl3-*).
    "openssl3-devel",
    "rust-std",
    # rusqlite links the system libsqlite3 (cports forces
    # LIBSQLITE3_SYS_USE_PKG_CONFIG=1).
    "sqlite-devel",
    # zstd-sys: cports' cargo env forces ZSTD_SYS_USE_PKG_CONFIG=1
    # (system lib, not the vendored C build).
    "zstd-devel",
]
depends = []
pkgdesc = "IPS (pkg5-protocol) package depot server, Rust implementation"
license = "MPL-2.0"
url = "https://github.com/OpenFlowLabs/ips"
# PLACEHOLDER source URL — upstream has no release tags yet; the
# tarball is cut from Hazel's local clone (d7f49ac:
# +LISTEN_FDS socket activation) via
# git archive and pre-seeded into sources/ (same local-tarball
# convention as the scm-infra monorepo packages).
source = f"{url}/archive/refs/tags/v{pkgver}.tar.gz>pkg6depotd-{pkgver}.tar.gz"
sha256 = "7e73fcaa41f960e87128d2673e737fd729babdda21e0857a09b7e387489fff25"
# !check: workspace tests want network + fixture repos.
# !cross: untested; revisit on demand.
options = ["!check", "!cross"]


def install(self):
    # cargo install dislikes -p; binary copy, same as flautist.
    triplet = self.profile().triplet
    self.install_bin(f"target/{triplet}/release/pkg6depotd")


def post_install(self):
    self.install_license("LICENSE")
    # Reference config — the operator copies + edits; /usr/share
    # so `apk fix` never clobbers the live config.
    self.install_file(
        self.files_path / "pkg6depotd.kdl.example",
        "usr/share/pkg6depotd",
    )
    self.install_service(self.files_path / "pkg6depotd")
    self.install_sysusers(self.files_path / "sysusers.conf", name="pkg6depotd")
    self.install_tmpfiles(self.files_path / "tmpfiles.conf", name="pkg6depotd")


@subpackage("pkg6depotd-dinit")
def _(self):
    self.subdesc = "dinit service (local IPS mirror depot)"
    self.depends = [f"{pkgname}={pkgver}-r{pkgrel}", "dinit-chimera"]
    self.install_if = [f"{pkgname}={pkgver}-r{pkgrel}", "dinit-chimera"]
    return [
        "usr/lib/dinit.d/pkg6depotd",
        "usr/lib/sysusers.d/pkg6depotd.conf",
        "usr/lib/tmpfiles.d/pkg6depotd.conf",
    ]
