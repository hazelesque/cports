pkgname = "python-prettytable"
pkgver = "3.17.0"
pkgrel = 0
build_style = "python_pep517"
hostmakedepends = [
    "python-build",
    "python-hatch_vcs",
    "python-hatchling",
    "python-installer",
]
depends = ["python", "python-wcwidth"]
pkgdesc = "Display tabular data in ASCII table format"
license = "BSD-3-Clause"
url = "https://github.com/prettytable/prettytable"
source = f"$(PYPI_SITE)/p/prettytable/prettytable-{pkgver}.tar.gz"
sha256 = "59f2590776527f3c9e8cf9fe7b66dd215837cca96a9c39567414cbc632e8ddb0"
# tests want pytest-lazy-fixtures (not packaged)
options = ["!check"]


def post_install(self):
    self.install_license("LICENSE")
