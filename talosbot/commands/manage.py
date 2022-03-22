import discord

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
            comps = Comp.objects.all()
            if comps.count() > 0:
                names = [comp.name for comp in comps]
                for name in names:
                    drop_cmd = bot.get_command("manage dropcomp")
                    await ctx.invoke(drop_cmd, name)
            else:
                await ctx.channel.send("There are no competitions stored in the DB")

        @manage.command()
        @commands.has_permissions(administrator=True)
        async def dropcomp(ctx, name):
            comp = Comp.objects.get({"name": name})
            category = discord.utils.get(ctx.guild.categories, name=name)
            
            comp_role = discord.utils.get(ctx.guild.roles, name=f"Comp-{name}")

            if comp_role is not None:
                await comp_role.delete()
            for c in category.channels:
                await c.delete()

            await category.delete()
            comp.delete()

        @manage.command()
        async def showcomps(ctx):
            comps = Comp.objects.all()
            if comps.count() > 0:
                for comp in comps:
                    await ctx.channel.send(comp.name)
            else:
                await ctx.channel.send("There are no competitions stored in the DB")
