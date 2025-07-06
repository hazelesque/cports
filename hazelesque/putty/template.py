pkgname = "putty"
pkgver = "0.83"
pkgrel = 1
build_style = "cmake"
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
    "ninja",
    "cmake",
    "re2c",
    "perl",
##    "meson",
##    "vala",
##    "perl",
##    "bison",
##    "cmake",
##    "glib-devel",
##    "libgsf-devel",
##    "gcab-devel",
##    "gobject-introspection",
##    "gobject-introspection-devel",
##    "bash",
    "git",
    ##"openssl3-devel",
    "linux-headers",
    "gtk+3-devel",
]
depends = [
    ##"openssl3-libs",
##    "glib",
##    "libgsf",
##    "gcab",
##    "gobject-introspection",
##    "gobject-introspection-libs",
    "gtk+3",
]
pkgdesc = "Free implementation of SSH and Telnet for Windows and Unix platforms"
license = "MIT"
url = "https://www.chiark.greenend.org.uk/~sgtatham/putty"
source = [
    f"https://the.earth.li/~sgtatham/putty/latest/putty-{pkgver}.tar.gz",
]
source_paths = [
    ".",
]
sha256 = [
    "718777c13d63d0dff91fe03162bc2a05b4dfc8b0827634cd60b51cefdff631c6",
]
tool_flags = {
##    "CFLAGS": ["-D_GNU_SOURCE"],
}
# /usr/share/bash-completion/completions/msitools has no matching command
options = [
    "!distlicense",
##    "!lintcomp",
]

##def post_extract(self):
##    (self.cwd / ".tarball-version").write_text(f"{pkgver}")
