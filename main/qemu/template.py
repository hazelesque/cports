pkgname = "qemu"
pkgver = "11.0.1"
pkgrel = 2
build_style = "gnu_configure"
# TODO vde
configure_args = [
    "--enable-bpf",
    "--enable-cap-ng",
    "--enable-capstone",
    "--enable-curl",
    "--enable-curses",
    "--enable-dbus-display",
    "--enable-docs",
    "--enable-gtk",
    "--enable-guest-agent",
    "--enable-jack",
    "--enable-kvm",
    "--enable-libdw",
    "--enable-libnfs",
    "--enable-libssh",
    "--enable-linux-aio",
    "--enable-linux-io-uring",
    "--enable-lzo",
    "--enable-numa",
    "--enable-pie",
    "--enable-sdl",
    "--enable-seccomp",
    "--enable-snappy",
    "--enable-system",
    "--enable-tpm",
    "--enable-usb-redir",
    "--enable-vhost-net",
    "--enable-virglrenderer",
    "--enable-virtfs",
    "--enable-vnc",
    "--enable-vnc-jpeg",
    "--enable-zstd",
    "--disable-bsd-user",
    "--disable-debug-info",
    "--disable-glusterfs",
    "--disable-linux-user",
    "--disable-oss",
    "--disable-werror",
    "--disable-xen",
    "--audio-drv-list=pa,pipewire,jack,sdl",
]
# actually meson
configure_gen = []
hostmakedepends = [
    "bash",
    "bison",
    "bzip2",
    "flex",
    "gettext",
    "meson",
    "ninja",
    "perl",
    "pkgconf",
    "python-sphinx",
    "python-sphinx_rtd_theme",
]
makedepends = [
    "bzip2-devel",
    "capstone-devel",
    "curl-devel",
    "dinit-chimera",
    "dtc-devel",
    "elfutils-devel",
    "fuse-devel",
    "glib-devel",
    "gnutls-devel",
    "gtk+3-devel",
    "keyutils-devel",
    "libaio-devel",
    "libbpf-devel",
    "libcacard-devel",
    "libcap-ng-devel",
    "libcbor-devel",
    "libdrm-devel",
    "libiscsi-devel",
    "libjpeg-turbo-devel",
    "libnfs-devel",
    "libpulse-devel",
    "libsasl-devel",
    "libseccomp-devel",
    "libslirp-devel",
    "libssh-devel",
    "liburing-devel",
    "libusb-devel",
    "linux-headers",
    "linux-pam-devel",
    "lzo-devel",
    "ncurses-devel",
    "nss-devel",
    "numactl-devel",
    "pcsc-lite-devel",
    "pipewire-devel",
    "pipewire-jack-devel",
    "pixman-devel",
    "sdl2-compat-devel",
    "sdl2_image-devel",
    "snappy-devel",
    "usbredir-devel",
    "virglrenderer-devel",
    "vte-gtk3-devel",
    "zlib-ng-compat-devel",
    "zstd-devel",
]
pkgdesc = "Generic machine emulator and virtualizer"
license = "GPL-2.0-only AND LGPL-2.1-only"
url = "https://qemu.org"
source = f"https://download.qemu.org/qemu-{pkgver}.tar.xz"
sha256 = "0d235f5820278d914a3155ec27af8e4258d697ea892895570807d69c0cb8cd64"
tool_flags = {
    # see libbpf comment about bpf headers
    "CFLAGS": ["-I/usr/include/bpf/uapi"],
    "CXXFLAGS": ["-I/usr/include/bpf/uapi"],
}
file_modes = {
    "usr/lib/qemu-bridge-helper": ("root", "root", 0o4755),
}
# there are integer overflows all over the emulator
hardening = ["!int"]
# maybe someday
options = ["!cross", "!check"]

if self.profile().endian == "little":
    configure_args += ["--enable-spice"]
    makedepends += ["spice-devel", "spice-protocol"]
else:
    configure_args += ["--disable-spice"]

if self.profile().wordsize == 32:
    broken = "not supported anymore"


def init_configure(self):
    ljobs = 4 if self.make_jobs >= 4 else self.make_jobs
    # qemu links a lot of big exes at once so ensure there is not more than four
    self.configure_args += [f"-Dbackend_max_links={ljobs}"]


def post_install(self):
    self.install_service(self.files_path / "qemu-ga")

    # no elf files in /usr/share
    self.rename("usr/share/qemu", "usr/lib/qemu", relative=False)
    self.install_link("usr/share/qemu", "../lib/qemu")

    self.install_tmpfiles(self.files_path / "tmpfiles.conf")
    self.install_sysusers(self.files_path / "qemu.conf")
    self.install_file(self.files_path / "80-kvm.rules", "usr/lib/udev/rules.d")
    self.install_file(self.files_path / "bridge.conf", "usr/lib/qemu")

    self.uninstall("usr/share/doc")

    if self.profile().wordsize == 32:
        self.uninstall("usr/lib/qemu/palcode-clipper")
        self.uninstall("usr/lib/qemu/hppa-firmware.img")
        self.uninstall("usr/lib/qemu/hppa-firmware64.img")
        self.uninstall("usr/lib/qemu/opensbi-riscv64-generic-fw_dynamic.bin")
        self.uninstall("usr/lib/qemu/s390-ccw.img")
        self.uninstall("usr/lib/qemu/openbios-sparc64")

    # Generate qcow2 pflash siblings (both the read-only code and
    # the writable vars template) alongside the raw .fd originals so
    # libvirt's auto-firmware can serve `<nvram format='qcow2'/>`
    # requests. Internal qcow2 snapshots of UEFI guests require all
    # pflash files to be qcow2 (the libvirt error against raw pflash
    # is "internal snapshots of a VM with pflash based firmware
    # require QCOW2 nvram format").
    #
    # **Both code and vars need re-encoding.** libvirt's matcher
    # (`qemuFirmwareMatchDomain` in src/qemu/qemu_firmware.c) treats
    # the loader/executable and the nvram-template as a single
    # "flash" pair and rejects descriptors with mismatched formats
    # — "Discarding loader with mismatching flash format 'raw' !=
    # 'qcow2'" — even when the domain XML only constrains the
    # nvram side. So shipping qcow2 vars alongside raw code is
    # insufficient on its own; the code has to come along too.
    #
    # The raw .fd files stay in place untouched — same-content
    # re-encoding, no functional change for guests not opting into
    # qcow2.
    fw = self.chroot_destdir / "usr/lib/qemu"
    for stem in (
        # Read-only code blobs:
        "edk2-i386-code",
        "edk2-i386-secure-code",
        "edk2-x86_64-code",
        "edk2-x86_64-secure-code",
        "edk2-aarch64-code",
        "edk2-arm-code",
        "edk2-loongarch64-code",
        "edk2-riscv-code",
        # Writable NVRAM templates:
        "edk2-i386-vars",
        "edk2-arm-vars",
        "edk2-loongarch64-vars",
        "edk2-riscv-vars",
    ):
        # Skip variants that didn't get installed for this profile
        # (e.g. 32-bit hosts where some arches are pruned above).
        if not (self.destdir / "usr/lib/qemu" / f"{stem}.fd").exists():
            continue
        self.do(
            self.chroot_cwd / "build/qemu-img",
            "convert",
            "-f",
            "raw",
            "-O",
            "qcow2",
            fw / f"{stem}.fd",
            fw / f"{stem}.qcow2",
        )

    # Sibling firmware descriptors pointing at the qcow2 vars
    # templates. Numbering preserves precedence: 55- pairs with the
    # existing 50- secure-boot descriptors, 65- pairs with the
    # non-secure 60- ones. Default-format `<nvram>` requests still
    # match the existing raw descriptors first (lexicographic
    # iteration); qcow2 entries only match when an XML explicitly
    # requests `<nvram format='qcow2'/>`. See
    # https://libvirt.org/formatdomain.html#bios-bootloader for
    # libvirt's auto-firmware selection algorithm.
    for descriptor in (
        "55-edk2-i386-secure-qcow2.json",
        "55-edk2-x86_64-secure-qcow2.json",
        "65-edk2-aarch64-qcow2.json",
        "65-edk2-arm-qcow2.json",
        "65-edk2-i386-qcow2.json",
        "65-edk2-loongarch64-qcow2.json",
        "65-edk2-riscv64-qcow2.json",
        "65-edk2-x86_64-qcow2.json",
    ):
        self.install_file(
            self.files_path / descriptor,
            "usr/lib/qemu/firmware",
        )


@subpackage("qemu-guest-agent")
def _(self):
    self.pkgdesc = "QEMU guest agent"
    self.depends = []

    return [
        "usr/lib/dinit.d/qemu-ga",
        "usr/bin/qemu-ga",
    ]


@subpackage("qemu-img")
def _(self):
    self.pkgdesc = "QEMU command line tools for manipulating disk images"
    self.depends = []

    return [
        "usr/bin/qemu-img",
        "usr/bin/qemu-io",
        "usr/bin/qemu-nbd",
        "usr/bin/qemu-storage-daemon",
    ]


@subpackage("qemu-tools")
def _(self):
    self.pkgdesc = "QEMU support tools"
    self.depends = []

    return [
        "usr/bin/qemu-edid",
        "usr/bin/qemu-keymap",
        "usr/bin/elf2dmp",
    ]


@subpackage("qemu-pr-helper")
def _(self):
    self.pkgdesc = "QEMU pr helper utility"
    self.depends = []

    return [
        "usr/bin/qemu-pr-helper",
        "usr/share/man/man8/qemu-pr-helper.8",
    ]


@subpackage("qemu-vhost-user-gpu")
def _(self):
    self.pkgdesc = "QEMU vhost user GPU device"
    self.depends = []

    return [
        "usr/lib/vhost-user-gpu",
        "usr/lib/qemu/vhost-user/50-qemu-gpu.json",
    ]


@subpackage("qemu-edk2-firmware")
def _(self):
    self.pkgdesc = "QEMU edk2 firmware files"
    self.depends = []

    return [
        "usr/lib/qemu/firmware",
        "usr/lib/qemu/edk2*",
    ]


def _spkg(sname, wordsize):
    do_epkg = True

    if self.profile().wordsize == 32 and wordsize == 64:
        do_epkg = False

    @subpackage(f"qemu-system-{sname}", do_epkg)
    def _(self):
        self.subdesc = f"system-{sname}"
        self.depends = [self.parent]
        self.options = ["foreignelf"]

        extras = []

        match sname:
            case "aarch64":
                self.depends += [self.with_pkgver("qemu-edk2-firmware")]
            case "alpha":
                extras = ["usr/lib/qemu/palcode-clipper"]
            case "arm":
                self.depends += [self.with_pkgver("qemu-edk2-firmware")]
                extras = [
                    "usr/lib/qemu/npcm7xx_bootrom.bin",
                ]
            case "hppa":
                extras = [
                    "usr/lib/qemu/hppa-firmware.img",
                    "usr/lib/qemu/hppa-firmware64.img",
                ]
                self.options += ["execstack"]
            case "i386":
                self.depends += [self.with_pkgver("qemu-edk2-firmware")]
            case "ppc":
                extras = [
                    "usr/lib/qemu/openbios-ppc",
                    "usr/lib/qemu/u-boot.e500",
                    "usr/lib/qemu/u-boot-sam460.bin",
                ]
                self.options += ["execstack"]
            case "riscv32":
                extras = [
                    "usr/lib/qemu/opensbi-riscv32-generic-fw_dynamic.bin",
                ]
            case "riscv64":
                extras = [
                    "usr/lib/qemu/opensbi-riscv64-generic-fw_dynamic.bin",
                ]
            case "s390x":
                extras = [
                    "usr/lib/qemu/s390-ccw.img",
                ]
                self.options += ["execstack", "textrels"]
            case "sparc":
                extras = [
                    "usr/lib/qemu/openbios-sparc32",
                ]
                self.options += ["execstack"]
            case "sparc64":
                extras = [
                    "usr/lib/qemu/openbios-sparc64",
                ]
                self.options += ["execstack"]
            case "x86_64":
                self.depends += [self.with_pkgver("qemu-edk2-firmware")]

        # never strip them
        self.nostrip_files = extras

        return [f"usr/bin/qemu-system-{sname}", *extras]


for _sys, _ws in [
    ("aarch64", 64),
    ("alpha", 64),
    ("arm", 32),
    ("avr", 32),
    ("hppa", 64),
    ("i386", 32),
    ("loongarch64", 64),
    ("m68k", 32),
    ("microblaze", 64),
    ("mips", 32),
    ("mips64", 64),
    ("mips64el", 64),
    ("mipsel", 32),
    ("or1k", 32),
    ("ppc", 32),
    ("ppc64", 64),
    ("riscv32", 32),
    ("riscv64", 64),
    ("rx", 32),
    ("s390x", 64),
    ("sh4", 32),
    ("sh4eb", 32),
    ("sparc", 32),
    ("sparc64", 64),
    ("tricore", 32),
    ("x86_64", 64),
    ("xtensa", 32),
    ("xtensaeb", 32),
]:
    _spkg(_sys, _ws)
