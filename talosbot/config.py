import sys
import inspect
import logging

from os import environ
from colorama import Fore
from itertools import chain
from typing import Any, List, NoReturn
from talosbot.db_models import BotConfig
from pymodm.errors import ValidationError

logger = logging.getLogger(__name__)

class ConfigurableProperty:
    """
        Defines a property that can be updated dyanmically
        through the bot. For that purpose, the last value of the property
        is also kept in the database
    """

    def __init__(self, value: str):
        self._value = value

    @property
    def value(self):
        return self._value

    def __str__(self):
        return str(self._value)

class AbstractConfig:

    __instance__ = None

    def __new__(cls):
        if AbstractConfig.__instance__ is None:
            logger.info("[+] Creating config instance")
            AbstractConfig.__instance__ = object.__new__(cls)
            AbstractConfig.__instance__._copy_from_class()
            AbstractConfig.__instance__._load_from_db()
        
        return AbstractConfig.__instance__

    def _copy_from_class(self) -> NoReturn:
        """Copies all attributes from class to instance"""
        dynamic_props = self._get_configurable_props_from_cls()
        static_props = self._get_static_props_from_cls()
        for prop, value in chain(static_props, dynamic_props):
            setattr(self, prop, value)

    def _get_static_props_from_cls(self) -> List[Any]:
        props = inspect.getmembers(self.__class__, lambda a: not (inspect.isroutine(a)))
        props = filter(lambda a: not(isinstance(getattr(self.__class__, a[0]), ConfigurableProperty)
                        or (a[0].startswith("__") and a[0].endswith("__"))), props)
        return props

    def _get_configurable_props_from_cls(self) -> List[Any]:
        props = inspect.getmembers(self.__class__, lambda a: not (inspect.isroutine(a)))
        props = filter(lambda a: isinstance(getattr(self.__class__, a[0]), ConfigurableProperty), props)
        
        return map(lambda a: (a[0], a[1].value), props)

    def _get_or_create_config_from_db(self) -> BotConfig:
        """Loads the BotConfig from DB or creates a new one with the values
        provided in the subclasses of this class
        NOTE: Assumes that there is only one config.
        """
        try:
            return BotConfig.objects.all().first()
        except BotConfig.DoesNotExist:
            config = BotConfig(
                **{k: v for k, v in self._get_configurable_props_from_cls()}
            )
            try:
                config.save()
            except ValidationError as err:
                logger.error("Couldn't launch bot. Not configured properly")
                logger.error(err)
                sys.exit(1)
        return config

    def _load_from_db(self) -> NoReturn:
        dynamic_props = self._get_configurable_props_from_cls()
        config_in_db = self._get_or_create_config_from_db()
        self.config_in_db = config_in_db
        for prop, value in dynamic_props:
            saved_value = getattr(config_in_db, prop, None)
            if saved_value is not None and value != saved_value:
                setattr(self, prop, saved_value)

    def save(self) -> NoReturn:
        """Saves current instance config to database"""
        config_in_db_props = inspect.getmembers(self.config_in_db, lambda a: not (inspect.isroutine(a)))
        for prop in self._get_configurable_props_from_cls():
            prop_name = prop[0]
            config_in_db_prop_names = list(
                map(lambda p: p[0], config_in_db_props)
            )
            if prop_name in config_in_db_prop_names:
                setattr(self.config_in_db, prop_name, getattr(self, prop_name))
            else:
                logger.warning(
                    Fore.YELLOW
                    + "Attempted to save configurable config variable ({0}) which is not included in the DB model...".format(
                        prop_name
                    )
                )
        self.config_in_db.save()
        self._load_props_from_db()  # To ensure consistency after db validations


class Config(AbstractConfig):
    """Configuration class"""
    DB_URL = environ.get("TALOSBOT_DB_URL", "mongodb://mongo/talosdb")
    COMMAND_PREFIX = environ.get("TALOSBOT_COMMAND_PREFIX", '!')
    DISCORD_BOT_TOKEN = environ.get("TALOSBOT_DISCORD_BOT_TOKEN")

    GIT_REPO = environ.get("TALOSBOT_GIT_REPO", "https://github.com/npitsillos/talosbot.git")

    KAGGLE_USERNAME = environ.get("KAGGLE_USERNAME")
    KAGGLE_KEY = environ.get("KAGGLE_KEY")

    ADMIN_ROLE = ConfigurableProperty(environ.get("TALOSBOT_ADMIN_ROLE"))

class DevConfig(Config):
    pass


class ProdConfig(Config):
    pass

bot_config = {
    "dev": DevConfig,
    "prod": ProdConfig
}