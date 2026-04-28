pkgname = "scip-go"
# Pinned to the last v0.1 series release.  v0.2.x bumped go.mod to
# `go 1.25.0`; chimera's main/go is currently 1.24.4 (2026-04-28).
# Bump pkgver once chimera ships go 1.25.
pkgver = "0.1.26"
pkgrel = 0
build_style = "go"
# `cmd/scip-go` is the only main package; restrict the build to it
# rather than `./...` (which would also pull in test helpers).
make_build_args = ["./cmd/scip-go"]
hostmakedepends = ["go"]
makedepends = []
depends = []
pkgdesc = "SCIP indexer for Go"
license = "Apache-2.0"
# v0.1.x lived under sourcegraph/, was forked to scip-code/ for v0.2.
# The tag still resolves under the new owner.
url = "https://github.com/scip-code/scip-go"
source = f"{url}/archive/refs/tags/v{pkgver}.tar.gz"
sha256 = "3e113fd1dfbb7516c932e60c9c5e6f2a3861113e0802a1c45669262d7c9aafaa"
# Tests fetch upstream test corpora from the network — bwrap-incompat.
options = ["!check"]
