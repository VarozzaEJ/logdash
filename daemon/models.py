from dataclasses import dataclass
from datetime import datetime

@dataclass
class LogEntry:
    service: str
    level: str
    message: str
    created_at: datetime = None

    def to_dict(self) -> dict:
        return {
            "service": self.service,
            "level": self.level,
            "message": self.message,
        }