import asyncio
import logging
from datetime import datetime

from mcbot import triggers, Bot, Context, Task
from mcbot.models.internal.commands import CommandType

from commands.alerts import AlertCommands
from commands.myself import MyselfCommands
from commands.nodes import NodeCommands
from commands.testing import TestingCommands
from settings import Settings

settings = Settings.load_settings()
logger = logging.getLogger("zbot")

bot = Bot(settings)

testing_commands = TestingCommands(bot)
myself_commands = MyselfCommands(bot)
alert_commands = AlertCommands(bot)
node_commands = NodeCommands(bot)

@bot.prefixed_command(
    description="Show help for commands",
    help="/help [command]"
)
async def help(ctx: Context):
    if ctx.content and (cmd := ctx.bot.get_command(ctx.content)):
        await ctx.send(cmd.description + "\n" + cmd.help) # type: ignore
    else:
        messages = []
        current_message = ""
        for (name, cmd_type), command in ctx.bot._commands.items():
            if cmd_type == CommandType.CHAT:
                continue
            logger.debug(f"Processing {name}")
            help_msg = f"{ctx.bot.prefix}{name}"
            if docstring := command.description:
                help_msg += f" - {docstring}"
            help_msg += "\n"
            if len(current_message + help_msg) > 140 and current_message:
                messages.append(current_message)
                current_message = ""
            elif len(current_message + help_msg) > 140 and not current_message:
                logger.error(f"Command {name} has too long of a help string, please edit")
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