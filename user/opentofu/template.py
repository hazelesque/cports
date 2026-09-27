pkgname = "opentofu"
pkgver = "1.12.0"
pkgrel = 0
build_style = "go"
make_build_args = [
    f"-ldflags=-X main.version={pkgver} -X github.com/opentofu/opentofu/version.dev=no",
    "./cmd/tofu",
]
hostmakedepends = ["go"]
checkdepends = ["bash"]
pkgdesc = "Tool for building, changing and versioning infrastructure"
license = "MPL-2.0"
url = "https://github.com/opentofu/opentofu"
source = f"{url}/archive/refs/tags/v{pkgver}.tar.gz"
sha256 = "d33c3c8ec139abae4c45e8a4187f1400032c8441a2eea4f976d2f16cdb5ec9f4"
