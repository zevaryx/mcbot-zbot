import asyncio
import binascii
from datetime import datetime

from mcbot import Context
from mcbot.models.internal.commands.chat import chat_command
from mcbot.models.internal.commands.prefixed import prefixed_command
from pymc_core.protocol.constants import CONTACT_TYPE_REPEATER, CONTACT_TYPE_ROOM_SERVER

from . import Extension

class TestingCommands(Extension):
    @prefixed_command(description="Pong!")        
    async def ping(self, ctx: Context):
        await ctx.reply("Pong!")
    
    @prefixed_command(name="path", description="Get message path")
    async def _prefixed_path(self, ctx: Context):
        await self.path(ctx)
        
    @chat_command(name="path", description="Get message path", triggers=["p", "path"])
    async def _chat_path(self, ctx: Context):
        await self.path(ctx)

    async def path(self, ctx: Context):
        contacts = self.bot.get_contacts()
        path: list[str] = ctx.packet.get_path_hashes_hex()
        messages = []
        current_message = ""
        for hop in path:
            matching_contact = None
            for contact in contacts:
                if not contact.adv_type in [CONTACT_TYPE_ROOM_SERVER, CONTACT_TYPE_REPEATER]:
                    continue
                if contact.public_key.hex()[:2].upper() == hop.upper():
                    matching_contact = contact
                    break
            if matching_contact:
                name = contact.name
            else:
                name = "<UNKNOWN>" 
            step = f"{hop}: {name}\n"
            if len(current_message + step) > 140 and current_message:
                messages.append(current_message)
                current_message = ""
            elif len(current_message + step) > 140 and not current_message:
                self._logger.warning(f"Path step is >140 characters: {step}")
                step = step[:32] + "\n"
                if len(current_message + step) > 140:
                    messages.append(current_message)
                    current_message = ""
            current_message += step
        if current_message:
            messages.append(current_message)
        if not messages:
            messages = ["Direct"]
        for message in messages:
            await ctx.send(message.strip())
            await asyncio.sleep(1)
            
    @prefixed_command(name="test", description="Test connectivity to the bot")
    async def _prefixed_test(self, ctx: Context):
        await self.test(ctx)
        
    @chat_command(name="test", description="Test connectivity to the bot", triggers=["t", "test", "testing"])
    async def _chat_test(self, ctx: Context):
        await self.test(ctx)
    
    async def test(self, ctx: Context):
        path = ",".join(ctx.packet.get_path_hashes_hex()) or "direct"
        snr = ctx.packet.snr
        rssi = ctx.packet.rssi
        received_at = datetime.now().strftime("%H:%M:%S")
        
        await ctx.send(
            f"ack @[{ctx.sender}] | {path} | SNR: {snr:.2f} dB | "
            f"RSSI: {rssi} dBm | Received at: {received_at} | "
            f"Hash Size: {ctx.packet.get_path_hash_size()}"
        )
    
    @prefixed_command(description="Echo a message", help="/echo [message]")
    async def echo(self, ctx: Context):
        if ctx.content:
            await ctx.send(ctx.content)
        else:
            await ctx.send("<no content>")