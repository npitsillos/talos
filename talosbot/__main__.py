import logging
import talosbot.logging
from talosbot.bot import TalosBot

logger = logging.getLogger(__name__)


def launch():

    bot = TalosBot()
    bot.launch()


if __name__ == "__main__":
    launch()
