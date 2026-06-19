pkgname = "python-pskc"
pkgver = "1.4"
pkgrel = 0
build_style = "python_pep517"
hostmakedepends = ["python-build", "python-installer", "python-setuptools"]
depends = ["python-cryptography", "python-dateutil"]
pkgdesc = "Python module for handling Portable Symmetric Key Container files"
license = "LGPL-2.1-or-later"
url = "https://arthurdejong.org/python-pskc"
source = f"$(PYPI_SITE)/p/python-pskc/python_pskc-{pkgver}.tar.gz"
sha256 = "4a36381446ca067be728b30e01b4d18dbd9d1ad553bf07c3710abcd87653eefe"
# Upstream's setup.cfg pytest config hard-codes --cov=pskc; pytest-cov
# isn't packaged in Chimera and we don't need coverage at build time.
options = ["!check"]


def post_install(self):
    self.install_license("COPYING")
