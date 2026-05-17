pkgname = "r2ghidra"
pkgver = "5.9.9" # Not really, but they seem to skip odd numbers and this is unreleased git HEAD
pkgrel = 0
##build_style = "configure"
build_style = "meson"
##build_style = "makefile"
configure_args = [
###    "COMPILER=clang",
###    "--with-syscapstone",
###    "--prefix=/usr",
##    "--disable-nls",
##    "--disable-werror",
##    "--enable-debuginfod",
##    "--enable-deterministic-archives",
##    "--enable-libdebuginfod",
##    "--with-zstd",
##    "--program-prefix=eu-",
]
configure_env = {
    "MESON_PACKAGE_CACHE_DIR": "subprojects/packagecache",
}
# autoreconf generates junk configure
make_env = {
    "MESON_PACKAGE_CACHE_DIR": "subprojects/packagecache",
##    "CS_ARCHIVE": "capstone/"
}
##make_build_args = ["prefix=/usr"]
make_build_args = [
##    "COMPILER=clang",
##    "CC=clang",
##    "USERCC=clang",
##    "HOST_CC=clang",
##    "CXX=clang++",
##    "CS_ARCHIVE=capstone/",
##    "WANT_CAPSTONE=0",
##    "USE_CAPSTONE=0",
##    "WITHOUT_PULL=1",
]
##make_install_args = ["prefix=/usr"]
##configure_gen = []
hostmakedepends = [
##    "bison",
##    "flex",
    "pkgconf",
]
makedepends = [
    "capstone-devel",
    "meson",
    "radare2",
    "zlib-ng-compat-devel",
    "zlib-ng-devel",
##    "argp-standalone",
##    "bzip2-devel",
##    "chimerautils-devel",
##    "curl-devel",
##    "json-c-devel",
##    "libarchive-devel",
##    "libmicrohttpd-devel",
##    "libpng-devel",
##    "linux-headers",
##    "linux-headers",
##    "musl-bsd-headers",
##    "musl-obstack-devel",
##    "openssl3-devel",
##    "sqlite-devel",
##    "xz-devel",
##    "zstd-devel",
]
depends = [
    "capstone",
##    "openssl3-libs",
##    "libpng",
]
##checkdepends = ["bash"]
# transitional
##provides = [self.with_pkgver("elftoolchain")]
pkgdesc = "JavaScript-based decompiler that converts assembly code into pseudo-C"
license = "BSD-3-Clause AND MIT"	
url = "https://github.com/wargio/r2dec-js"
source = [
    ##f"https://github.com/radareorg/radare2/archive/refs/tags/{pkgver}.tar.gz",
    ##f"https://github.com/wargio/r2dec-js/archive/refs/tags/{pkgver}-p1.tar.gz",
    ####f"https://github.com/radareorg/r2ghidra/archive/refs/tags/{pkgver}.tar.gz",
    "https://github.com/radareorg/r2ghidra/archive/a0119396b192fbe61cdc347ea91dea3e5590b6d6.tar.gz",
    "https://github.com/zeux/pugixml/archive/refs/tags/v1.11.3.tar.gz",
    "https://github.com/radareorg/ghidra-native/archive/refs/tags/0.5.0.tar.gz",
    ###"https://github.com/quickjs-ng/quickjs/archive/refs/tags/v0.8.0.tar.gz",
    #"https://github.com/radareorg/vector35-arch-arm64/archive/55d73c6bbb94448a5c615933179e73ac618cf876.tar.gz>vector35-arm64.tar.gz",
    #"https://github.com/radareorg/vector35-arch-armv7/archive/f270a6cc99644cb8e76055b6fa632b25abd26024.tar.gz>vector35-armv7.tar.gz",
]
source_paths = [
    ".",
    "third-party/pugixml",
    ##"subprojects/ghidra-native",
    "subprojects/packagecache/ghidra-native",
    ###"subprojects/libquickjs",
    #"vector35-arch-arm64",
    #"vector35-arch-armv7",
]
##source_paths = [
##    ".",
###    "shlr/capstone",
##]
sha256 = [
    ##"e45e4fd342f04b2e00363bc1b68cc375c1cf36041085d3d59caa7a3b7be43836",
    ##"af643d6f206d261fd0eaad04868dc240a75694b5edb21223fcdca94cd2c37234",
    ####"c414416d220e68eb532c91e3a225139345690ac78c46ecc236e76a3d451230f0",
    "5613a15224037ed713bd4e421596fcd94a263ed2101ecccb9d50ccd76b80d0bf",
    "3a215dd7bd9cecaf5edf690ac9045e8f83e4a865004f01b8f0a351a037a6ef06",
    "338f814db241e2de128f85f0556162289288aa12f8a20899af4e3ae051b9b80d",
    ###"7e60e1e0dcd07d25664331308a2f4aee2a88d60d85896e828d25df7c3d40204e",
    #"5d92d062bce1f2246afaf4f5063a8ce1244a2668938c6b5de89d896d294aab95",
    #"006f79e4b381f3d75763dc53ef94688fef247465c28f4814c2c112fbe1b25f2e",
]
tool_flags = {
    "CFLAGS": ["-D_GNU_SOURCE"],
##    "CFLAGS": ["-D_GNU_SOURCE", "-Wno-unaligned-access"],
##    "LDFLAGS": ["-Wl,-z,stack-size=2097152"],
}
# make check not implemented
options = [
    "!check",
    "!distlicense",
]

##if self.profile().arch == "x86_64":
##    makedepends += ["sysprof-capture"]
##    configure_args += ["--enable-stacktrace"]


def post_extract(self):
    # Move the unpacked vector35 sources into place
    ##self.mv("vector35-arch-arm64", f"libr/arch/p/arm/v35/arch-arm64")
    ##self.mv("vector35-arch-armv7", f"libr/arch/p/arm/v35/arch-armv7")
    ##self.cp("subprojects/packagefiles/libquickjs/meson.build", "subprojects/libquickjs/meson.build")
    pass


##def post_build(self):
##    self.ln_s("eustack", "build/src/stack")
##
##
##def post_install(self):
##    self.rename("usr/bin/eu-eustack", "eu-stack")


##@subpackage("elfutils-debuginfod")
##def _(self):
##    self.subdesc = "debuginfod"
##    # transitional
##    self.provides = [self.with_pkgver("debuginfod")]
##
##    return [
##        "usr/bin/debuginfod*",
##        "usr/share/man/man[18]/debuginfod*",
##    ]
##
##
##@subpackage("elfutils-debuginfod-libs")
##def _(self):
##    self.subdesc = "debuginfod library"
##    # transitional
##    self.provides = [self.with_pkgver("debuginfod-libs")]
##
##    return [
##        "etc/profile.d",
##        "usr/lib/libdebuginfod.so.*",
##        "usr/lib/libdebuginfod-*.so",
##    ]
##
##
##@subpackage("elfutils-libs")
##def _(self):
##    # since the resolved (after symlinks) filename of the .so is without
##    # a suffix, the automatic virtual version would be 0, which would
##    # prevent upgrades from elftoolchain (which had 1)
##    pv = pkgver[2:]
##    self.provides = [
##        self.with_pkgver("libelf"),  # transitional
##        f"so:libasm.so.1={pv}",  # allow for upgrade
##        f"so:libdw.so.1={pv}",
##        f"so:libelf.so.1={pv}",
##    ]
##
##    return self.default_libs(extra=[f"usr/lib/*-{pkgver}.so"])
##
##
##@subpackage("elfutils-devel")
##def _(self):
##    # transitional
##    self.provides = [self.with_pkgver("elftoolchain-devel")]
##
##    return self.default_devel()
