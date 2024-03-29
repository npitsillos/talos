import discord
import logging
import datetime

from discord.ext import commands
from talosbot.db_models import TutorialModel
from talosbot.exceptions import TutorialAlreadyExistsException

logger = logging.getLogger(__name__)


async def check_role(ctx):
    return Tutorial.CREATE_ROLE in [role.name for role in ctx.author.roles]


has_create_role = commands.check(check_role)


class Tutorial(commands.Cog):

    CREATE_ROLE = None
    MODERATOR_ONLY_CHANNEL_ID = 934108003228061736

    def __init__(self, bot):
        self.bot = bot
        Tutorial.CREATE_ROLE = self.bot.config.ADMIN_ROLE

    def _get_tutorial_embed(self, tutorial):
        description = f"Category: {tutorial.category}\n" f"Difficulty: {tutorial.difficulty}"
        emb = discord.Embed(title=tutorial.name, description=description, url=tutorial.url, colour=4387968)
        return emb

    @commands.group()
    async def tutorial(self, ctx):
        """
        Collections of commands for interacting with tutorials
        """

        self.guild = ctx.guild
        self.gid = ctx.guild.id

        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid command passed. Use !help")

    @tutorial.command()
    @has_create_role
    async def create(self, ctx, name, url, difficulty=None, category=None):
        """
        Creates a tutorial and stores it in the database

        Parameters:
            name (str): tutorial name
            url (str): the google colab url for the tutorial
            difficulty (str): the tutorial difficulty
            category (str): the tutorial category
        """

        try:
            tutorial = TutorialModel.objects.get({"name": name})
            if tutorial is not None:
                raise TutorialAlreadyExistsException
        except TutorialModel.DoesNotExist:
            TutorialModel(
                name=name, created_at=datetime.datetime.now(), url=url, difficulty=difficulty, category=category
            ).save()
        general_channel = discord.utils.get(
            discord.utils.get(self.guild.categories, name="cybrainers").channels, name="general"
        )

        await general_channel.send("@everyone!!! A new tutorial has been added! Πάμε να μάθουμεεε..!! :partying_face:")
        channel = self.guild.get_channel(Tutorial.MODERATOR_ONLY_CHANNEL_ID)
        await channel.send("Tutorial has been created.")

    @create.error
    async def create_error(self, ctx, error):
        if isinstance(error.original, TutorialAlreadyExistsException):
            await ctx.channel.send("Ρεεεε τούτο το τουτόριαλ υπάρχει!!")

    @tutorial.command()
    async def list(self, ctx):
        """
        Lists all tutorials uploaded to the database.
        """
        tutorials = TutorialModel.objects.all()
        if tutorials.count() == 0:
            await ctx.channel.send("Ένεσηει τουτόριαλς κόμααα... No tutorials added yet! Admins where you at??")
        for tutorial in tutorials:
            emb = self._get_tutorial_embed(tutorial)
            await ctx.channel.send(embed=emb)


def setup(bot):
    bot.add_cog(Tutorial(bot))
