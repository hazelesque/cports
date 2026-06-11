pkgname = "pkg5-mirror-tools"
pkgver = "0_git20250713"
pkgrel = 1
_gitrev = "4e1d42c72f1a4cc91a4ea107a4cb4e2075a067cf"
build_wrksrc = "src"
hostmakedepends = [
    "python",
    "python-cffi",
    "python-setuptools",
    "python-six",  # setup.py imports it at module level
]
makedepends = ["python-devel"]
depends = [
    "python",
    "python-cryptography",
    "python-jsonrpclib-pelix",
    "python-jsonschema",
    "python-openssl",
    "python-ply",
    "python-prettytable",
    "python-pycurl",
    "python-rapidjson",
    "python-six",
]
pkgdesc = "IPS repository mirroring tools (pkgrecv, pkgrepo) from pkg5"
license = "CDDL-1.0 AND MIT"
url = "https://github.com/OpenIndiana/pkg5"
source = f"{url}/archive/{_gitrev}.tar.gz>pkg5-{pkgver}.tar.gz"
sha256 = "b45b7bdf4a9eaafeb8ef1824c8649663693b682f48b6b9ea27bc06b7ab669360"
# !check: upstream test suite assumes a full Solaris pkg(7) install;
# only the mirror-tools subset (pkgrecv/pkgrepo) is shipped here.
# !cross: setup.py drives the host python's distutils directly.
options = ["!check", "!cross"]

# The mirror PULL side of the local OmniOS IPS mirror: pkgrecv
# (src/pull.py) + pkgrepo (src/pkgrepo.py) and the pkg python
# package they import.  The serve side is hazelesque/pkg6depotd;
# see scm-infra/kajiya/spikes/pkg-depot-investigation.md for the
# verified end-to-end pairing and the per-C-extension porting
# notes behind patches/chimera-linux-extensions.patch.  The
# pkg(1) client, pkg.depotd, pkglint etc. are deliberately NOT
# packaged.


def build(self):
    self.do("python3", "setup.py", "build")


def install(self):
    pyver = self.python_version
    proto = (
        "../proto/build_linux_x86_64/"
        f"lib.linux-x86_64-cpython-{pyver.replace('.', '')}/pkg"
    )
    # Drop any build-tree bytecode; regenerated against the final
    # install paths in post_install.
    self.do(
        "find",
        proto,
        "-name",
        "__pycache__",
        "-prune",
        "-exec",
        "rm",
        "-rf",
        "{}",
        "+",
    )
    self.install_files(proto, f"usr/lib/python{pyver}/site-packages")
    # Same entry-point renames setup.py performs for the Solaris
    # install (scripts_sunos); upstream's Linux script list never
    # got the renamed forms.
    self.install_bin("pull.py", name="pkgrecv")
    self.install_bin("pkgrepo.py", name="pkgrepo")
    self.install_man("man/pkgrecv.1")
    self.install_man("man/pkgrepo.1")


def post_install(self):
    from cbuild.util import python

    self.install_license("../LICENSE-CDDL")
    # MIT: the minisat-derived solver extension + cpiofile.py
    self.install_license("../LICENSE-MINISAT")
    self.install_license("../LICENSE-CPIO")
    python.precompile(
        self, f"usr/lib/python{self.python_version}/site-packages/pkg"
    )
