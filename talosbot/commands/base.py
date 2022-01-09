import logging
import discord

from talosbot.helpers import get_competition_embed, chunkify
from talosbot.db_models import Comp

logger = logging.getLogger(__name__)


class BaseCommandsMixin:
    def load_commands(self):

        """
        Loads base commands to bot class
        """
        bot = self

        @bot.command()
        async def contribute(ctx):
            """
            Shows contribute link.
            """
            await ctx.channel.send(f"Κάμε με πιο έξυπνο! {bot.config.GIT_REPO}")

        @bot.command()
        async def showcomps(ctx, deadline_order=1, all=False):
            """
            Shows all competitions currently attempted by members of the server.
            By default does not display competitions with full teams.

            Parameters:
                deadline_order (int): whether to show deadline in ascending (1) or descending (-1) order
                all (bool): whether to show comps with full teams
            """
            comps = Comp.objects.all().order_by([("deadline", 1)])
            for comp in comps:
                if not all:
                    if len(comp.team_members) == comp.max_team_size:
                        continue
                comp_emb = get_competition_embed(
                    comp, ["team_name", "name", "deadline", "team_members"], title_field="name"
                )
                await ctx.channel.send(embed=comp_emb)

        @bot.command()
        async def join(ctx, comp_name):
            """
            Sends a request to join a team.

            Parameters:
                comp_name (str): competition name in slug format
            """

            comp = Comp.objects.get({"name": comp_name})
            if ctx.author.name not in comp.team_members:
                category = discord.utils.get(ctx.guild.categories, name=comp.name)
                general = discord.utils.get(category.channels, name="general")

                await general.send(f"{ctx.author.name} requests to join your team!")

                await ctx.author.send(f"Your request to join {comp.team_name} has been sent!")

        @showcomps.error
        @join.error
        async def join_error(ctx, error):
            if isinstance(error.original, Comp.DoesNotExist):
                await ctx.channel.send("Πάενε μες το κομπετίσιον ρεεε. Run this command in the competition category.")

        @bot.command()
        async def status(ctx):
            """
            Shows all ongoing, finished and archived competitions in the server.
            """

            comps = Comp.objects.all()

            comps = sorted([c for c in comps], key=lambda x: x.created_at)
            status_response = ""
            for comp in comps:
                comp_role = discord.utils.get(ctx.guild.roles, name=f"Comp-{comp.name}")
                status_response += comp.status()

            if len(status_response) == 0:
                await ctx.channel.send("No competitions in server!")
                return

            for chunk in chunkify(status_response, 1900):
                emb = discord.Embed(description=chunk, colour=4387968)
                await ctx.channel.send(embed=emb)
