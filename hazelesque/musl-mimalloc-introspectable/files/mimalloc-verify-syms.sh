#!/bin/sh
#
# Variant of main/musl/files/mimalloc-verify-syms.sh that also
# allows mimalloc's public introspection API (mi_*) to escape the
# .o file.  Used by hazelesque/musl-mimalloc-introspectable to
# build a parallel-installable libc whose mi_stats_*, mi_collect,
# mi_process_info, etc. show up in the dynamic symbol table.
#
# Internals (e.g. _mi_*-prefixed) remain gated by mimalloc's
# `mi_decl_export = visibility("default")` annotation — only the
# mimalloc.h public API has the visibility attribute, so internals
# stay -fvisibility=hidden as in the upstream main/musl build.
# This script is a redundant safety net on top of that visibility
# story, not the primary export-control mechanism.

nm "$1" | grep '[0-9A-Za-z] [A-Z] ' | while read -r addr type name; do
    case "$name" in
        # glue symbols (libc-internal allocator hooks)
        __libc_*|__malloc_*) ;;
        # compiler-generated
        .L*) ;;
        # directly provided api
        aligned_alloc|malloc_usable_size) ;;
        # mimalloc heaps (used by glue code in mimalloc.c)
        _mi_heap_empty|_mi_heap_main) ;;
        # mimalloc public API (allowed in this variant; rejected
        # by main/musl/files/mimalloc-verify-syms.sh)
        mi_*) ;;
        *)
            echo "unexpected symbol $name ($type)"
            exit 1
            ;;
    esac
done
