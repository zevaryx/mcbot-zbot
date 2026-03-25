import asyncio
import binascii
from datetime import datetime

from mcbot import Context

from . import CommandWrapper

class TestingCommands(CommandWrapper):        
    async def ping(self, ctx: Context):
        """Pong!"""
        await ctx.reply("Pong!")
        
    async def path(self, ctx: Context):
        """Get message path"""
        contacts = self.bot.get_contacts()
        path: list[str] = ctx.packet.get_path_hashes_hex()
        messages = []
        current_message = ""
        for hop in path:
            matching_contact = None
            for contact in contacts:
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
                self.logger.warning(f"Path step is >140 characters: {step}")
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
            
    async def test(self, ctx: Context):
        """Get connection stats to the bot"""
        path = ",".join(ctx.packet.get_path_hashes_hex()) or "direct"
        snr = ctx.packet.snr
        rssi = ctx.packet.rssi
        received_at = datetime.now().strftime("%H:%M:%S")
        
        await ctx.send(
            f"ack @[{ctx.sender}] | {path} | SNR: {snr:.2f} dB | "
            f"RSSI: {rssi} dBm | Received at: {received_at} | "
            f"Hash Size: {ctx.packet.get_path_hash_size()}"
        )
        
    async def echo(self, ctx: Context):
        """Echo a message"""
        if ctx.content:
            await ctx.send(ctx.content)
        else:
            await ctx.send("<no content>")