from dataclasses import dataclass
from datetime import datetime


@dataclass
class WebSocketMessage:
    type: str
    content: str
    timestamp: str = datetime.now().isoformat()

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

    def to_dict(self):
        return {
            "type": self.type,
            "content": self.content,
            "timestamp": self.timestamp
        }

@dataclass
class ProgressMessage(WebSocketMessage):
    progress_type: str = "unknown"

    def to_dict(self):
        return {
            "type": self.type,
            "content": self.content,
            "timestamp": self.timestamp,
            "progress_type": self.progress_type
        }
