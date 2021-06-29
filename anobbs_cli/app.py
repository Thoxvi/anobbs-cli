import click
import json
import logging
import time
from anobbs_core import AppConstant
from anobbs_core.lib import BbsManager

logger = logging.getLogger(__name__)


def print_version(ctx, _, value):
    if not value or ctx.resilient_parsing:
        return

    click.echo(AppConstant.NAME)
    click.echo(AppConstant.VERSION)
    click.echo()
    ctx.exit(0)


def set_debug_level(debug: str) -> None:
    logging.basicConfig(level=logging.DEBUG if debug else logging.INFO,
                        format='%(asctime)s %(name)s %(levelname)s: %(message)s')


@click.command()
@click.option("--version",
              is_flag=True,
              callback=print_version,
              expose_value=False,
              is_eager=True)
@click.option("-d",
              "--debug",
              is_flag=True,
              help="Start debug mode")
@click.pass_context
def cli(
        ctx,
        debug,
):
    ctx.ensure_object(dict)
    set_debug_level(debug)

    exit(0)


if __name__ == '__main__':
    cli()
