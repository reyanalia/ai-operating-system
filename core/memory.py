from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class MemoryEntry:
    key: str
    value: Any
    agent: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class Memory:
    """Shared in-session key-value store and task history for all agents."""

    def __init__(self) -> None:
        self._store: dict[str, MemoryEntry] = {}
        self._history: list[dict] = []

    def set(self, key: str, value: Any, agent: str = "") -> None:
        self._store[key] = MemoryEntry(key=key, value=value, agent=agent)

    def get(self, key: str, default: Any = None) -> Any:
        entry = self._store.get(key)
        return entry.value if entry else default

    def delete(self, key: str) -> None:
        self._store.pop(key, None)

    def append_history(self, entry: dict) -> None:
        self._history.append({**entry, "timestamp": datetime.now().isoformat()})

    def get_history(self, limit: int = 10) -> list[dict]:
        return self._history[-limit:]

    def snapshot(self) -> dict:
        return {k: v.value for k, v in self._store.items()}

    def clear(self) -> None:
        self._store.clear()
        self._history.clear()
