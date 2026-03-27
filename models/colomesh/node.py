"""Re-implemented Node from https://github.com/Colorado-Mesh/coloradomesh_python"""

from enum import Enum
from typing import Any, Optional, Self, Type

from pydantic import BaseModel

class NodeType(Enum):
    """
    Enum representing the type of MeshCore node on the ColoradoMesh network.
    """
    UNKNOWN = 0
    COMPANION = 1
    REPEATER = 2
    ROOM_SERVER = 3
    SENSOR = 4

    @classmethod
    def from_int(cls: Type[Self], role: int) -> NodeType:
        if role == 1:
            return cls.REPEATER
        elif role == 2:
            return cls.ROOM_SERVER
        elif role == 3:
            return cls.COMPANION
        elif role == 4:
            return cls.SENSOR
        elif role == 0:
            return cls.UNKNOWN
        else:
            raise ValueError(f"Unknown device role: {role}")
        
class Node(BaseModel):
    """
    Represents a MeshCore node on the ColoradoMesh network.
    """
    public_key: str
    name: str
    node_type: NodeType
    created_at: int  # Unix timestamp
    last_heard: int  # Unix timestamp
    owner: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    @classmethod
    def from_dict(cls: Type[Self], data: dict[str, Any]) -> Self:
        wanted = [
            "public_key", 
            "name", 
            "node_type", 
            "created_at", 
            "last_heard", 
            "owner", 
            "latitude", 
            "longitude"
        ]
        fixed = {}
        for key, value in data.items():
            if key in wanted:
                fixed[key] = value
        return cls(**fixed)
    
    @classmethod
    def from_list(cls: Type[Self], data: list[dict[str, Any]]) -> list[Self]:
        fixed = []
        for item in data:
            fixed.append(cls.from_dict(item))
        return fixed
    
    def get_id(self, hash_mode: int = 0) -> str:
        return self.public_key[:2 * (hash_mode + 1)].upper()