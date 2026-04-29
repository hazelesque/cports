pkgname = "bazel-7.4.0"
pkgver = "7.4.0"
pkgrel = 1
archs = ["aarch64", "ppc64le", "x86_64"]
# cports default is extract -> prepare -> patch; we need patches
# (chimera-java-toolchain in particular) applied BEFORE bazel-
# bootstrap reads .bazelrc and selects toolchains.
prepare_after_patch = True
hostmakedepends = [
    "bash",
    "bazel-7.4.0-bootstrap",
    "clang",
    "openjdk21",
    "pkgconf",
    "python",
    "unzip",
    "zip",
]
makedepends = [
    # abseil-cpp's spinlock_linux.inc pulls <linux/futex.h>; not in
    # musl-devel.  Same need as bazel-7.4.0-bootstrap.
    "linux-headers",
    "openjdk21-jdk",
    "zlib-ng-compat-devel",
]
depends = ["openjdk21-jre"]
pkgdesc = "Bazel build tool, built with Bazel"
license = "Apache-2.0"
url = "https://bazel.build"
# Same dist zip as bazel-7.4.0-bootstrap — the difference is only
# in the build path: bootstrap uses compile.sh end-to-end, this
# package uses the bootstrap bazel to invoke
# `bazel build src:bazel` per
# https://bazel.build/install/compile-source#build-bazel-using-bazel.
# We deliberately do not pull from a separate `git clone of the tag`
# tarball even though upstream documents it that way; the dist zip
# already carries every generated proto stub the build needs and is
# what we have audited patches against.
source = (
    f"https://github.com/bazelbuild/bazel/releases/download/{pkgver}/"
    f"bazel-{pkgver}-dist.zip"
)
sha256 = "198d70bb73b93bb2b630c26feb08c4f832e7520c2390776672a853d68f46f428"
# bazel ships its own test suite (`bazel test //src/test/...`); not
# something we run during a package build.
options = [
    "!check",
    "!cross",
    "!debug",
    "!distlicense",
    "!lto",
    "!parallel",
    "!scanrundeps",
    "!strip",
    "foreignelf",
]


def init_prepare(self):
    # Absolute paths because bazel's local_config_cc probes via
    # absolute lookup, not PATH.  Matches the working copybara
    # build command's `CC=/usr/bin/clang`.
    self.env["CC"] = "/usr/bin/clang"
    self.env["CXX"] = "/usr/bin/clang++"
    self.env["JAVA_HOME"] = "/usr/lib/jvm/java-21-openjdk"


def prepare(self):
    # Same network-during-prepare hack as bazel-7.4.0-bootstrap:
    # `bazel build src:bazel` resolves bzlmod deps from
    # bcr.bazel.build at action time, and cbuild won't allow
    # network in build phase.  TODO: vendor distfiles via
    # `--distdir` and switch to a sealed offline build.
    #
    # `--config=chimera`-equivalent flags below substitute the
    # source-built Java toolchain for the glibc-linked prebuilts in
    # @remote_java_tools_linux (would otherwise execvp-fail on
    # musl).  Pattern lifted verbatim from copybara's .bazelrc; see
    # scm-infra/copybara/tools/chimera_java_toolchain/BUILD for the
    # toolchain definition this corresponds to.
    bazel_build_args = [
        "--lockfile_mode=update",
        "--copt=-D_GNU_SOURCE",
        "--copt=-D_LARGEFILE64_SOURCE",
        "--host_copt=-D_GNU_SOURCE",
        "--host_copt=-D_LARGEFILE64_SOURCE",
        "--java_runtime_version=local_jdk",
        "--tool_java_runtime_version=local_jdk",
        # `--embed_label` is silently ignored unless `--stamp` is
        # also set; without both, `bazel --version` reads
        # "no_version" and downstream tooling that keys off
        # bazel_features (which parses the version string to detect
        # available Starlark globals) blows up on `name 'macro' is
        # not defined`-shaped errors against newer rules sets.
        # compile.sh's EMBED_LABEL_ARG sets the pair together; mirror
        # that here for bazel-build-bazel.
        "--stamp",
        f"--embed_label={pkgver}",
    ]
    # //src:bazel_nojdk, not //src:bazel.  The latter triggers
    # the //src:embedded_jdk_minimal genrule, which downloads a
    # Zulu OpenJDK tarball and runs jlink against it — same
    # cdn.azul.com / glibc-prebuilt class of problem we already
    # avoid on the toolchain side.  We ship openjdk21-jre as a
    # runtime dep anyway, so an embedded JDK is redundant; this
    # mirrors what compile.sh produces (its `output/bazel` is
    # bazel_nojdk).
    # `--output_user_root` MUST land somewhere persistent.  cbuild
    # gives every phase a fresh bwrap session with /tmp mounted as
    # a tmpfs that's destroyed at session end, and bazel's default
    # ($HOME/.cache/bazel) lands inside it.  /builddir is the
    # cports-bound persistent workspace; outputs there survive
    # across phase boundaries so install() can pick up the binary
    # via the bazel-bin symlink.
    self.do(
        "bazel-bootstrap",
        "--output_user_root=/builddir/.bazel-cache",
        "build",
        *bazel_build_args,
        "//src:bazel_nojdk",
        env=self.env,
        allow_network=True,
    )
    # Lift the artifact out of bazel-bin/ into the workspace root.
    # bazel-bin -> /builddir/.bazel-cache/<hash>/.../bazel_nojdk;
    # that target only resolves *inside* the sandbox (the bind-
    # mount path naming differs from the host path), so install()
    # outside the sandbox can't follow the symlink.  The cp runs
    # in its own bwrap session, but outputs persist across
    # sessions now that --output_user_root points at /builddir.
    self.do(
        "cp",
        "bazel-bin/src/bazel_nojdk",
        "bazel_nojdk",
        env=self.env,
    )


def build(self):
    pass


def install(self):
    self.install_license("LICENSE")
    self.install_dir("usr/lib/bazel")
    # `bazel_nojdk` was lifted out of bazel-bin/ at the end of
    # prepare() — see comment there for why we can't follow the
    # bazel-bin symlink directly from install().  Rename to plain
    # `bazel` on install; JRE supplied via openjdk21-jre runtime.
    self.install_file(
        "bazel_nojdk",
        "usr/lib/bazel",
        name="bazel",
        mode=0o755,
    )
    self.install_dir("usr/bin")
    self.install_link("usr/bin/bazel", "../lib/bazel/bazel")
