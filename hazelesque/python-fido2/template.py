pkgname = "python-fido2"
pkgver = "2.2.0"
pkgrel = 0
build_style = "python_pep517"
hostmakedepends = ["python-build", "python-installer", "python-poetry-core"]
depends = ["python-cryptography"]
pkgdesc = "FIDO2/WebAuthn library for implementing clients and servers"
license = "BSD-2-Clause"
url = "https://github.com/Yubico/python-fido2"
source = f"$(PYPI_SITE)/f/fido2/fido2-{pkgver}.tar.gz"
sha256 = "0d8122e690096ad82afde42ac9d6433a4eeffda64084f36341ea02546b181dd1"
# tests/test_pcsc.py hard-imports pyscard at collection time even
# though PC/SC is an optional runtime feature; adding pyscard as a
# checkdep just to keep the test suite happy isn't worth it.
options = ["!check"]


def post_install(self):
    self.install_license("COPYING")
