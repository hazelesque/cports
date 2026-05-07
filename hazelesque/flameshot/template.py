pkgname = "flameshot"
pkgver = "13.3.0"
pkgrel = 0
build_style = "cmake"
# Disable bundled KDSingleApplication so we use cports' system
# package; the bundled FetchContent path needs network during
# configure which cports' build phase doesn't allow.  Same logic
# would apply to Qt-Color-Widgets except it has no system
# alternative — we vendor it as a second source instead (below).
configure_args = [
    "-DUSE_BUNDLED_KDSINGLEAPPLICATION=OFF",
    "-DUSE_WAYLAND_CLIPBOARD=ON",
    # Disable phone-home update check by default; users on a
    # source-built distro pick their own update cadence via apk.
    "-DDISABLE_UPDATE_CHECKER=ON",
]
hostmakedepends = [
    "cmake",
    "ninja",
    "pkgconf",
    "qt6-qttools",
]
makedepends = [
    "kdsingleapplication-devel",
    # KF6GuiAddons is required by USE_WAYLAND_CLIPBOARD=ON for
    # the Wayland clipboard integration.
    "kguiaddons-devel",
    "qt6-qtbase-devel",
    "qt6-qtsvg-devel",
    "qt6-qttools-devel",
    "qt6-qtwayland-devel",
]
pkgdesc = "Powerful yet simple to use screenshot software"
license = "GPL-3.0-or-later"
url = "https://flameshot.org"
# Two sources: the flameshot release tarball, and a snapshot of
# Qt-Color-Widgets at the exact commit upstream's CMakeLists.txt
# pins via FetchContent.  We drop the second into
# external/Qt-Color-Widgets/ where flameshot's CMakeLists.txt
# checks for it before falling back to FetchContent.
source = [
    f"https://github.com/flameshot-org/flameshot/archive/refs/tags/v{pkgver}.tar.gz",
    "https://gitlab.com/mattbas/Qt-Color-Widgets/-/archive/352bc8f99bf2174d5724ee70623427aa31ddc26a/Qt-Color-Widgets-352bc8f99bf2174d5724ee70623427aa31ddc26a.tar.gz>qt-color-widgets.tar.gz",
]
source_paths = [
    ".",
    "external/Qt-Color-Widgets",
]
sha256 = [
    "bd1666313c875400e9588b47eb3fd2f4d0828460b3705a215b97746ea654c1b4",
    "fba0319194bd99649be6646f3f4c39d6b5467e3d0eceb0b8a53a48ae6b9fdcb2",
]
# `ctest` for flameshot needs a running display server.
options = ["!check"]
