import logging

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
            Shows contribute link
            """
            await ctx.channel.send(f"Κάμε με πιο έξυπνο! {bot.config.GIT_REPO}")
