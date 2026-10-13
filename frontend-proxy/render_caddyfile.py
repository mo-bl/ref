#!/usr/bin/env python3

"""Render the Caddyfile Jinja2 template from environment variables."""

import os
import re
import sys

import jinja2

OUTPUT = "/etc/caddy/Caddyfile"
# Mount points of the user-provided certificate in custom mode.
CUSTOM_CERT = "/etc/caddy/tls/cert.pem"
CUSTOM_KEY = "/etc/caddy/tls/key.pem"

# DOMAIN and HTTPS_HOST_PORT are interpolated into the Caddyfile; reject
# anything that could inject directives. Keep in sync with prepare.py.
HOSTNAME_RE = re.compile(
    r"^(?=.{1,253}$)[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?"
    r"(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)*$"
)


def main() -> None:
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader("/etc/caddy"),
        undefined=jinja2.StrictUndefined,
    )
    template = env.get_template("Caddyfile.prod.j2")

    tls_mode = os.environ.get("TLS_MODE", "off")
    if tls_mode not in ("off", "internal", "acme", "custom"):
        print(
            f"error: unknown TLS_MODE '{tls_mode}' (expected off|internal|acme|custom)",
            file=sys.stderr,
        )
        sys.exit(1)

    domain = os.environ.get("DOMAIN", "")
    if tls_mode in ("internal", "acme", "custom") and not domain:
        print(f"error: DOMAIN must be set when TLS_MODE={tls_mode}", file=sys.stderr)
        sys.exit(1)
    if domain and not HOSTNAME_RE.fullmatch(domain):
        print(f"error: DOMAIN {domain!r} is not a valid hostname", file=sys.stderr)
        sys.exit(1)

    https_host_port = os.environ.get("HTTPS_HOST_PORT", "8443")
    if (
        not https_host_port.isascii()
        or not https_host_port.isdigit()
        or not (1 <= int(https_host_port) <= 65535)
    ):
        print(f"error: invalid HTTPS_HOST_PORT {https_host_port!r}", file=sys.stderr)
        sys.exit(1)

    if tls_mode == "custom":
        for path in (CUSTOM_CERT, CUSTOM_KEY):
            if not os.path.isfile(path):
                print(
                    f"error: {path} is missing; TLS_MODE=custom needs the "
                    "certificate and key mounted (see tls.cert_file/key_file)",
                    file=sys.stderr,
                )
                sys.exit(1)

    context = {
        "tls_mode": tls_mode,
        "https_host_port": https_host_port,
        "domain": domain,
        "cert_file": CUSTOM_CERT,
        "key_file": CUSTOM_KEY,
        "redirect_http_to_https": os.environ.get(
            "REDIRECT_HTTP_TO_HTTPS", "false"
        ).lower()
        == "true",
    }

    with open(OUTPUT, "w") as f:
        f.write(template.render(context))

    print(f"Rendered Caddyfile (tls_mode={tls_mode})")


if __name__ == "__main__":
    main()
