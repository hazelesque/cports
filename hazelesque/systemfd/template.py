pkgname = "systemfd"
pkgver = "0.4.6"
pkgrel = 0
build_style = "cargo"
hostmakedepends = ["cargo-auditable"]
makedepends = ["rust-std"]
pkgdesc = "Helper for passing sockets into another process"
license = "Apache-2.0"
url = "https://github.com/mitsuhiko/systemfd"
source = f"{url}/archive/{pkgver}.tar.gz"
sha256 = "e2aa957a239543df86f0e153263faa6c658886a7c2fc9c30c2caba544d090734"


def install(self):
    self.install_file(
        f"target/{self.profile().triplet}/release/systemfd",
        "usr/bin",
        0o755,
    )
    self.install_license("LICENSE")
