import os
import sys

from pathlib import Path
from talosbot.db_models import CogDetails


class CogManager:
    def __init__(self, bot):
        self.bot = bot

    # @property
    # def cogs(self):
    #     return CogDetails.objects.all()

    def _builtin_cogs(self):
        cog_dir = os.path.join(Path(__file__).resolve().parent, "extensions")
        builtin_cogs = self._load_cog_details_path(cog_dir)

        return builtin_cogs

    def _load_cog_details_path(self, cog_dirs):
        cog_details = []
        for dir in os.listdir(cog_dirs):
            cog_dir = os.path.join(cog_dirs, dir)
            if os.path.isdir(cog_dir) and not dir.startswith("__") and not dir.endswith("__"):
                cog_details.append((dir, cog_dir))

        return cog_details

    def load_cogs(self):
        builtin_cogs = self._builtin_cogs()

        for cog in builtin_cogs:
            sys.path.insert(1, cog[1])
            self.bot.load_extension(cog[0])
