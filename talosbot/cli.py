import os
import click
import logging

from pymodm import connect
from dotenv import load_dotenv
from collections import defaultdict
from talosbot.__main__ import launch
from talosbot.__version__ import __version__
from pymongo.errors import ServerSelectionTimeoutError

from texttable import Texttable

load_dotenv(dotenv_path=os.path.join(os.getcwd(), ".env"))

from talosbot.config import bot_config


def draw_options_table(options):
    table = Texttable()
    table.set_deco(Texttable.VLINES | Texttable.HEADER | Texttable.HLINES)
    table.set_cols_dtype(["a", "a"])  # automatic
    table.set_cols_align(["l", "l"])
    table.add_rows(
        [
            ["name", "value"],
            *[[name, val] for name, val in options],
        ]
    )
    return table.draw()


@click.group()
@click.option("--env", default="prod", help="Which environment to use")
@click.pass_context
def cli(ctx, env):
    ctx.ensure_object(dict)
    ctx.obj["env"] = env


@cli.command()
@click.pass_context
def config(ctx):
    """Shows current bot config (Requires DB connection)."""
    try:
        config_cls = bot_config[ctx.obj.get("env")]
        connect(config_cls.DB_URL)
        config = config_cls()
    except ServerSelectionTimeoutError:
        logging.error(
            "Database timeout error! Make use an instance of mongodb is running and your OVISBOT_DB_URL env variable is valid! Terminating... "
        )
        exit(1)

    click.echo(
        # config._load_static_props()
        draw_options_table(
            #     chain(
            #         config._get_configurable_props_from_cls(),
            config._get_static_props_from_cls(),
            #     )
        )
    )


@cli.command()
@click.pass_context
def setupenv(ctx):
    """
    Sets up environment variables for bot
    """
    config_cls = bot_config[ctx.obj["env"]]
    env = defaultdict(str)
    for attr in dir(config_cls):
        if attr.isupper():
            default_val = getattr(config_cls, attr)
            value = click.prompt(f"Provide the value for TALOSBOT_{attr}", default=default_val)
            value = value or default_val
            env[attr] = value

    ROOT_DIR = os.path.abspath(os.curdir)

    with open(os.path.join(ROOT_DIR, ".env"), "w") as f:
        for key, value in env.items():
            if value is not None:
                env_var = f"TALOSBOT_{key}={value}" if "KAGGLE" not in key else f"{key}={value}"
                f.write(f"{env_var}\n")


@cli.command()
def run():
    """
    Launches bot
    """
    launch()


@cli.command()
def version():
    """
    Displays bot version
    """
    click.echo(f"TalosBot v{__version__}")
