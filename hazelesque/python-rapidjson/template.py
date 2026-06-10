pkgname = "python-rapidjson"
pkgver = "1.23"
pkgrel = 0
build_style = "python_pep517"
hostmakedepends = [
    "python-build",
    "python-installer",
    "python-setuptools",
]
makedepends = ["python-devel"]
depends = ["python"]
pkgdesc = "Python wrapper around RapidJSON"
license = "MIT"
url = "https://github.com/python-rapidjson/python-rapidjson"
source = f"$(PYPI_SITE)/p/python_rapidjson/python_rapidjson-{pkgver}.tar.gz"
sha256 = "0f845daeb26be147f5720a8c410308235092bb4fbb81ea408aa77203e26296fb"
# tests need pytest-benchmark and friends; packaged as a pkg5-mirror-tools dep
options = ["!check"]


def post_install(self):
    self.install_license("LICENSE")
