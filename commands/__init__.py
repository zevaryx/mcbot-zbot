import logging
from typing import TYPE_CHECKING

from mcbot.models.internal.extension import Extension as BaseExtension

if TYPE_CHECKING:
    from mcbot import Bot

class Extension(BaseExtension):
    def __init__(self, bot: Bot):
        self.bot = bot
        self._logger = logging.getLogger(self.name)