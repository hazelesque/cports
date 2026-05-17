broken = "make check Tools test fails"
pkgname = "msitools"
pkgver = "0.106"
pkgrel = 0
build_style = "meson"
configure_args = [
#    f"-Dversion-tag={pkgver}",
]
##make_build_args = ["prefix=/usr"]
##make_install_args = ["prefix=/usr"]
hostmakedepends = [
##    "bison",
##    "flex",
    "pkgconf",
]
makedepends = [
    "bash",
    "bison",
    "cmake",
    "gcab-devel",
    "git",
    "glib-devel",
    "gobject-introspection",
    "gobject-introspection-devel",
    "libgsf-devel",
    "meson",
    "perl",
    "vala",
    ##"linux-headers",
    ##"openssl3-devel",
]
depends = [
    "gcab",
    "glib",
    "gobject-introspection",
    "gobject-introspection-libs",
    "libgsf",
    ##"openssl3-libs",
]
pkgdesc = "Windows Installer file manipulation tool"
license = "LGPL-2.1-or-later"
url = "https://gitlab.gnome.org/GNOME/msitools"
source = [
    f"https://gitlab.gnome.org/GNOME/msitools/-/archive/v{pkgver}/msitools-v{pkgver}.tar.gz",
    "https://github.com/bats-core/bats-core/archive/refs/tags/v1.12.0.tar.gz",
]
source_paths = [
    ".",
    "subprojects/bats-core",
]
sha256 = [
    "01f56b97465d0449e9182ea9ed8b7a3588264c04f828cc07d9569accbc8a6648",
    "e36b020436228262731e3319ed013d84fcd7c4bd97a1b34dee33d170e9ae6bab",
]
tool_flags = {
##    "CFLAGS": ["-D_GNU_SOURCE"],
}
# /usr/share/bash-completion/completions/msitools has no matching command
options = [
##    "!distlicense",
    "!lintcomp",
]

def post_extract(self):
    (self.cwd / ".tarball-version").write_text(f"{pkgver}")
