pkgname = "opensc"
pkgver = "0.27.1"
pkgrel = 0
build_style = "gnu_configure"
configure_args = [
    "--enable-openssl",
    "--enable-pcsc",
    "--enable-piv-sm",
    "--enable-readline",
    "--enable-sm",
    "--enable-zlib",
]
hostmakedepends = [
    "automake",
    "gettext",
    "libtool",
    "pkgconf",
]
makedepends = [
    "glib-devel",
    "openssl3-devel",
    "pcsc-lite-devel",
    "readline-devel",
    "zlib-ng-compat-devel",
]
checkdepends = ["bash"]
depends = ["pcsc-lite"]
pkgdesc = "Open source smart card tools and middleware"
license = "LGPL-2.1-or-later"
url = "https://github.com/OpenSC/OpenSC"
source = f"{url}/archive/refs/tags/{pkgver}.tar.gz"
sha256 = "9b72f1b5d92569de67a42bf0edb21ecdc685ad03378343416362a99b90b1fad1"
# Upstream builds with -Werror; too strict for distro packaging across
# compiler versions.  -U_FORTIFY_SOURCE matches Alpine's carry; some
# smartcard code paths trigger false positives with FORTIFY hardening.
tool_flags = {"CFLAGS": ["-U_FORTIFY_SOURCE", "-Wno-error"]}


def post_install(self):
    # Upstream installs bash completions to /etc/bash_completion.d
    # (the legacy location); Chimera's auto-bashcomp split takes from
    # /usr/share/bash-completion/completions.
    self.rename(
        "etc/bash_completion.d",
        "usr/share/bash-completion/completions",
        relative=False,
    )
    # Legacy compat symlinks for the pre-OpenSC-0.21 PKCS#11 module
    # naming; modern callers reference opensc-pkcs11.so directly.
    self.uninstall("usr/lib/onepin-opensc-pkcs11.so")
    self.uninstall("usr/lib/pkcs11/onepin-opensc-pkcs11.so")
    # npa-tool requires libeac/OpenPACE for the German nPA card; not
    # packaged in Chimera, so the binary isn't built — drop its
    # orphan completion to satisfy the bashcomp linter.
    self.uninstall("usr/share/bash-completion/completions/npa-tool")


@subpackage("opensc-libs")
def _(self):
    return self.default_libs()


@subpackage("opensc-devel")
def _(self):
    return self.default_devel()
