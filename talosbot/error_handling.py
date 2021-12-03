import sys
import logging

from discord.ext.commands.errors import (
    CommandNotFound,
    MissingPermissions,
    NoPrivateMessage,
    MissingRole,
    MissingRequiredArgument,
    CommandInvokeError,
)

logger = logging.getLogger(__name__)


def hook_error_handlers(bot):
    @bot.event
    async def on_error(event, *args, **kwargs):
        logger.info("ON_ERROR")
        logger.info(sys.exc_info())
        for arg in args:
            if isinstance(arg, Exception):
                raise arg

    @bot.event
    async def on_command_error(ctx, error):

        logger.info("ON_COMMAND_ERROR")

        if ctx.cog is not None:
            logger.info(f"Received cog exception: {error}")
            raise error.original

        if isinstance(error, CommandNotFound):
            await ctx.channel.send("Command not found.")
        elif isinstance(error, MissingPermissions):
            await ctx.channel.send("Permission denied!")
        elif isinstance(error, NoPrivateMessage):
            await ctx.channel.send("This command can not be send in a private message.")
        elif isinstance(error, MissingRole):
            await ctx.channel.send("You don't have the required role to run this command.")
        elif isinstance(error, MissingRequiredArgument):
            await ctx.send_help(ctx.command)
        else:
            # Something else happened here
            if hasattr(error, "original"):
                raise error.original
            else:
                raise error
