import asyncio
import logging
from datetime import datetime

from mcbot import triggers, Bot, Context, Task, load_settings
from commands.myself import MyselfCommands
from commands.testing import TestingCommands

settings = load_settings()
logger = logging.getLogger("zbot")

bot = Bot(settings)

testing_commands = TestingCommands(bot)
myself_commands = MyselfCommands(bot)

@bot.command
async def help(ctx: Context):
    """This help message"""
    messages = []
    current_message = ""
    for command in ctx.bot._commands:
        logger.debug(f"Processing {command.name}")
        help_msg = f"{settings.prefix}{command.name}"
        if docstring := command.callback.__doc__:
            help_msg += f" - {docstring}"
        help_msg += "\n"
        if len(current_message + help_msg) > 140 and current_message:
            messages.append(current_message)
            current_message = ""
        elif len(current_message + help_msg) > 140 and not current_message:
            logger.error(f"Command {command.name} has too long of a docstring, please edit")
            continue
        current_message += help_msg
        
    if current_message:
        messages.append(current_message)
    for message in messages:
        await ctx.send(message.strip())
        await asyncio.sleep(1)

# @bot.task
# @Task.create(triggers.IntervalTrigger(seconds=5))
# async def five_second_test(bot: Bot):
#     bot.logger.info("5 seconds")

asyncio.run(bot.start())