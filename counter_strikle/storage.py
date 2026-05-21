from __future__ import annotations

from dataclasses import dataclass, field
from time import time

from .game import CounterStrikleGame, create_game


@dataclass
class Session:
    key: str
    game: CounterStrikleGame
    created_at: float = field(default_factory=time)
    updated_at: float = field(default_factory=time)


class InMemorySessionStore:
    def __init__(self) -> None:
        self._sessions: dict[str, Session] = {}

    def start(self, key: str) -> Session:
        session = Session(key=key, game=create_game())
        self._sessions[key] = session
        return session

    def get(self, key: str) -> Session | None:
        return self._sessions.get(key)

    def end(self, key: str) -> Session | None:
        return self._sessions.pop(key, None)


def build_session_key(platform: str, group_id: str | None, user_id: str) -> str:
    scope = group_id or "private"
    return f"{platform}:{scope}:{user_id}"
