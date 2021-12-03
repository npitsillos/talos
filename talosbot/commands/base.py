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

        @bot.command()
        async def showcomps(ctx):
            # TODO: Implement command to show currently entered comps
            raise NotImplemented
            
        @bot.command()
        async def join(ctx, comp_name):
            # TODO: Implement command for request to join comp
            raise NotImplemented