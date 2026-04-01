import binascii
import json
import logging
import re
from functools import lru_cache
from typing import TYPE_CHECKING, Any

import aiohttp
from mcbot import Context
from mcbot.const import __version__
from mcbot.models.internal.commands.chat import chat_command
from mcbot.models.internal.commands.prefixed import prefixed_command
from mcbot.models.internal.task import Task
from mcbot.models.internal.triggers import IntervalTrigger
from pymc_core.companion.models import Contact
from pymc_core.protocol.constants import CONTACT_TYPE_REPEATER, CONTACT_TYPE_ROOM_SERVER

from . import Extension
from models.colomesh.node import Node, NodeType

if TYPE_CHECKING:
    from mcbot import Bot
    
prefix_checker = re.compile(r"^[0-9a-f]{2,6}$", flags=re.I)

class NodeManager:
    
    def __init__(self):
        self.nodes: list[Node] = []
        self._updated = False
        self._session: aiohttp.ClientSession = None # type: ignore
        self._logger = logging.getLogger("NodeManager")
        
        self.get_collisions = lru_cache(maxsize=256)(self.get_collisions)
        
    async def update(self) -> None:
        self._logger.debug(f"Updating NodeManager...")
        if not self._session:
            self._session = aiohttp.ClientSession(headers={"user-agent": f"zbot/{__version__}"})
        url = "https://raw.githubusercontent.com/Colorado-Mesh/coloradomesh_python/refs/heads/master/data/meshcore/nodes/nodes.json"
        resp = await self._session.get(url)
        resp.raise_for_status()
        data = await resp.content.read()
        self.nodes = Node.from_list(json.loads(data))
        self._updated = True
        self._logger.info(f"NodeManager now has {len(self)} nodes!")
        
    def get_nodes(self, prefix: str, node_type: NodeType = NodeType.REPEATER) -> list[Node]:
        self._logger.debug(f"Finding nodes with prefix {prefix}")
        prefix = prefix.strip()
        matches = []
        for node in self.nodes:
            if node.node_type == node_type and node.public_key.upper().startswith(prefix.upper()):
                matches.append(node)
        return matches
    
    def get_collisions(self, hash: str | None = None) -> dict[int, dict[str, Node]] | list[Node]:
        if not hash:
            mapping = {1: {}, 2: {}, 3: {}}
            for node in self.nodes:
                for size in mapping:
                    if node.get_id(size - 1) not in mapping[size]:
                        mapping[size][node.get_id(size - 1)] = []
                    mapping[size][node.get_id(size - 1)].append(node)
            return mapping
        collisions = []
        for node in self.nodes:
            if node.public_key.startswith(hash):
                collisions.append(node)
        return collisions
        
    def __len__(self):
        return len(self.nodes)
    
    def __contains__(self, item: Any) -> bool:
        if isinstance(item, Node):
            return item in self.nodes
        elif isinstance(item, str):
            return any(
                x.public_key.startswith(item) 
                or x.name == item 
                for x in self.nodes
            )
        return False

class NodeCommands(Extension):
    def __init__(self, bot: Bot):
        super().__init__(bot)
        
        self._manager = NodeManager()
        
    def _search_contacts(self, prefix: str) -> list[Contact]:
        contacts = self.bot.get_contacts()
        matches = []
        for contact in contacts:
            if not contact.adv_type in [CONTACT_TYPE_ROOM_SERVER, CONTACT_TYPE_REPEATER]:
                continue
            if binascii.hexlify(contact.public_key).decode().upper().startswith(prefix.upper()):
                matches.append(contact)
        return matches
    
    def _dedup(self, matches: list[Contact | Node]) -> list[str]:
        lookup: dict[str, str] = {}
        for match in matches:
            pk = match.public_key
            if isinstance(pk, bytes):
                pk = binascii.hexlify(pk).decode()
            pk = pk.lower()
            if pk not in lookup:
                lookup[pk] = match.name
        return list(lookup.values())
    
    @prefixed_command(
        name="nodecount",
        description="Get a count of the nodes from analyzers",
    )
    async def nodecount(self, ctx: Context):
        if not self._manager._updated:
            await self._manager.update()
        nodes = {
            NodeType.REPEATER: 0,
            NodeType.ROOM_SERVER: 0,
            NodeType.COMPANION: 0,
            NodeType.SENSOR: 0,
        }
        names = {
            NodeType.REPEATER: "Repeater",
            NodeType.ROOM_SERVER: "Room Server",
            NodeType.COMPANION: "Companion",
            NodeType.SENSOR: "Sensor",
        }
        for node in self._manager.nodes:
            nodes[node.node_type] += 1
            
        message = "Nodes in CO Region:\n"
        for node_type, num in nodes.items():
            if num > 0:
                message += f"{names.get(node_type)}: {num}\n"
        await ctx.send(message.strip())
            
        
    @prefixed_command(
        name="prefix",
        description="Get node(s) with prefix",
        help="/prefix <prefix>, where <prefix> is the first 1, 2, or 3 bytes of the public key",
    )
    async def _prefixed_prefix(self, ctx: Context):
        await self.prefix(ctx)
        
    @chat_command(
        name="prefix",
        description="Get node(s) with prefix",
        help="prefix <prefix>, where <prefix> is the first 1, 2, or 3 bytes of the public key",
        triggers=["prefix"],
    )
    async def _chat_prefix(self, ctx: Context):
        await self.prefix(ctx)
    
    async def prefix(self, ctx: Context):
        if not self._manager._updated:
            await self._manager.update()
        if not ctx.content or not prefix_checker.match(ctx.content):
            self._logger.debug(f"Invalid prefix: {ctx.content}")
            await ctx.send("Usage: /prefix <prefix>, where <prefix> is the first 1, 2, or 3 bytes of the public key")
            return
        matches_nm = self._manager.get_nodes(ctx.content)
        matches_bot = self._search_contacts(ctx.content)
        matches = self._dedup(matches_nm + matches_bot)
        if not matches:
            await ctx.send(f"❌ No known nodes with prefix {ctx.content}")
        else:
            message = f"Prefix '{ctx.content.upper()}': {len(matches)} repeater(s)\n"
            for idx, match in enumerate(matches, start=1):
                message += f"{idx}. {match}\n"
            await ctx.send(message.strip())
        
    @Task.create(IntervalTrigger(hours=1))
    async def update(self):
        try:
            await self._manager.update()
        except Exception as e:
            self._logger.error(f"Failed to update NodeManager: {e}")
    