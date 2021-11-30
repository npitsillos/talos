from discord.ext import commands
from talosbot.db_models import Comp
from talosbot.__version__ import __version__

class ManageCommandsMixin:

    def load_commands(self):
        bot = self

        @bot.group(hidden=True)
        @commands.has_role(bot.config.ADMIN_ROLE)
        async def manage(ctx):
            if ctx.invoked_subcommand is None:
                await ctx.send("Invalid command passed. Use !help.")

        @manage.command()
        async def version(ctx):
            """
                Displays bot current version
            """
            await ctx.send(f"TalosBot: v{__version__}")

        @manage.command()
        async def showconfig(ctx):
            """
                Shows bot config
            """
            await ctx.send(f"```{bot.config.__dict__}```")

        @manage.command()
        @commands.has_permissions(administrator=True)
        async def dropcomps(ctx):
            """
                Drops all competitions from database
            """
            Comp._mongometa.collection.drop()