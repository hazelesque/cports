pkgname = "python-pyscard"
pkgver = "2.3.1"
pkgrel = 0
build_style = "python_pep517"
hostmakedepends = [
    "pkgconf",
    "python-build",
    "python-installer",
    "python-setuptools",
    "swig",
]
makedepends = ["pcsc-lite-devel", "python-devel"]
depends = ["pcsc-lite"]
pkgdesc = "Python module for smart cards via PC/SC"
license = "LGPL-2.1-or-later"
url = "https://github.com/LudovicRousseau/pyscard"
source = f"$(PYPI_SITE)/p/pyscard/pyscard-{pkgver}.tar.gz"
sha256 = "a24356f57a0a950740b6e54f51f819edd5296ee8892a6625b0da04724e9e6c13"
# Tests need a real pcscd + card reader.
options = ["!check"]


def post_install(self):
    self.install_license("LICENSE")
