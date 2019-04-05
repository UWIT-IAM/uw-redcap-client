"""
A command-line interface to the Infectious Disease Data Distribution Center.
"""
import click
from typing import NoReturn


# Invoked by bin/id3c
@click.group(help = __doc__)
def cli() -> NoReturn:
    pass


# Load all top-level seattleflu.db.cli.command packages, giving them an
# opportunity to register their commands using @cli.command(…).
from .command import *


# Invoked via `python -m seattleflu.db.cli`.
if __name__ == "__main__":
    cli(prog_name = "id3c")
