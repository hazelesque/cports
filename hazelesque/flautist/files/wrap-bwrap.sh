#!/bin/sh
# wrap-bwrap.sh — bwrap sandbox launcher for `f7` (flautist CLI)
# instances.  Same shape + posture as withy's wrapper; see the
# rationale in hazelesque/withy/files/wrap-bwrap.sh.
#
# Usage:
#   wrap-bwrap.sh <DATA_DIR> <ETC_DIR> -- <f7-subcommand-and-args...>
#
# Difference from withy's wrapper: this one execs /usr/bin/f7
# instead of /usr/bin/wy.  Otherwise identical.

set -eu

if [ "$#" -lt 3 ]; then
    echo "usage: $0 DATA_DIR ETC_DIR -- <f7-subcommand-and-args...>" >&2
    exit 64
fi

DATA_DIR=$1
ETC_DIR=$2
shift 2

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
    /usr/bin/f7 "$@"
