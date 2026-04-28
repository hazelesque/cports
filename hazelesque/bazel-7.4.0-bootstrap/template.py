pkgname = "bazel-7.4.0-bootstrap"
pkgver = "7.4.0"
pkgrel = 0
archs = ["aarch64", "ppc64le", "x86_64"]
hostmakedepends = [
    "bash",
    "clang",
    "openjdk21",
    "pkgconf",
    "python",
    "unzip",
    "zip",
]
makedepends = [
    # abseil-cpp's spinlock_linux.inc pulls <linux/futex.h>; not in
    # musl-devel.  Same need will recur for any package that
    # transitively builds something Linux-syscall-aware.
    "linux-headers",
    "openjdk21-jdk",
    "zlib-ng-compat-devel",
]
depends = ["openjdk21-jre"]
pkgdesc = "Bazel build tool, source-bootstrapped via compile.sh"
license = "Apache-2.0"
url = "https://bazel.build"
# Upstream's "build from a release distribution archive" path
# (https://bazel.build/install/compile-source#bootstrap-bazel) — a
# zip pre-populated with all generated proto + grpc stubs so that
# the bootstrap doesn't need a working bazel to run them.  We ship
# this rather than the github tag tarball so the bootstrap stays
# self-contained.
source = (
    f"https://github.com/bazelbuild/bazel/releases/download/{pkgver}/"
    f"bazel-{pkgver}-dist.zip"
)
sha256 = "198d70bb73b93bb2b630c26feb08c4f832e7520c2390776672a853d68f46f428"
# compile.sh bakes timestamps and the JDK path into the resulting
# binary's data section, so we let it do its thing rather than
# fighting the SOURCE_DATE_EPOCH plumbing.  install_base hashes
# the install tree so any inadvertent changes to the layout get
# caught at runtime.
options = [
    "!check",  # bazel ships its own test suite; not run during package build
    "!cross",  # compile.sh has no cross story — host builds only
    "!debug",  # the embedded launcher refuses -g binaries' relocations
    "!distlicense",  # LICENSE ships in /usr/lib/<pkg>/, install_license() handles top-level
    "!lto",  # bazel's compile.sh links .o's into a self-extracting blob; lto breaks it
    "!parallel",  # compile.sh manages its own parallelism via JOBS env
    "!scanrundeps",  # bazel binary embeds a JVM jar — scanner trips over it
    "!strip",  # the launcher reads its own ELF for the embedded zip; strip eats the marker
    "foreignelf",  # libblaze.jar contains pre-built native helpers (linux-x86_64 .so's)
]


# compile.sh is the only sane entry point — it owns the
# javac->bootstrap-bazel->bazel-builds-bazel sequence end-to-end.
# We can't split it across cports build phases because the inner
# bootstrap stage and the outer "build src:bazel_nojdk via the
# bootstrap bazel" stage share state through $OUTPUT_DIR.
#
# The outer stage does fetch MODULE deps from the network.  cbuild
# only allows network in fetch/extract/prepare/patch, so the whole
# build runs in prepare() with allow_network=True.  Yes, this is
# offside relative to the cports phase model — it's the cargo
# pattern (prepare = network-yes, build = network-no).  TODO:
# pre-stage every MODULE dep + http_archive into source = [...]
# entries and switch to a real offline build.  See
# combine_distfiles_to_tar.sh in the bazel tree for what to vendor.
def init_prepare(self):
    self.env["BAZEL_JAVAC_OPTS"] = "-g:source,lines"
    # Bake the version into the resulting bazel binary; without
    # these, `bazel --version` reads "(non-git)" and the embedded
    # release label is empty.  Mirrors Alpine's bazel7 APKBUILD.
    self.env["EMBED_LABEL"] = pkgver
    self.env["BAZEL_DEV_VERSION_OVERRIDE"] = pkgver
    # Absolute paths because bazel's local_config_cc probes via
    # absolute lookup, not PATH.  Matches the working copybara
    # build command's `CC=/usr/bin/clang`.
    self.env["CC"] = "/usr/bin/clang"
    self.env["CXX"] = "/usr/bin/clang++"
    # JAVA_HOME for compile.sh's javac probe.  openjdk21 in cports
    # installs to /usr/lib/jvm/java-21-openjdk.
    self.env["JAVA_HOME"] = "/usr/lib/jvm/java-21-openjdk"
    # Force bzlmod to refresh the lockfile rather than refusing to
    # build because our MODULE.bazel patch left it stale.
    self.env["EXTRA_BAZEL_ARGS"] = (
        "--lockfile_mode=update "
        # Chimera-equivalent of copybara's --config=chimera flags;
        # _GNU_SOURCE / _LARGEFILE64_SOURCE for off64_t on musl
        # in remote_java_tools C++ compiles.
        "--copt=-D_GNU_SOURCE "
        "--copt=-D_LARGEFILE64_SOURCE "
        "--host_copt=-D_GNU_SOURCE "
        "--host_copt=-D_LARGEFILE64_SOURCE "
        # Pin both the runtime and the tool JDK to whatever sits at
        # JAVA_HOME (openjdk21 above).  Without these, bazel's
        # default toolchain resolution downloads a glibc-linked
        # Zulu OpenJDK 11 from cdn.azul.com and tries to exec its
        # javac — which dies on musl with error=2 (ENOENT-shaped
        # failure of dynamic-linker resolution; the actual missing
        # file is /lib64/ld-linux-x86-64.so.2, not javac).
        "--java_runtime_version=local_jdk "
        "--tool_java_runtime_version=local_jdk"
    )


def prepare(self):
    self.do(
        "bash",
        "compile.sh",
        env=self.env,
        allow_network=True,
    )


def build(self):
    # All real work happened in prepare(); this phase is a no-op.
    # The native binary lives at output/bazel relative to the
    # source root.
    pass


def install(self):
    self.install_license("LICENSE")
    # Self-contained binary — embeds its own runtime jar + native
    # helpers.  Lives under /usr/lib/<pkg>/ rather than /usr/bin so
    # the "real" bazel package can occupy /usr/bin/bazel without
    # collision.
    self.install_dir(f"usr/lib/{pkgname}")
    self.install_file("output/bazel", f"usr/lib/{pkgname}", mode=0o755)
    # Convenience symlink so downstream packages can hostmakedepend
    # on us and call `bazel-bootstrap` unambiguously.
    self.install_dir("usr/bin")
    self.install_link(
        "usr/bin/bazel-bootstrap",
        f"../lib/{pkgname}/bazel",
    )
