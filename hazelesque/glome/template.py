pkgname = "glome"
pkgver = "0.3.0"
pkgrel = 0
build_style = "meson"
configure_args = [
    "-Dtests=true",
    "-Dpam-glome=true",
    "-Dglome-cli=true",
]
hostmakedepends = ["meson", "pkgconf"]
makedepends = [
    "glib-devel",
    "linux-pam-devel",
    "openssl3-devel",
]
pkgdesc = "Generic Low Overhead Message Exchange authentication"
license = "Apache-2.0"
url = "https://github.com/google/glome"
source = f"{url}/archive/refs/tags/v{pkgver}.tar.gz"
sha256 = "be904ce193dfaffc4901e9c0f3bde762dfc752da51012eb9972dc45f05db6638"


def post_install(self):
    self.install_license("LICENSE")


@subpackage("glome-libs")
def _(self):
    return self.default_libs()


@subpackage("glome-devel")
def _(self):
    return self.default_devel()


@subpackage("glome-pam")
def _(self):
    self.subdesc = "PAM module"
    self.depends = [self.parent, "linux-pam"]
    self.install_if = [self.parent, "linux-pam"]

    return ["usr/lib/security"]
