# Parallel-installable variant of main/musl that exports
# mimalloc's mi_* introspection API as dynamic symbols.
#
# Built from the same upstream sources as main/musl/ (verbatim
# patches + verbatim mimalloc.c shim).  Two deltas:
#
#   1. files/mimalloc-verify-syms.sh allows `mi_*` symbols to
#      escape mimalloc.o.  The `-fvisibility=hidden` on the
#      EXTRA_OBJ compile + mimalloc's `mi_decl_export = default`
#      annotation already give us the right visibility split
#      (public API exported, internals hidden) — the verify
#      script is just the gate that needs to be relaxed.
#
#   2. Install layout is fully contained under
#      /usr/lib/musl-mimalloc-introspectable/.  No files at /lib,
#      /usr/lib/libc.so*, or /usr/lib/ld-musl-*.  System musl
#      is untouched.  The variant loader is named
#      ld-musl-mimalloc-introspectable-<arch>.so.1 with matching
#      DT_SONAME so a binary that links against it cannot
#      silently fall back to system libc.
#
# Use case: a binary that wants to call mi_stats_print_out etc.
# at runtime can either dlopen() the variant libc directly or be
# built with `-Wl,--dynamic-linker=/usr/lib/musl-mimalloc-
# introspectable/lib/ld-musl-mimalloc-introspectable-<arch>.so.1`
# to use it as PT_INTERP.  In the latter case, mi_* are naked
# functions in the libc the consumer is loaded against.

pkgname = "musl-mimalloc-introspectable"
pkgver = "1.2.6"
pkgrel = 0
_commit = "9fa28ece75d8a2191de7c5bb53bed224c5947417"
_mimalloc_ver = "2.2.7"
build_style = "gnu_configure"
# All install paths under our variant prefix; nothing in /lib or
# /usr/lib root.  --syslibdir controls LDSO_PATHNAME (the
# PT_INTERP string baked into ldso/dlstart.lo).
_prefix = "/usr/lib/musl-mimalloc-introspectable"
configure_args = [
    f"--prefix={_prefix}",
    f"--libdir={_prefix}/lib",
    f"--syslibdir={_prefix}/lib",
    "--disable-gcc-wrapper",
    # Use external (mimalloc) allocator, NOT the default mallocng.
    # main/musl/template.py picks this conditionally on wordsize ==
    # 32; we only build x86_64/aarch64/etc. (64-bit), so external
    # is unconditional.  Without this, MALLOC_DIR stays "mallocng"
    # (the upstream default in Makefile) and mimalloc.o never gets
    # linked into libc.so, even though the EXTRA_OBJ rule still
    # builds it as an unused dependency.
    "--with-malloc=external",
]
configure_gen = []
make_build_args = [
    "EXTRA_OBJ=$(srcdir)/src/malloc/external/mimalloc.o",
    # Override LDSO_PATHNAME so PT_INTERP points at the renamed
    # loader name we install in post_install, not the default
    # ld-musl-<arch>.so.1.
    f"LDSO_PATHNAME={_prefix}/lib/ld-musl-mimalloc-introspectable-x86_64.so.1",
]
hostmakedepends = []
makedepends = []
depends = []
pkgdesc = "Parallel-installable musl with exported mimalloc introspection API"
license = "MIT"
url = "http://www.musl-libc.org"
# Verbatim source list from main/musl/.
source = [
    f"https://git.musl-libc.org/cgit/musl/snapshot/musl-{_commit}.tar.gz",
    f"https://github.com/microsoft/mimalloc/archive/refs/tags/v{_mimalloc_ver}.tar.gz",
]
source_paths = [".", "mimalloc"]
sha256 = [
    "d3baf222d234f2121e71b7eabd0c17667b7a3733b3077e99f9920c69cb5899df",
    "8e0ed89907a681276bff2e49e9a048b47ba51254ab60daf6b3c220acac456a95",
]
compression = "deflate"
# scp makes it segfault (inherited from main/musl).
hardening = ["!scp"]
# Tests upstream need a running musl; not appropriate for a
# package build.  No bootstrap option — this is a leaf, not a
# stage participant.  No LTO for the same reason main/musl skips
# it (CRT bits + dlstart need -fno-lto).
options = ["!check", "!lto"]


def post_extract(self):
    # libc.so --version reports this string.
    with open(self.cwd / "VERSION", "w") as f:
        f.write(pkgver)
    # Ship the mimalloc shim (verbatim from main/musl) and the
    # relaxed verify-syms script that allows mi_*.
    self.cp(self.files_path / "mimalloc-verify-syms.sh", ".")
    self.cp(self.files_path / "mimalloc.c", "mimalloc/src")
    # Same x86_64 memcpy/memmove asm-vs-C swap main/musl does
    # because the asm is slower in practice.
    self.rm("src/string/x86_64/memcpy.s")
    self.rm("src/string/x86_64/memmove.s")


def pre_install(self):
    self.install_dir(_prefix.lstrip("/") + "/lib")
    self.install_license("COPYRIGHT")


def post_install(self):
    libdir = self.destdir / _prefix.lstrip("/") / "lib"
    # Rename libc.so -> libc-mimalloc-introspectable.so.1.  The
    # DT_SONAME inside is already libc-mimalloc-introspectable.so.1
    # because the patches/libc-soname.patch sets it at link time
    # (cleaner than post-link patchelf, which added an extra
    # program header to fit the longer string and broke the
    # binary's static-PIE startup).
    new_libc = libdir / "libc-mimalloc-introspectable.so.1"
    (libdir / "libc.so").rename(new_libc)
    # Rename the loader file.  LDSO_PATHNAME above already baked
    # the new path into PT_INTERP at link time; this is just the
    # filesystem matching that string.  The original symlinking
    # logic in main/musl points ld-musl-<arch>.so.1 -> libc.so;
    # we do the equivalent for the variant, with the new name.
    for f in libdir.glob("ld-musl-*.so.1"):
        f.unlink()
    new_loader = libdir / "ld-musl-mimalloc-introspectable-x86_64.so.1"
    new_loader.symlink_to("libc-mimalloc-introspectable.so.1")
    # Drop static archive — consumers of this variant introspect
    # at runtime, they don't statically link against it.
    (libdir / "libc.a").unlink(missing_ok=True)
    # Drop everything not directly part of the runtime libc + ldso
    # pair: include/, bin/ (musl ships nothing in bin/ by default
    # via configure, but be defensive), share/, etc.
    for sub in ("include", "bin", "share", "etc", "var"):
        p = self.destdir / _prefix.lstrip("/") / sub
        if p.is_dir():
            self.rm(p, recursive=True)
