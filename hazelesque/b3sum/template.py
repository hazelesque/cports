pkgname = "b3sum"
pkgver = "1.8.5"
pkgrel = 0
build_style = "cargo"
# The b3sum crate lives in b3sum/ inside the BLAKE3 monorepo;
# its Cargo.toml has `blake3 = { path = ".." }`, so vendor and
# build must run from b3sum/ to resolve the parent crate.
make_dir = "b3sum"
hostmakedepends = ["cargo-auditable"]
makedepends = ["rust-std"]
pkgdesc = "Command-line BLAKE3 hash utility"
license = "CC0-1.0 OR Apache-2.0 OR Apache-2.0 WITH LLVM-exception"
url = "https://github.com/BLAKE3-team/BLAKE3"
source = f"{url}/archive/{pkgver}.tar.gz"
sha256 = "220bd81286e2a0585beac66d41ac3f4c2c33ae8a4e339fc88cf22d5e00514fe9"


def prepare(self):
    # Pass wrksrc explicitly: cargo.vendor()'s own dirn calculation
    # ignores make_dir and writes .cargo/config.toml at template.cwd,
    # while the actual vendor tree lands under wrksrc.  Without this,
    # config.toml at the root points at a non-existent root vendor/.
    self.cargo.vendor(wrksrc="b3sum")


def install(self):
    self.install_file(
        f"b3sum/target/{self.profile().triplet}/release/b3sum",
        "usr/bin",
        0o755,
    )
    self.install_license("LICENSE_A2")
    self.install_license("LICENSE_A2LLVM")
    self.install_license("LICENSE_CC0")
