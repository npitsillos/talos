import logging
from typing import Optional
import discord
import datetime

from discord.ext import commands
from talosbot.helpers import slugify
from talosbot.db_models import Comp
from kaggle.api.kaggle_api_extended import KaggleApi
from talosbot.exceptions import (
    InvalidCategoryException,
    CompetitionAlreadyExistsException,
    CompetitionAlreadyFinishedException,
    )

logger = logging.getLogger(__name__)

CATEGORIES = ["featured", "research", "recruitment", "gettingStarted", "masters", "playground"]
EMOJIS = {
    "question": ":question:",
    "right": ":point_right:",
    "calendar": ":calendar:"
}


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
        description = f"{EMOJIS['question']} {comp_desc}\n"\
                    f"{EMOJIS['right']} Reward: {reward}\n"\
                    f"{EMOJIS['calendar']} Deadline: {deadline}"
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
                comp_name (str): name of the competition to find and create
        """
        
        first_word = comp_name.split()[0]
        comps = self.api.competitions_list(sort_by="latestDeadline")
        latest_comps = [comp.__dict__ for comp in comps]
        matched_comps = []

        for latest_comp in latest_comps:
            if first_word in latest_comp["title"].lower():
                matched_comps.append(latest_comp)

        if len(matched_comps) == 1:
            comp_cat_name = slugify(matched_comps[0]["title"])
            category = discord.utils.get(ctx.guild.categories, name=comp_cat_name)

            if category is not None:
                raise CompetitionAlreadyExistsException

            comp_role = await self.guild.create_role(name=f"Comp-{comp_cat_name}", mentionable=True)
            await ctx.message.author.add_roles(comp_role)
            overwrites = {
                # Everyone
                self.guild.get_role(self.gid): discord.PermissionOverwrite(read_messages=False),
                self.bot.user: discord.PermissionOverwrite(read_messages=True),
                comp_role: discord.PermissionOverwrite(read_messages=True)
            }

            category = await self.guild.create_category(name=comp_cat_name, overwrites=overwrites)
            general_channel = await self.guild.create_text_channel(name="general", category=category)

            Comp(name=category, url=matched_comps[0]["url"], created_at=datetime.datetime.now(), deadline=matched_comps[0]["deadline"], team_name=team_name).save()

            await general_channel.send("@here New competition created! @here Άτε κοπέλια..!")
        elif len(matched_comps) > 1:
            await ctx.channel.send("Έσηει παραπάνω που ένα!")
            for matched_comp in matched_comps:
                emb = self._get_competition_embed(matched_comp)
                await ctx.channel.send(embed=emb)
        else:
            await ctx.channel.send("Νομίζω έφηε σου το όνομα! Use !kgl competitions to see a list.")

    @create.error
    async def create_error(self, ctx, error):
        if isinstance(error.original, CompetitionAlreadyExistsException):
            await ctx.channel.send("Ρεεεε τούτο το κομπετίσιον υπάρχει!!")

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

def setup(bot):
    bot.add_cog(Competition(bot))