pkgname = "r2mcp"
pkgver = "5.9.8"
pkgrel = 0
build_style = "makefile"
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
# autoreconf generates junk configure
make_env = {
##    "CS_ARCHIVE": "capstone/"
}
make_build_args = [
    "prefix=/usr",
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
make_install_args = ["prefix=/usr"]
##configure_gen = []
hostmakedepends = [
##    "bison",
##    "flex",
    "pkgconf",
]
makedepends = [
    "capstone-devel",
    "radare2",
##    "openssl3-devel",
##    "linux-headers",
##    "libpng-devel",
##    "argp-standalone",
##    "bzip2-devel",
##    "chimerautils-devel",
##    "json-c-devel",
##    "libarchive-devel",
##    "curl-devel",
##    "libmicrohttpd-devel",
##    "linux-headers",
##    "musl-bsd-headers",
##    "musl-obstack-devel",
##    "sqlite-devel",
##    "xz-devel",
##    "zlib-ng-compat-devel",
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
pkgdesc = "MCP server for using radare2 with AI assistants like Claude"
license = "MIT"
url = "https://github.com/radareorg/radare2-mcp"
source = [
    "https://github.com/radareorg/radare2-mcp/archive/ab57b65f803c4cf180c3216916900a9553691187.tar.gz",
]
source_paths = [
    ".",
]
##source_paths = [
##    ".",
###    "shlr/capstone",
##]
sha256 = [
    "73a3091c8474be4824f5b47065cb37914a1b4cbe5d7cf189d4e35c5580ad861d",
]
tool_flags = {
    "CFLAGS": [
        "-D_GNU_SOURCE",
	"-I/usr/include/libr",
	"-I/usr/include/capstone",
    ],
    "LDFLAGS": [
	"-lr_core",
	"-lm",
	"-lcapstone",
	"-lr_config",
	"-lr_debug",
	"-lr_bin",
	"-lr_lang",
	"-lr_anal",
	"-lr_bp",
	"-lr_egg",
	"-lr_asm",
	"-lr_flag",
	"-lr_search",
	"-lr_syscall",
	"-lr_fs",
	"-lr_io",
	"-lr_socket",
	"-lr_cons",
	"-lr_magic",
	"-lr_crypto",
	"-lr_arch",
	"-lr_esil",
	"-lr_reg",
	"-lr_util",
	"-ldl",
    ],
##    "CFLAGS": ["-D_GNU_SOURCE", "-Wno-unaligned-access"],
##    "LDFLAGS": ["-Wl,-z,stack-size=2097152"],
}
# make check not implemented
options = [
    "!check",
    "!distlicense",
]

