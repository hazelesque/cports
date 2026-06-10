pkgname = "python-jsonrpclib-pelix"
pkgver = "1.1.0"
pkgrel = 0
build_style = "python_pep517"
hostmakedepends = [
    "python-build",
    "python-hatchling",
    "python-installer",
]
depends = ["python"]
pkgdesc = "Pelix fork of the jsonrpclib JSON-RPC client and server"
license = "Apache-2.0"
url = "https://github.com/tcalmant/jsonrpclib"
source = f"$(PYPI_SITE)/j/jsonrpclib_pelix/jsonrpclib_pelix-{pkgver}.tar.gz"
sha256 = "379a3c9b3dd478727419587aa7cf14bb6ff0e64301decc0ffa98f710f6bfec1e"
# tests spin up live JSON-RPC servers; packaged as a pkg5-mirror-tools dep
options = ["!check"]


def post_install(self):
    self.install_license("LICENSE")
