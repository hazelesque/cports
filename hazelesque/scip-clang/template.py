pkgname = "scip-clang"
pkgver = "0.4.0"
pkgrel = 0
archs = ["aarch64", "x86_64"]
# Patches modify WORKSPACE / setup_deps.bzl / indexer/Exception.cc;
# they MUST land before bazel reads the workspace.  cports default
# is extract -> prepare -> patch, which would run our prepare()
# (the bazel build) too early.
prepare_after_patch = True
hostmakedepends = [
    "bash",
    "bazel-7.4.0-bootstrap",
    "clang",
    "clang-devel",
    "openjdk21",
    "pkgconf",
    "python",
    "zip",
]
makedepends = [
    "clang-devel",
    # abseil + grpc transitively pull <linux/futex.h>, not in
    # musl-devel.  Same need as bazel-7.4.0.
    "linux-headers",
    "llvm-devel",
    "zlib-ng-compat-devel",
]
depends = []
pkgdesc = "SCIP indexer for C, C++, CUDA"
license = "Apache-2.0"
url = "https://github.com/sourcegraph/scip-clang"
source = f"https://github.com/sourcegraph/scip-clang/archive/refs/tags/v{pkgver}.tar.gz"
sha256 = "94ef362fa7d095975a2a8b143934056eed9f530915d5e17b54dd01df2e17b3a0"
# `bazel test //...` pulls indexer fixtures over the network; not
# runnable in cports' sealed build phase.
options = [
    "!check",
    "!cross",
    "!debug",
    "!distlicense",
    "!lto",  # bazel manages its own optimization; cflag injection clashes
    "!parallel",  # bazel parallelizes itself
    "!scanrundeps",
    "!strip",
    "foreignelf",  # bazel-built binary may carry exec-config artefacts
]


def init_prepare(self):
    # Absolute paths because bazel's local_config_cc probes via
    # absolute lookup, not PATH.  Same as bazel-7.4.0.
    self.env["CC"] = "/usr/bin/clang"
    self.env["CXX"] = "/usr/bin/clang++"
    self.env["JAVA_HOME"] = "/usr/lib/jvm/java-21-openjdk"


def prepare(self):
    # bazel-bootstrap as the build driver, same pattern as
    # bazel-7.4.0 (see that template's prepare() for the
    # output_user_root / sandbox-tmpfs reasoning).
    #
    # `--repo_env=BAZEL_DO_NOT_DETECT_CPP_TOOLCHAIN=0` overrides
    # the in-tree .bazelrc setting (`...=1`); without this flip,
    # local_config_cc never probes the system clang and the
    # WORKSPACE patch's "skip llvm_register_toolchains and let
    # local_config_cc pick up /usr/bin/clang" plan is inert.
    bazel_args = [
        "--repo_env=BAZEL_DO_NOT_DETECT_CPP_TOOLCHAIN=0",
        # Bazel defaults to its own linux-sandbox for action
        # execution, which mounts /sys/proc/etc into a fresh
        # namespace.  We're already inside cports' bwrap sandbox,
        # which doesn't permit nested namespace operations —
        # linux-sandbox-pid1.cc dies with "mount /sys: Operation
        # not permitted" on every action.  Run actions directly
        # via the local strategy; cports' bwrap is the one source
        # of isolation.
        "--spawn_strategy=local",
        # Bazel's vendored LLVM overlay hardcodes HAVE_MALLINFO=1
        # and BACKTRACE_HEADER=<execinfo.h> in its config.h —
        # both glibc-only.  On musl, the Process.inc / Signals.inc
        # branches gated behind HAVE_MALLINFO / HAVE_BACKTRACE
        # fail to compile (incomplete struct mallinfo, missing
        # <execinfo.h>).  Override with -U on copt; copts append
        # after the overlay's -D, so -U wins.  Mirrored on
        # host_copt so exec-config compiles (e.g. tablegen for
        # tools used during the build) get the same treatment.
        "--copt=-UHAVE_BACKTRACE",
        "--copt=-UHAVE_MALLINFO",
        "--host_copt=-UHAVE_BACKTRACE",
        "--host_copt=-UHAVE_MALLINFO",
    ]
    self.do(
        "bazel-bootstrap",
        "--output_user_root=/builddir/.bazel-cache",
        "build",
        *bazel_args,
        "//indexer:scip-clang",
        env=self.env,
        allow_network=True,
    )
    # Same pattern as bazel-7.4.0: bazel-bin/* symlinks resolve
    # only inside the sandbox, so cp the artifact out into the
    # workspace root where install_file() (which runs outside
    # the sandbox) can pick it up.
    self.do(
        "cp",
        "bazel-bin/indexer/scip-clang",
        "scip-clang",
        env=self.env,
    )


def build(self):
    pass


def install(self):
    self.install_license("LICENSE")
    self.install_file("scip-clang", "usr/bin", mode=0o755)
