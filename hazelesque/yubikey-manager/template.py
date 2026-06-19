pkgname = "yubikey-manager"
pkgver = "5.9.1"
pkgrel = 0
build_style = "python_pep517"
hostmakedepends = ["python-build", "python-installer", "python-poetry-core"]
depends = [
    "python-click",
    "python-cryptography",
    "python-fido2",
    "python-keyring",
    "python-pskc",
    "python-pyscard",
]
pkgdesc = "CLI and library for managing YubiKey configuration"
license = "BSD-2-Clause"
url = "https://github.com/Yubico/yubikey-manager"
source = f"$(PYPI_SITE)/y/yubikey-manager/yubikey_manager-{pkgver}.tar.gz"
sha256 = "83bda2a4bbb6a93bc07e5de73a0f30e5a8b811c85a9116aaca6dd3eed8abb0eb"
# Tests want a real YubiKey plugged in.
options = ["!check"]


def post_install(self):
    self.install_license("COPYING")
    # Ship the upstream man pages.  The poetry-core build doesn't
    # install them automatically; the upstream Makefile uses
    # generate-man.py which the sdist runs as part of `make man`.
    # The sdist includes the rendered .1 files pre-built under man/.
    for f in (self.cwd / "man").glob("*.1"):
        self.install_man(f)
