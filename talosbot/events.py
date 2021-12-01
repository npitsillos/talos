import logging
import discord

from talosbot.__version__ import __version__

logger = logging.getLogger(__name__)


def hook_events(bot):
    @bot.event
    async def on_ready():
        logger.info(f"<{bot.user.name} Online>")
        logger.info(f"TalosBot v{__version__}")
        activity = discord.Game(name="Atari games to learn! Use !help")
        await bot.change_presence(activity=activity)

    @bot.event
    async def on_message(message):
        if bot.user in message.mentions:
            await message.channel.send("Μόλις απόχτησα συνείδησην... Πε μου;")
        await bot.process_commands(message)

    @bot.event
    async def on_member_join(member):
        await member.send(
            f"Hello {member.name} Welcome to the server! Send {bot.command.prefix}help for a list of commands."
        )

        announcements = discord.utils.get(member.guild.text_channels, name="announcements")

        if announcements is not None:
            await announcements.send(
                f"Welcome {member.name}. Why don't you interoduce yourself to the other CYBrAIners."
            )
