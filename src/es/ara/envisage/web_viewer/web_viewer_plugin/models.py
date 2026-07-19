from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from typing import Any

COMMAND_CALL_RESPONSE_OK="ACK"
COMMAND_CALL_RESPONSE_ERROR_EXECUTOR_NOT_FOUND="EXECUTOR_NOT_FOUND"
COMMAND_CALL_RESPONSE_ERROR_PARSING_RESPONSE="ERROR_PARSING_RESPONSE"
COMMAND_CALL_RESPONSE_ERROR_EXECUTOR_FAILS="EXECUTOR_FAILS"

@dataclass
class Message(ABC):
    @classmethod
    @abstractmethod
    def from_json(cls, value: str) -> Message:
        raise NotImplementedError

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict())


@dataclass
class CommandCall(Message):
    name: str
    args: dict[str, Any]

    @classmethod
    def from_json(cls, value: str) -> CommandCall:
        payload = json.loads(value)
        return cls(name=payload["name"], args=payload["args"])


@dataclass
class CommandCallResponse(Message):
    code: str
    details: Any

    @classmethod
    def from_json(cls, value: str) -> CommandCallResponse:
        payload = json.loads(value)
        return cls(code=payload["code"], details=payload["details"])


@dataclass
class Event(Message):
    name: str
    source: str
    details: dict[str, Any] | None

    @classmethod
    def from_json(cls, value: str) -> Event:
        payload = json.loads(value)
        return cls(
            name=payload["name"],
            source=payload["source"],
            details=payload["details"],
        )
