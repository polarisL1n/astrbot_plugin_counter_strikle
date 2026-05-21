from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class FeedbackKind(StrEnum):
    MATCH = "match"
    PARTIAL = "partial"
    MISS = "miss"
    HIGHER = "higher"
    LOWER = "lower"


@dataclass(frozen=True)
class Player:
    id: str
    name: str
    aliases: tuple[str, ...]
    age: int
    country: str
    continent: str
    team: str
    majors: int
    roles: tuple[str, ...]
    hint: str = ""
    trivia: str = ""


@dataclass(frozen=True)
class Feedback:
    field: str
    guessed: str | int
    kind: FeedbackKind
    note: str = ""


@dataclass(frozen=True)
class PlayerGuessResult:
    guess: Player
    answer: Player
    feedback: tuple[Feedback, ...]
    solved: bool
    guess_count: int
    max_guesses: int
