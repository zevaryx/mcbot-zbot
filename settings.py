from abc import abstractmethod
from typing import Any, Literal
from zoneinfo import ZoneInfo

from mcbot.settings import Settings as BaseSettings
from mcbot.models.internal.triggers import BaseTrigger, TimeTrigger, CronTrigger, IntervalTrigger
from pydantic import BaseModel, Field, field_validator

class BaseSchedule(BaseModel):
    @property
    @abstractmethod
    def trigger(self) -> BaseTrigger:
        """The trigger for the schedule"""

class IntervalSchedule(BaseSchedule):
    weeks: float | int = 0
    days: float | int = 0
    hours: float | int = 0
    minutes: float | int = 0
    seconds: float | int = 0
    
    @property
    def trigger(self) -> IntervalTrigger:
        return IntervalTrigger(
            weeks=self.weeks,
            days=self.days,
            hours=self.hours,
            minutes=self.minutes,
            seconds=self.seconds
        ) # type: ignore

class TimeSchedule(BaseSchedule):
    hour: int = 0
    minute: int = 0
    seconds: int = 0
    utc: bool = False
    
    @property
    def trigger(self) -> TimeTrigger:
        return TimeTrigger(
            hour=self.hour,
            minute=self.minute,
            seconds=self.seconds,
            utc=self.utc,
        ) # type: ignore
        
class CronSchedule(BaseSchedule):
    cron: str
    tz: ZoneInfo = ZoneInfo("UTC")
    
    @property
    def trigger(self) -> CronTrigger:
        return CronTrigger(
            cron=self.cron,
            tz=self.tz
        ) # type: ignore

def default_hash_mode() -> list[Literal[0, 1, 2]]:
    return [0]

class Alert(BaseModel):
    message: str
    enabled: bool = False
    type: Literal["time", "cron", "interval"]
    schedule: IntervalSchedule | TimeSchedule | CronSchedule
    path_hash_mode: list[Literal[0, 1, 2]] = Field(default_factory=default_hash_mode)
    """What byte path to use: 1-byte = 0, 2-byte = 1, 3-byte = 2"""
    channel: int = 0
    """Channel index to send, default public"""
    
    @field_validator("schedule", mode="before")
    @classmethod
    def validate_schedule(cls, value: Any) -> Any:
        if isinstance(value, dict):
            if "cron" in value:
                return CronSchedule(**value)
            elif "utc" in value:
                return TimeSchedule(**value)
            elif "weeks" in value:
                return IntervalSchedule(**value)
        return value
    

class Settings(BaseSettings):
    alerts: list[Alert] = Field(default_factory=list)
