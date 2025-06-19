pkgname = "readpe"
pkgver = "0.84"
pkgrel = 0
build_style = "makefile"
make_build_args = ["prefix=/usr"]
make_install_args = ["prefix=/usr"]
makedepends = [
    "openssl3-devel",
    "linux-headers",
]
depends = [
    "openssl3-libs",
]
pkgdesc = "Command-line tools to manipulate Windows PE files"
license = "BSD-2-Clause AND LGPL-3.0-or-later AND GPL-2.0-or-later"
url = "https://github.com/mentebinaria/readpe"
source = (
    f"https://github.com/mentebinaria/readpe/archive/refs/tags/v{pkgver}.tar.gz"
)
sha256 = "2d0dc383735802db62234297ae1703ccbf4b6d2f2754e284eb90d6f0a57aa670"
tool_flags = {
    "CFLAGS": ["-D_GNU_SOURCE"],
}
# Check disabled because check target is not present in Makefile
options = [
    "!check",
    "!distlicense",
]
