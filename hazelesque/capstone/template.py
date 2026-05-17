pkgname = "capstone"
pkgver = "5.0.6"
pkgrel = 0
build_style = "makefile"
configure_args = [
    "COMPILER=clang",
]
make_env = {
}
make_build_args = [
    "COMPILER=clang",
    "CC=clang",
    "USERCC=clang",
    "HOST_CC=clang",
    "CXX=clang++",
]
hostmakedepends = ["pkgconf"]
makedepends = [
]
depends = [
]
pkgdesc = "Disassembly framework for binary analysis and reversing"
license = "BSD-2-Clause AND LGPL-3.0-or-later AND GPL-2.0-or-later"
url = "http://www.capstone-engine.org"
source = [
    f"https://github.com/capstone-engine/capstone/archive/refs/tags/{pkgver}.tar.gz"
]
source_paths = [
    ".",
]
sha256 = [
    "240ebc834c51aae41ca9215d3190cc372fd132b9c5c8aa2d5f19ca0c325e28f9",
]
tool_flags = {
}
# make check not implemented
options = [
    "!check",
    "!distlicense",
]

def build(self):
    self.do("sh", "make.sh", "clang", *self.configure_args)

@subpackage("capstone-static")
def _(self):
    return self.default_static()

@subpackage("capstone-devel")
def _(self):
    return self.default_devel()


