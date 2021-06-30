import logging

import click

from anobbs_cli import AppConstant
from anobbs_cli.lib import ano_bbs_client
from imcli import VerticalLayout, Text

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


def create_floor_text(floor: dict) -> Text:
    return Text(
        f"No.{floor.get('no')}\n"
        f"Owner: {floor.get('owner_ac')}\n"
        f"Date: {floor.get('create_date')}\n"
        f"\n"
        f"\t{floor.get('content')}\n",
        64,
        lr_padding=0,
        lr_margin=1,
    )


@click.group()
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


@cli.command()
@click.pass_context
def login(ctx):
    res = ano_bbs_client.login()
    if res:
        print(f"Login successful, token: {res}")
        ctx.exit(0)
    else:
        print(f"Login failed, please check your account id.")
        ctx.exit(1)


@cli.command()
@click.option("--page_size", default=30)
@click.option("-p", "--page_index", default=1)
@click.pass_context
def pages(ctx, page_size, page_index):
    res = ano_bbs_client.query_group_with_pages(
        page_index=page_index,
        page_size=page_size
    )
    if res:
        header = Text(
            f"Group name: {res['name']}\n"
            f"Number of pages: {res['pages_count']}\n"
            f"Range: {page_size * (page_index - 1)}-{min(res['pages_count'] - 1, page_size * page_index)}",
            max_lenght=128,
            min_lenght=128,
            lr_padding=0,
            use_line_border=False,
        )
        body = VerticalLayout([
            Text(
                f"ID: {_page.get('id')}\n"
                f"Owner: {_page.get('owner_ac')}\n"
                f"Date: {_page.get('update_date')}\n"
                f"Topic: {_page.get('first_floor', {}).get('content')}",
                max_lenght=64,
                min_lenght=64,
                lr_padding=1,
                lr_margin=1,
            )
            for _page
            in res["pages"]
        ])
        print(header.render())
        print(body.render())

        ctx.exit(0)
    else:
        ctx.exit(1)


@cli.command()
@click.argument("page_id")
@click.option("-p", "--page_index", default=1)
@click.option("--page_size", default=50)
@click.pass_context
def page(ctx, page_id, page_size, page_index):
    res = ano_bbs_client.query_page_with_floor(page_id, page_size, page_index)
    if res:
        floors = res["floors"]
        header = Text(
            f"ID: {res['id']}\n"
            f"Topic: {floors[0]['content']}\n"
            f"Number of floors: {res['floors_count']}\n"
            f"Range: {page_size * (page_index - 1)}-{min(res['floors_count'] - 1, page_size * page_index)}",
            128,
            use_line_border=False,
            lr_padding=0,
        )
        body = VerticalLayout([
            create_floor_text(floor)
            for floor
            in floors
        ])
        print(header.render())
        print()
        print(body.render())
        ctx.exit(0)
    else:
        ctx.exit(1)


@cli.command()
@click.argument("content")
@click.pass_context
def post(ctx, content):
    res = ano_bbs_client.post_page(content)
    if res:
        print(f"Page ID: {res}")
        ctx.exit(0)
    else:
        ctx.exit(1)


@cli.command()
@click.argument("page_id")
@click.argument("content")
@click.pass_context
def append(ctx, page_id, content):
    res = ano_bbs_client.append_page(page_id, content)
    if res:
        print(create_floor_text(res).render())
        ctx.exit(0)
    else:
        ctx.exit(1)


if __name__ == '__main__':
    cli()
