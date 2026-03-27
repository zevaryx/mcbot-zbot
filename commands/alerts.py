import asyncio
from functools import partial
from typing import TYPE_CHECKING

from mcbot.models.internal.command import command
from mcbot.models.internal.task import Task
from mcbot.models.internal.triggers import TimeTrigger

from . import Extension
from settings import Settings, Alert

if TYPE_CHECKING:
    from mcbot import Bot

class AlertCommands(Extension):
    
    def __init__(self, bot: Bot):
        super().__init__(bot)
        
        for alert in bot._settings.alerts: # type: ignore
            if not alert.enabled:
                continue
            call = partial(self.base_send, alert=alert)
            task = Task(call, alert.schedule.trigger)
            self.bot.task(task)
            self._tasks.append(task)
            
    async def base_send(self, alert: Alert) -> None:
        async with self.bot._lock:
            for mode in alert.path_hash_mode:
                self.bot.set_path_hash_mode(mode)
                await self.bot.send_channel_message(alert.channel, alert.message)
                await asyncio.sleep(1)
            self.bot.set_path_hash_mode(None)
    
    # @Task.create(TimeTrigger(hour=12))
    # async def multibyte_alert(self):
    #     settings = Settings.load_settings()
    #     if settings.alert_for_multibyte:
    #         message = "Hello! If you can see this message, please go to your Experimental Settings and set path mode to 2-byte!"
    #         async with self.bot._lock:
    #             self.bot.set_path_hash_mode(0)
    #             await self.bot.send_channel_message(0, message)
    #             self.bot.set_path_hash_mode(None)