from dataclasses import dataclass, field
from datetime import datetime

MAX_MESSAGE_LENGTH = 2000

@dataclass
class LogEntry:
    service: str
    level: str
    message: str
    created_at: datetime = None

    def __post_init__(self):
        if len(self.message) > MAX_MESSAGE_LENGTH:
            self.message = self.message[:MAX_MESSAGE_LENGTH] + "... [truncated]"

    def to_dict(self) -> dict:
        return {
            "service": self.service,
            "level": self.level,
            "message": self.message,
        }