from dataclasses import dataclass
from datetime import datetime
from typing import Optional


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
    tool_name: Optional[str] = None
    tool_args: Optional[dict] = None

    def to_dict(self):
        result = {
            "type": self.type,
            "content": self.content,
            "timestamp": self.timestamp,
            "progress_type": self.progress_type
        }
        if self.tool_name:
            result["tool_name"] = self.tool_name
        if self.tool_args:
            result["tool_args"] = self.tool_args
        return result
