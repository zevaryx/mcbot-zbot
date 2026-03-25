import inspect
import logging
from typing import TYPE_CHECKING

from mcbot.models.internal.command import Command

if TYPE_CHECKING:
    from mcbot import Bot  

class CommandWrapper:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.logger = logging.getLogger(self.__class__.__name__)
        self._commands: list[Command] = []
        for name, callback in inspect.getmembers(self, predicate=inspect.iscoroutinefunction):
            if name.startswith("_"):
                continue
            self.bot.command(callback)
            self._commands.append(Command(name, callback))
        self.logger.info(f"Loaded {self.__class__.__name__} with {len(self._commands)} commands")