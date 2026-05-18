#!/bin/sh
# wrap-bwrap.sh — bwrap sandbox launcher for `wy` instances.
#
# Used by both withy-{demo,staging}-{server,web} dinit services.
# Caller passes the per-instance data dir + etc dir + a `--`
# separator + the `wy` subcommand and its args:
#
#   wrap-bwrap.sh <DATA_DIR> <ETC_DIR> -- <wy-subcommand-and-args...>
#
# Hardening posture (in addition to the dinit `run-as` UID drop
# that happens BEFORE this script is exec'd):
#
#   --die-with-parent       — dinit goes away → so do we
#   --unshare-pid / -uts /  — isolated pid/uts/ipc/cgroup namespaces
#     -ipc / -cgroup-try
#   --new-session           — drop the controlling tty
#   --proc /proc            — fresh /proc inside the sandbox
#   --dev /dev              — bare-minimum /dev (no /dev/{kmsg,
#                             mem,…}); blocks ptrace-based escape
#                             vectors
#   --tmpfs /tmp            — ephemeral, isolated /tmp
#   --ro-bind /usr /usr     — system binaries + libs read-only
#   --ro-bind /etc/ssl      — system CA roots (rustls-native-certs
#                             reads them; harmless if unused)
#   --ro-bind $ETC_DIR      — instance's cert files (read-only)
#   --bind    $DATA_DIR     — instance's SQLite DB (read-write)
#
# What we deliberately DON'T do:
#
#   --unshare-net           Network access required (gRPC,
#                             outbound flautist subscribe).
#                             External firewall pins egress.
#   --unshare-user          Mapping inside is more trouble than
#                             it's worth here; dinit's run-as
#                             already drops privs.
#
# Inside the sandbox a compromised `wy` cannot: exec a shell (no
# /usr/bin/sh visible — actually /usr/bin is read-only, so it CAN
# exec it but cannot escape namespaces); persist (root fs is RO);
# read /home; touch /etc outside its own /etc/withy subdir; talk
# to /dev/kmsg or the kernel keyring; or escape its pid/uts/ipc
# namespaces via shared IDs.

set -eu

if [ "$#" -lt 3 ]; then
    echo "usage: $0 DATA_DIR ETC_DIR -- <wy-subcommand-and-args...>" >&2
    exit 64
fi

DATA_DIR=$1
ETC_DIR=$2
shift 2

# Allow either `wrap-bwrap.sh DATA ETC wy_arg1 wy_arg2 ...` or
# `wrap-bwrap.sh DATA ETC -- wy_arg1 wy_arg2 ...` for clarity.
[ "$1" = "--" ] && shift

exec /usr/bin/bwrap \
    --die-with-parent \
    --unshare-pid \
    --unshare-uts \
    --unshare-ipc \
    --unshare-cgroup-try \
    --new-session \
    --proc /proc \
    --dev /dev \
    --tmpfs /tmp \
    --ro-bind /usr /usr \
    --symlink usr/lib /lib \
    --symlink usr/lib /lib64 \
    --ro-bind /etc/ssl /etc/ssl \
    --ro-bind "$ETC_DIR" "$ETC_DIR" \
    --bind    "$DATA_DIR" "$DATA_DIR" \
    --setenv PATH /usr/bin \
    --setenv HOME "$DATA_DIR" \
    --chdir "$DATA_DIR" \
    -- \
    /usr/bin/wy "$@"
