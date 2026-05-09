pkgname = "step-ca"
pkgver = "0.30.2"
pkgrel = 0
build_style = "go"
make_build_args = ["./cmd/step-ca"]
hostmakedepends = [
    "go",
    # go-piv (smartcard / YubiKey CA support) shells out to
    # pkg-config to find PCSC headers; without it we get
    # `exec: "pkg-config": executable file not found in $PATH`.
    "pkgconf",
]
makedepends = [
    # PCSC dev headers for go-piv's cgo binding.  Same Alpine
    # step-certificates makedeps with `pcsc-lite-dev`.
    "pcsc-lite-devel",
]
# step-ca itself doesn't need step-cli at runtime, but the
# expected operator workflow (`step ca init`, `step ca bootstrap`,
# token issuance, …) goes through the step CLI.  Declaring it as
# a hard depend matches Alpine's step-certificates packaging and
# means `apk add step-ca` lands a complete CA toolkit.
depends = ["step-cli"]
pkgdesc = "Smallstep online certificate authority and ACME server"
license = "Apache-2.0"
url = "https://github.com/smallstep/certificates"
# Use the release tarball — same rationale as step-cli (.VERSION
# is populated so `step-ca version` reads correctly).
source = f"{url}/releases/download/v{pkgver}/step-ca_{pkgver}.tar.gz"
sha256 = "944b205d5ba89f393cbdc09d68ab7ce485f5b44f44c28025d30508af956c1cba"
# `go test ./...` pulls additional fixtures and bind-tests on
# port 443 / TPM simulator; not appropriate for a sealed package
# build.  Upstream CI is the right place for that.
options = ["!check"]
