pkgname = "squid-proxy"
pkgver = "6.14"
pkgrel = 5
build_style = "gnu_configure"
configure_args = [
    "--with-pidfile=/run/squid/squid.pid",
    "--with-logdir=/var/log/squid",
    "--enable-removal-policies=heap,lru",
##    "--disable-nls",
##    "--disable-werror",
##    "--enable-debuginfod",
##    "--enable-deterministic-archives",
##    "--enable-libdebuginfod",
##    "--with-zstd",
##    "--program-prefix=eu-",
]
# autoreconf generates junk configure
configure_gen = []
##hostmakedepends = [
##    "bison",
##    "flex",
##    "pkgconf",
##]
makedepends = [
    "autoconf",
    "automake",
    "libtool",
    "libtool-devel",
    "gawk",
    ##"ed", # ed is included in chimerautils
    "chimerautils",
    "cppunit",
    "cppunit-devel",
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
    "openssl3-devel",
    "openssl3-devel-static",
]
checkdepends = [
    "cppunit",
    "cppunit-devel",
    "cppunit-devel-static",
]
depends = [
##    "libpng",
    "openssl3-libs",
]
##checkdepends = ["bash"]
# transitional
##provides = [self.with_pkgver("elftoolchain")]
pkgdesc = "Full featured Web Proxy cache"
license = "GPL-3.0-or-later"
url = "https://www.nongnu.org/icoutils"
source = (
    "https://github.com/squid-cache/squid/archive/refs/tags/SQUID_6_14.tar.gz"
)
sha256 = "ed3207e0ca82a927ecc8b9ef2e1d4808c335f99dc34acafdd7ee6fcd301aebaf"
tool_flags = {
##    "CFLAGS": ["-D_GNU_SOURCE", "-Wno-unaligned-access"],
##    "LDFLAGS": ["-Wl,-z,stack-size=2097152"],
}

##if self.profile().arch == "x86_64":
##    makedepends += ["sysprof-capture"]
##    configure_args += ["--enable-stacktrace"]


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

# make check doesn't work - some nonsense about cppunit in a dummy test
options = [
    "!check",
    "!distlicense",
]

def post_extract(self):
    self.do("sh", "./bootstrap.sh")

def post_install(self):
    self.install_sysusers(self.files_path / "sysusers.conf")
    self.install_tmpfiles(self.files_path / "tmpfiles.conf")
    self.install_service(self.files_path / "squid")
