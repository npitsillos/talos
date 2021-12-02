import logging
import discord
import datetime

from typing import Optional
from difflib import SequenceMatcher
from talosbot.db_models import Comp
from discord.ext import commands, tasks
from talosbot.helpers import get_team_entry_from_leaderboard
from kaggle.api.kaggle_api_extended import KaggleApi
from talosbot.exceptions import (
    InvalidCategoryException,
    CompetitionAlreadyExistsException,
    CompetitionAlreadyFinishedException,
    NotInCompCategoryException,
    TeamAlreadyHasNameException,
)

logger = logging.getLogger(__name__)

CATEGORIES = ["featured", "research", "recruitment", "gettingStarted", "masters", "playground"]
EMOJIS = {
    "question": ":question:",
    "right": ":point_right:",
    "calendar": ":calendar:",
    "worried": ":worried:",
    "tada": ":tada:",
}
FIELDS = ["teamId", "teamName", "submissionDate", "score"]


class Competition(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.init_api_client()

    def init_api_client(self):
        self.api = KaggleApi()
        self.api.authenticate()

    def _get_competition_embed(self, comp):
        comp_desc = comp["description"]
        reward = comp["reward"]
        deadline = comp["deadline"].strftime("%d/%m/%y")
        description = (
            f"{EMOJIS['question']} {comp_desc}\n"
            f"{EMOJIS['right']} Reward: {reward}\n"
            f"{EMOJIS['calendar']} Deadline: {deadline}"
        )
        emb = discord.Embed(title=comp["title"], description=description, url=comp["url"], colour=4387968)
        return emb

    @commands.group()
    async def comp(self, ctx):
        """
        Collection of commands for interacting with Kaggle
        """
        self.guild = ctx.guild
        self.gid = ctx.guild.id

        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid command passed. Use !help.")

    @comp.command()
    async def list(self, ctx, cat="featured", num=5):
        """
        List competitions sorted by latest deadline. Returns
        competitions from all categories and only lists the first 5
        by default.

        Parameters:
            cat (str): category to filter by [featured|research|recruitment|gettingStarted|masters|playground]
            num (int): how many results to display
        """
        if cat.lower() not in CATEGORIES:
            raise InvalidCategoryException

        comps = self.api.competitions_list(category="featured")
        latest_comps = [comp.__dict__ for comp in comps[:num]]
        for latest_comp in latest_comps:
            emb = self._get_competition_embed(latest_comp)
            await ctx.channel.send(embed=emb)

    @comp.error
    async def comps_error(self, ctx, error):
        if isinstance(error.original, InvalidCategoryException):
            await ctx.channel.send("The specified category is not supported")

    @comp.command()
    async def create(self, ctx, comp_name, team_name: Optional[str] = " "):
        """
        Create a competition given a name.

        Parameters:
            comp_name (str): name of the competition to find and create in lowercase and slug, eg comp-name
            team_name (str): optional string to add as team name
        """

        logger.info(comp_name)
        comps = self.api.competitions_list(sort_by="latestDeadline")
        latest_comps = [comp.__dict__ for comp in comps]

        max_longest_match = 0
        matched_comp = None
        for latest_comp in latest_comps:
            matcher = SequenceMatcher(None, comp_name, latest_comp["ref"])
            longest_match = matcher.find_longest_match(0, len(comp_name), 0, len(latest_comp["title"])).size
            if longest_match > max_longest_match:
                max_longest_match = longest_match
                matched_comp = latest_comp

        if matched_comp:
            category = discord.utils.get(ctx.guild.categories, name=matched_comp["ref"])

            if category is not None:
                raise CompetitionAlreadyExistsException

            comp_role = await self.guild.create_role(name=f"Comp-{matched_comp['ref']}", mentionable=True)
            await ctx.message.author.add_roles(comp_role)
            overwrites = {
                # Everyone
                self.guild.get_role(self.gid): discord.PermissionOverwrite(read_messages=False),
                self.bot.user: discord.PermissionOverwrite(read_messages=True),
                comp_role: discord.PermissionOverwrite(read_messages=True),
            }

            category = await self.guild.create_category(name=matched_comp["ref"], overwrites=overwrites)
            general_channel = await self.guild.create_text_channel(name="general", category=category)

            Comp(
                name=category,
                url=matched_comp["url"],
                created_at=datetime.datetime.now(),
                deadline=matched_comp["deadline"],
                team_name=team_name,
                max_team_size=matched_comp["maxTeamSize"],
                max_daily_subs=matched_comp["maxDailySubmissions"],
                merger_deadline=matched_comp["mergerDeadline"],
            ).save()

            await general_channel.send("@here New competition created! @here Άτε κοπέλια..!")
        else:
            await ctx.channel.send("Νομίζω έφηε σου το όνομα! Use !comp list to see a list.")

    @create.error
    async def create_error(self, ctx, error):
        if isinstance(error.original, CompetitionAlreadyExistsException):
            await ctx.channel.send("Ρεεεε τούτο το κομπετίσιον υπάρχει!!")

    @comp.command(aliases=["ranking"])
    async def show_ranking(self, ctx):
        """
        Shows team's current ranking on Kaggle Competition (should be run within competition category)
        """
        category = ctx.channel.category.name
        comp = Comp.objects.get({"name": category})
        if comp is None:
            raise NotInCompCategoryException
        else:
            leaderboard_results = self.api.competition_leaderboard_view(category)
            if leaderboard_results:
                comp = Comp.objects.get({"name": category})
                team_ranking = get_team_entry_from_leaderboard(leaderboard_results, comp.team_name)
                await ctx.channel.send("Πάμε καλά;;")
                team_ranking_vals = {key: getattr(team_ranking, key) for key in FIELDS}
                await ctx.channel.send(
                    f"Place: {team_ranking_vals[FIELDS[0]]}, Last submission date: {team_ranking_vals[2]}, Score: {team_ranking_vals[FIELDS[3]]}"
                )

    @show_ranking.error
    async def show_ranking_error(self, ctx, error):
        if isinstance(error.original, NotInCompCategoryException):
            await ctx.channel.send("Πάενε μες το κομπετίσιον ρεεε. Run this command in the competition category.")

    @comp.command()
    async def addteammate(self, ctx, team_mate: str):
        """
        Adds teammate to competition. (should be run within competition category)

        Parameters:
            team_mate (str): discord username of teammate to add
        """

        category = ctx.channel.category.name
        comp = Comp.objects.get({"name": category})
        if comp is None:
            raise NotInCompCategoryException
        else:
            comp = Comp.objects.get({"name": category})
            if team_mate in comp.team_members:
                await ctx.channel.send(f"{team_mate} is already a member of the competition's team")
            else:
                if len(comp.team_members) < comp.max_team_size:
                    comp.team_members.append(team_mate)
                    comp.save()
                    general = discord.utils.get(ctx.channel.category.channels, name="general")
                    user = None
                    for guild in self.bot.guilds:
                        for member in guild.members:
                            if member.name == team_mate:
                                user = member
                                break
                    if user:
                        comp_role = discord.utils.get(ctx.guild.roles, name=f"Comp-{category}")
                        await user.add_roles(comp_role)
                        await general.send(
                            f"{user.mention} you have been added to {comp.name} by {ctx.message.author.mention}. Good luck!"
                        )
                    else:
                        await ctx.channel.send("Ένηβρα έτσι παίχτη... User not found!")
                else:
                    await ctx.channel.send(f"Team is already at maximum capacity... {EMOJIS['worried']}")

    @addteammate.error
    async def addteammate_error(self, ctx, error):
        if isinstance(error.original, NotInCompCategoryException):
            await ctx.channel.send("Πάενε μες το κομπετίσιον ρεεε. Run this command in the competition category.")

    @comp.command(aliases=["teamname"])
    async def set_team_name(self, ctx, team_name: str):
        category = ctx.channel.category.name
        comp = Comp.objects.get({"name": category})
        if comp is None:
            raise NotInCompCategoryException

        if len(comp.team_name) == 1:  # default value is " "
            comp.team_name = team_name
            comp.save()
            general = discord.utils.get(ctx.channel.category.channels, name="general")
            await general.send(f"Let's go {team_name}!!!")
        else:
            raise TeamAlreadyHasNameException(comp.team_name)

    @set_team_name.error
    async def set_team_name_error(self, ctx, error):
        if isinstance(error.original, NotInCompCategoryException):
            await ctx.channel.send("Πάενε μες το κομπετίσιον ρεεε. Run this command in the competition category.")
        elif isinstance(error.original, TeamAlreadyHasNameException):
            await ctx.channel.send(
                f"Άρκησες ρε φίλε! This team already has a name and its... drum roll please {error.original.team_name} {EMOJIS['tada']}"
            )

    @comp.command()
    @commands.has_permissions(manage_channels=True, manage_roles=True)
    async def finish(self, ctx, comp_name):
        """
        Marks a competition as finished.

        Parameters:
            comp_name (str): name of the competition to mark as finished
        """
        comp = Comp.objects.get({"name": comp_name})
        if comp.finished_on is not None:
            raise CompetitionAlreadyFinishedException
        comp.finished_on = datetime.datetime.now()
        comp.save()

        await ctx.channel.send("Good job on the competition everyone! Επήαμε τα καλά;")

    @tasks.loop(hours=24)
    async def update_subs(self):

        comps = Comp.objects.all()
        for comp in comps:
            comp.subs_today = 0
            comp.save()


def setup(bot):
    bot.add_cog(Competition(bot))
