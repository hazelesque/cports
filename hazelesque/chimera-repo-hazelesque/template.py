pkgname = "chimera-repo-hazelesque"
pkgver = "0.1"
pkgrel = 0
archs = [
    "aarch64",
    "loongarch64",
    "ppc",
    "ppc64",
    "ppc64le",
    "riscv64",
    "x86_64",
]
build_style = "meta"
depends = ["chimera-repo-main", "chimera-repo-user"]
pkgdesc = "Chimera hazelesque repository"
license = "custom:meta"
url = "https://hazelesque.uk"


def install(self):
    self.install_file(
        self.files_path / "51-repo-hazelesque.list", "usr/lib/apk/repositories.d"
    )
    self.install_file(
        self.files_path / "52-repo-hazelesque-debug.list",
        "usr/lib/apk/repositories.d",
    )


@subpackage("chimera-repo-hazelesque-debug")
def _(self):
    self.subdesc = "debug packages"
    self.depends = [self.parent]

    return ["usr/lib/apk/repositories.d/*-debug.list"]
