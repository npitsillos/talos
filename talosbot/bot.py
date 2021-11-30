import os
import sys
import discord
import logging

from pathlib import Path
from pymodm import connect
from dotenv import load_dotenv
from discord.ext.commands import Bot
from talosbot.cog_manager import CogManager
from talosbot.events import hook_events
from talosbot.error_handling import hook_error_handlers
from talosbot.commands.base import BaseCommandsMixin
from talosbot.commands.manage import ManageCommandsMixin
from pymongo.errors import ServerSelectionTimeoutError

logger = logging.getLogger(__name__)

class TalosBot(Bot, BaseCommandsMixin):

    def __init__(self, *args, **kwargs):

        env_path = os.path.join(
            Path(sys.modules[__name__].__file__).resolve().parent.parent, ".env"  
        )

        load_dotenv(dotenv_path=env_path, verbose=True)
        env = os.environ.get("TALOSBOT_ENV", "dev")
        from talosbot.config import bot_config
        
        try:
            self.config_cls = bot_config[env]
            self.init_db()
            self.config = self.config_cls()
        except ServerSelectionTimeoutError:
            logging.error(
                "Database timeout error. Make sure an instance of mongodb is running and your TALOSBOT_DB_URL env variable is set!"
            )
            exit(1)
        
        intents = discord.Intents.default()
        intents.members = True
        super().__init__(*args, command_prefix=self.config.COMMAND_PREFIX, intents=intents, **kwargs)
        BaseCommandsMixin.load_commands(self)
        ManageCommandsMixin.load_commands(self)

        hook_error_handlers(self)
        hook_events(self)

        self.cog_manager = CogManager(self)
        self.cog_manager.load_cogs()

    def launch(self):
        logger.info("Launching TalosBot...")
        if self.config.DISCORD_BOT_TOKEN is None:
            raise ValueError("DISCORD_TOKEN is not set.")
        self.run(self.config.DISCORD_BOT_TOKEN)

    def init_db(self):
        connect(self.config_cls.DB_URL)