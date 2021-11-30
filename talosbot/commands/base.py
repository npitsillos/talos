import discord
import logging

from talosbot.db_models import Comp
from talosbot.helpers import get_team_entry_from_leaderboard

logger = logging.getLogger(__name__)

EXCLUDED_CHANNELS = ["information", "voice channels", "text channels", "cybrainers", "server-dev"]
FIELDS = ['teamId', 'teamName', 'submissionDate', 'score']

class BaseCommandsMixin:

    def load_commands(self):

        """
            Loads base commands to bot class
        """
        bot = self
        
        @bot.command()
        async def contribute(ctx):
            """
                Shows contribute link
            """
            await ctx.channel.send(f"Κάμε με πιο έξυπνο! {bot.config.GIT_REPO}")

        @bot.command(aliases=["ranking"])
        async def show_ranking(ctx):
            """
                Shows team's current ranking on Kaggle Competition (should be run within competition category)
            """
            category = ctx.channel.category.name
            
            if category.lower() in EXCLUDED_CHANNELS:
                await ctx.channel.send("Πάενε μες το κομπετίσιον ρεεε. Run this command in the competition category.")
            else:
                kaggle_cog = bot.get_cog("Competition")
                leaderboard_results = kaggle_cog.api.competition_leaderboard_view(category)
                if leaderboard_results:
                    comp = Comp.objects.get({"name": category})
                    team_ranking = get_team_entry_from_leaderboard(leaderboard_results, comp.team_name)
                    await ctx.channel.send("Πάμε καλά;;")
                    team_ranking_vals = {key: getattr(team_ranking, key) for key in FIELDS}
                    await ctx.channel.send(f"Place: {team_ranking_vals[FIELDS[0]]}, Last submission date: {team_ranking_vals[2]}, Score: {team_ranking_vals[FIELDS[3]]}")

        @bot.command()
        async def addteammate(ctx, team_mate:str):
            """
                Adds teammate to competition. (should be run within competition category)
            """
            category = ctx.channel.category.name
            
            if category.lower() in EXCLUDED_CHANNELS:
                await ctx.channel.send("Πάενε μες το κομπετίσιον ρεεε. Run this command in the competition category.")
            else:
                comp = Comp.objects.get({"name": category})
                comp.team_members.append(team_mate)
                comp.save()
                channels = ctx.channel.category.channels
                general = list(filter(lambda x: x.name == "general", channels))[0]
                user = None
                for guild in bot.guilds:
                    for member in guild.members:
                        if member.name == team_mate:
                            user = member
                            break
                await general.send(f"{user.mention} you have been added to {comp.name} by {ctx.message.author.mention}. Good luck!")