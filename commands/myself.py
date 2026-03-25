from datetime import datetime

from mcbot import Context
from mcbot.utils.board_configs import HARDWARE_CONFIGS

from . import CommandWrapper

class MyselfCommands(CommandWrapper):
    async def about(self, ctx: Context):
        """About this bot"""
        await ctx.send("Written by Zeva, using https://github.com/zevaryx/mcbot, a native Python library for Pi hats")
        
    async def stats(self, ctx: Context):
        """Bot stats"""
        uptime = (datetime.now() - self.bot._start_time)
        contacts = len(self.bot.get_contacts())
        last_advert = "N/A"
        if self.bot.sqlite:
            last_advert = datetime.fromtimestamp(await self.bot.sqlite.get_last_advert()).strftime("%m/%d/%Y %H:%M:%S")
        message = f"Uptime: {uptime}\nNum Contacts: {contacts}\nLast Advert: {last_advert}"
        await ctx.send(message)