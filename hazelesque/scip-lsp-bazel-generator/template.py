# The "SCIP generator for Bazel" piece of github.com/uber/scip-lsp.
# Concretely the `bsp_server/scip_sync_util:scip_sync` py_binary
# (the Python driver) PLUS the bazel-side aspect + Java aggregator
# tree it consumes.  The Go ulsp-daemon and VS Code extension are
# intentionally out of scope.
#
# Two install destinations:
#
# (1) /usr/lib/python<ver>/site-packages/bsp_server/{scip_sync_util,
#     bazel,util}/ — the Python driver.  Upstream runs this via
#     `bazel run`, materializing a runfiles tree; we ship it as a
#     plain Python package with a /usr/bin/scip-sync launcher that
#     does `python3 -m bsp_server.scip_sync_util.scip_sync "$@"`.
#     PEP 420 namespace package so no __init__.py needed.
#
# (2) /usr/share/scip-lsp/{MODULE.bazel, bsp_server/indexer/,
#     src/main/java/com/uber/{scip,intellij}/} — the aspect .bzl,
#     its BUILD.bazel + config.template, and the Java aggregator /
#     extractor / decompiler source the aspect references via
#     @scip_lsp//src/main/java/...:*_bin.  scip_sync.py shells out
#     to `bazel build ... --aspects=@scip_lsp//bsp_server/indexer:
#     scip.bzl%scip_java_aspect`; the user must wire @scip_lsp into
#     their target repo so bazel can find the aspect (see header
#     of /usr/share/scip-lsp/MODULE.bazel — local_path_override).
#
# Indexing flow at runtime:
#   1. Target repo's MODULE.bazel does
#        local_path_override(module_name = "scip-lsp",
#                            path = "/usr/share/scip-lsp")
#      (or equivalently passes --override_module to bazel).
#   2. User's repo's MODULE.bazel also pulls in the SCIP-Java
#      maven artifacts per upstream README's "Manual Setup Steps"
#      (com.sourcegraph:scip-java_2.13, scip-semanticdb, etc.).
#   3. `scip-sync --cwd=<target-repo>` discovers java_* targets,
#      shells out to `bazel build ... --aspects ...`, and bazel
#      builds aggregator_bin + extractor_bin + decompiler_bin from
#      the @scip_lsp tree under /usr/share/scip-lsp/ on demand.

pkgname = "scip-lsp-bazel-generator"
pkgver = "0.1.2"
pkgrel = 1
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
# No build phase — we only ship .py + .java + .bzl files; the
# Java aggregator is built on demand by the consuming repo's
# bazel.  No tests run because the upstream pytest fixtures need
# bazel + a fake target repo.
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
    # Bazel-side aspect data.  Mirrors upstream paths under
    # /usr/share/scip-lsp/ so a target repo's
    #   local_path_override(module_name="scip-lsp",
    #                       path="/usr/share/scip-lsp")
    # in MODULE.bazel makes @scip_lsp resolve to this tree.
    # bazel will build the Java aggregator/extractor/decompiler
    # binaries from these sources on demand when scip_sync.py
    # invokes `bazel build ... --aspects=@scip_lsp//bsp_server/
    # indexer:scip.bzl%scip_java_aspect`.
    sd = "usr/share/scip-lsp"
    self.install_file("MODULE.bazel", sd)
    self.install_files("bsp_server/indexer", f"{sd}/bsp_server")
    self.install_files(
        "src/main/java/com/uber/scip", f"{sd}/src/main/java/com/uber"
    )
    self.install_files(
        "src/main/java/com/uber/intellij", f"{sd}/src/main/java/com/uber"
    )
