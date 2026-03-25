from mcbot import Context
from mcbot.models.internal.command import command
from mcbot.models.internal.task import Task
from mcbot.models.internal.triggers import TimeTrigger

from . import Extension

class AlertCommands(Extension):
    
    @Task.create(TimeTrigger(hour=12))
    async def multibyte_alert(self):
        message = "Hello! If you can see this message, please go to your Experimental Settings and set path mode to 2-byte!"
        async with self.bot._lock:
            self.bot.set_path_hash_mode(0)
            await self.bot.send_channel_message(0, message)
            self.bot.set_path_hash_mode(None)