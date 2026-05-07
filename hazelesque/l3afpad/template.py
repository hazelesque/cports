pkgname = "l3afpad"
pkgver = "0.8.18.1.11"
pkgrel = 0
build_style = "gnu_configure"
# l3afpad's vintage-2015 aclocal.m4 (specifically AM_GLIB_GNU_GETTEXT)
# hardcodes `localedir=${libdir}/locale` AFTER configure parses
# --localedir, so the configure-time override doesn't stick (the
# resulting Makefile shows `localedir = /usr/lib/locale` regardless).
# Modern XDG and cports' lint both want /usr/share/locale; override
# at `make install` time — make-line `localedir=` wins over the
# Makefile's own assignment.
make_install_args = ["localedir=/usr/share/locale"]
hostmakedepends = [
    "automake",
    "gettext",
    # gettext-devel ships the m4 macros (AM_NLS, AM_GNU_GETTEXT,
    # …) that intltool's configure.ac references via aclocal at
    # autoreconf time.  Without it, autoreconf fails with
    # "possibly undefined macro: AM_NLS".
    "gettext-devel",
    "intltool",
    "libtool",
    "pkgconf",
]
makedepends = [
    "gtk+3-devel",
]
pkgdesc = "Lightweight GTK3 text editor, fork of Leafpad"
license = "GPL-2.0-or-later"
url = "https://github.com/stevenhoneyman/l3afpad"
source = f"{url}/archive/refs/tags/v{pkgver}.tar.gz"
sha256 = "86f374b2f950b7c60dda50aa80a5034b8e3c80ded5cd3284c2d5921b31652793"
# No `make check` target in the upstream Makefile.  Disable the
# pixmaps lint because l3afpad's data/ ships its app icon as a
# legacy /usr/share/pixmaps/l3afpad.png; cports' lint prefers
# /usr/share/icons/ but installing a single PNG into a hicolor
# theme dir is more invasive than this 11 KB icon warrants.
options = ["!check", "!lintpixmaps"]
