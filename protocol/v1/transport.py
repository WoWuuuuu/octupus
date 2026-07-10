from abc import ABC, abstractmethod
from typing import Optional
import json
import sys

from .messages import ODEPMessage


class Transport(ABC):
    @abstractmethod
    def send(self, message: ODEPMessage) -> None:
        pass

    @abstractmethod
    def receive(self) -> Optional[ODEPMessage]:
        pass

    @abstractmethod
    def close(self) -> None:
        pass


class StdioTransport(Transport):
    def send(self, message: ODEPMessage) -> None:
        print(json.dumps(message.to_dict()))
        sys.stdout.flush()

    def receive(self) -> Optional[ODEPMessage]:
        try:
            line = sys.stdin.readline()
            if not line:
                return None
            data = json.loads(line.strip())
            return ODEPMessage.from_dict(data)
        except (json.JSONDecodeError, EOFError):
            return None

    def close(self) -> None:
        pass