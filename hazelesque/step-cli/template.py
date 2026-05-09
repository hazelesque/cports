pkgname = "step-cli"
pkgver = "0.30.2"
pkgrel = 0
build_style = "go"
make_build_args = ["./cmd/step"]
hostmakedepends = ["go"]
makedepends = []
depends = []
pkgdesc = (
    "Smallstep zero-trust swiss-army-knife CLI for certificates and identity"
)
license = "Apache-2.0"
url = "https://github.com/smallstep/cli"
# Use the release tarball rather than the github archive — the
# release bundle has the .VERSION file populated, so the binary's
# `step --version` reads the proper release string instead of "dev".
source = f"{url}/releases/download/v{pkgver}/step_{pkgver}.tar.gz"
sha256 = "db62a88ebec709de591dd86eec9759e15bdff4c6b96f3d7db6f53b6cf86bd3ec"
# `go test ./...` includes integration tests that bind ports and
# need a network; not appropriate for a sealed package build.
options = ["!check"]


def post_install(self):
    # Provides the `step` binary; cports' default go install drops
    # it under the build_artifact name from `make_build_args`.
    # Bash + zsh completions ship in autocomplete/.
    self.install_completion("autocomplete/bash_autocomplete", "bash", "step")
    self.install_completion("autocomplete/zsh_autocomplete", "zsh", "step")
