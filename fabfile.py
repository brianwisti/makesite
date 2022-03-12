"""Define site management tasks."""

import os
from http.server import HTTPServer, SimpleHTTPRequestHandler

import rich
from invoke import task


def run(ctx, cmd):
    """Run a command with some default settings."""
    return ctx.run(cmd, pty=True, env=os.environ)


@task
def site(ctx):
    """Make the site."""
    run(ctx, "python makesite.py")


@task(pre=[site])
def serve(_):
    """Serve the site locally."""
    server_port = 8000
    site_dir = "_site"
    rich.print(f"Serving from {site_dir} on http://127.0.0.1:{server_port}")
    server_address = ("", server_port)
    os.chdir(site_dir)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    httpd.serve_forever()


@task
def setup(ctx):
    """Compile and sync requirements."""
    run(ctx, "pip-compile requirements.in > requirements.txt")
    run(ctx, "pip-sync requirements.txt")
    run(ctx, "pyenv rehash")


@task
def test(ctx, cov=False):
    """Run automated tests."""
    if cov:
        run(ctx, "pytest test --cov=makesite")
    else:
        run(ctx, "pytest test")
