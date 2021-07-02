import json
import logging
import time

import click

from anobbs_cli import AppConstant
from anobbs_cli.lib import ano_bbs_client
from imcli import VerticalLayout, Text, AnyStr

logger = logging.getLogger(__name__)


def format_time(timestamp: float) -> AnyStr:
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))


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


def create_floor_text(floor_data: dict) -> Text:
    return Text(
        f"No.{floor_data.get('no')}\n"
        f"Owner: {floor_data.get('owner_ac')}\n"
        f"Date: {format_time(floor_data.get('create_date'))}\n"
        f"\n"
        f"\t{floor_data.get('content')}\n",
        64,
        lr_padding=0,
        lr_margin=4,
        use_line_border=ano_bbs_client.config[ano_bbs_client.ConfigKeys.UI_USE_LINE_BORDER]
    )


def cli_query_group(page_size=50, page_index=1) -> bool:
    res = ano_bbs_client.query_group_with_pages(
        page_index=page_index,
        page_size=page_size
    )
    if res:
        group_pages = res["pages"]
        body = VerticalLayout([
            Text(
                f"No: {_page.get('first_floor', {}).get('no')}\n"
                f"ID: {_page.get('id')}\n"
                f"Owner: {_page.get('owner_ac')}\n"
                f"Date: {format_time(_page.get('update_date'))}\n"
                f"Count: {_page.get('floor_count')}\n"
                f"Topic: {_page.get('first_floor', {}).get('content')}\n\n",
                max_lenght=64,
                min_lenght=0,
                lr_padding=1,
                lr_margin=4,
                use_line_border=ano_bbs_client.config[ano_bbs_client.ConfigKeys.UI_USE_LINE_BORDER]
            )
            for _page
            in group_pages
        ])
        header = Text(
            f"Group name: {res['name']}\n" +
            f"Number of pages: {res['pages_count']}\n" +
            f"Range: {page_size * (page_index - 1)}-{min(res['pages_count'], page_size * page_index)}\n",
            max_lenght=128,
            min_lenght=0,
            lr_padding=1,
            lr_margin=1,
            use_line_border=False,
        )
        print(header.render())
        print()
        print(body.render())
        return True
    else:
        return False


def cli_query_page(page_id, page_size=20, page_index=1) -> bool:
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
        return True
    else:
        return False


def cli_query_account() -> bool:
    res = ano_bbs_client.query_account()
    if res:
        ac_list = res.get("ac_list")
        ic_list = res.get("ic_list")
        print(Text(
            f"ID: {res['id']}\n" +
            f"Birthday: {format_time(res['create_date'])}\n" +
            f"Ano Code ({len(ac_list)}/{res.get('max_ano_size')})\n" +
            f"\t- Unblocked\n" +
            f"\n".join([f"\t\t- {ac['id']}" for ac in ac_list if not ac['is_blocked']]) + "\n" +
            f"\t- Blocked\n" +
            f"\n".join([f"\t\t- {ac['id']}" for ac in ac_list if ac['is_blocked']]) + "\n" +
            f"Invitation Code\n" +
            f"\t- Unused\n" +
            f"\n".join([f"\t\t- {ic['id']}" for ic in ic_list if not ic['is_used']]) + "\n" +
            f"\t- Used\n" +
            f"\n".join([f"\t\t- {ic['id']}" for ic in ic_list if ic['is_used']]),
            max_lenght=256
        ).render())
        return True
    return False


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
    if cli_query_group(page_size, page_index):
        ctx.exit(0)
    else:
        ctx.exit(1)


@cli.command()
@click.argument(
    "page_id",
    type=click.STRING,
    autocompletion=lambda *args, **kwargs: ano_bbs_client.cache[ano_bbs_client.ConfigKeys.CACHE_PAGES],
)
@click.option("-p", "--page_index", default=1)
@click.option("--page_size", default=50)
@click.pass_context
def page(ctx, page_id, page_size, page_index):
    if cli_query_page(page_id, page_size, page_index):
        ctx.exit(0)
    else:
        ctx.exit(1)


@cli.command()
@click.argument("content")
@click.pass_context
def post(ctx, content):
    res = ano_bbs_client.post_page(content)
    if res:
        cli_query_page(res)
        ctx.exit(0)
    else:
        print("Post failed")
        ctx.exit(1)


@cli.command()
@click.argument(
    "page_id",
    type=click.STRING,
    autocompletion=lambda *args, **kwargs: ano_bbs_client.cache[ano_bbs_client.ConfigKeys.CACHE_PAGES],
)
@click.argument("content")
@click.pass_context
def append(ctx, page_id, content):
    res = ano_bbs_client.append_page(page_id, content)
    if res:
        print(create_floor_text(res).render())
        ctx.exit(0)
    else:
        ctx.exit(1)


@cli.command()
@click.pass_context
def account(ctx):
    if cli_query_account():
        ctx.exit(0)
    else:
        ctx.exit(1)


@cli.command()
@click.pass_context
def config(ctx):
    config_obj = ano_bbs_client.config
    print(json.dumps(config_obj, indent=2))
    ctx.exit(0)


@cli.command()
@click.pass_context
def check(ctx):
    config_obj = ano_bbs_client.config
    config_path = ano_bbs_client.DEFAULT_CONFIG_PATH.absolute()
    server_addr = config_obj[ano_bbs_client.ConfigKeys.ADDR]
    account_id = config_obj[ano_bbs_client.ConfigKeys.ACCOUNT]

    logger.info(f"User config file: {config_path}")
    logger.info(f"Config obj: \n{json.dumps(config_obj, indent=2)}")
    logger.info(f"Try to connect server: {server_addr}...")
    if not ano_bbs_client.hello_world():
        logger.error(
            f"There are some errors, \n"
            f"please check the address: {server_addr}\n"
            f"(or there are some problems in the server, Maybe you should ask the admin"
        )
        ctx.exit(1)
    logger.info("Connect server success!")
    logger.info("Try to login...")
    if not ano_bbs_client.login():
        if account_id:
            logger.error(
                f"Login failed, \n"
                f"please check the account id: {account_id}\n"
            )
        else:
            logger.error(f"You account id is empty!")
        ctx.exit(1)
    logger.info("Login success!")
    print()
    cli_query_account()
    ctx.exit(0)


@cli.command()
@click.pass_context
def create_ic(ctx):
    res = ano_bbs_client.create_ic()
    if res:
        print(f"New InvitationCode: {res}")
        ctx.exit(0)
    else:
        ctx.exit(1)


@cli.command()
@click.pass_context
def create_ac(ctx):
    res = ano_bbs_client.create_ac()
    if res:
        print(f"New AnoCode: {res}")
        ano_bbs_client.query_account()
        ctx.exit(0)
    else:
        ctx.exit(1)


@cli.command()
@click.argument("invitation_code")
@click.pass_context
def register(ctx, invitation_code):
    res = ano_bbs_client.create_account(invitation_code)
    if res:
        cli_query_account()
        ctx.exit(0)
    else:
        ctx.exit(1)


@cli.group()
@click.pass_context
def admin(_):
    pass


@admin.command()
@click.argument(
    "floor_no",
    type=click.STRING,
    autocompletion=lambda *args, **kwargs: ano_bbs_client.cache[ano_bbs_client.ConfigKeys.CACHE_NOS],
)
@click.pass_context
def block(ctx, floor_no):
    res = ano_bbs_client.block_ac_by_floor_no(floor_no)
    if res:
        print(f"Anocode blocked: {res}")
        ctx.exit(0)
    else:
        ctx.exit(1)


@admin.command()
@click.pass_context
def account_tree(ctx):
    res = ano_bbs_client.query_account_tree()
    if res:
        print(res)
        ctx.exit(0)
    else:
        ctx.exit(1)


if __name__ == '__main__':
    cli()
