# The "SCIP generator for Bazel" piece of github.com/uber/scip-lsp.
# Concretely the `bsp_server/scip_sync_util:scip_sync` py_binary —
# the rest of scip-lsp (the Go ulsp-daemon, the VS Code extension)
# is intentionally out of scope.
#
# upstream's scip_sync runs as a `bazel run` py_binary target,
# meaning bazel materializes a runfiles tree and a launcher script.
# We ship something cleaner: the bsp_server.* Python package tree
# under site-packages (PEP 420 namespace, no __init__.py needed)
# and a one-line shell launcher that does
# `python3 -m bsp_server.scip_sync_util.scip_sync "$@"`.
#
# scip_sync at runtime invokes `bazel query` / `bazel run` against
# the *target* repo's MODULE.bazel / BUILD files — the indexer
# targets (scip-java, scip-clang) live in the repo being indexed,
# not in this package.  README's "Manual Setup Steps" enumerates
# the bazel_dep + maven.install entries the user must add to their
# repo's MODULE.bazel.

pkgname = "scip-lsp-bazel-generator"
pkgver = "0.1.2"
pkgrel = 0
hostmakedepends = [
    # Needed at configure time so cbuild populates
    # self.python_version (see Packaging.md "self.python_version").
    # Used in install() to land the .py files under the right
    # site-packages directory; also lets cports' 005_py_dep hook
    # validate the destdir layout.
    "python",
]
makedepends = []
depends = [
    # cmd:bazel virtual; cports requires the !provider suffix so
    # the manifest records exactly which package satisfied it
    # (avoids ambiguity if a future cports gains multiple bazel
    # packages providing the same cmd virtual).
    "cmd:bazel!bazel-7.4.0",
    "python",
    "python-tqdm",
]
pkgdesc = "SCIP index generator for Bazel workspaces, from uber/scip-lsp"
license = "Apache-2.0"
url = "https://github.com/uber/scip-lsp"
source = f"{url}/archive/refs/tags/v{pkgver}.tar.gz"
sha256 = "ee83b4df4ebe8aab9de6101099df58a49f49c2d60a4843578799efd441b2962f"
# No build phase — we only ship .py files.  No tests run because
# the upstream pytest fixtures need bazel + a fake target repo.
options = [
    "!check",
    "!cross",
    "!debug",
    "!distlicense",
    "!lto",
    "!parallel",
    "!scanrundeps",
    "!strip",
]


def install(self):
    self.install_license("LICENSE")
    # Mirror the upstream bsp_server.* namespace under site-packages
    # so the existing `from bsp_server.scip_sync_util.X import Y`
    # imports resolve unmodified.  PEP 420 namespace packages mean
    # we don't need __init__.py files.
    sp = f"usr/lib/python{self.python_version}/site-packages/bsp_server"
    for sub, files in [
        (
            "scip_sync_util",
            [
                "incremental.py",
                "mnemonics.py",
                "scip_const.py",
                "scip_sync.py",
                "scip_utils.py",
                "workspace.py",
            ],
        ),
        ("bazel", ["execute_query.py"]),
        ("util", ["utils.py"]),
    ]:
        for f in files:
            self.install_file(f"bsp_server/{sub}/{f}", f"{sp}/{sub}")
    # Launcher.  Lives in files/ rather than being generated inline
    # because cports' template API doesn't expose a write-file
    # helper.
    self.install_file(self.files_path / "scip-sync", "usr/bin", mode=0o755)
