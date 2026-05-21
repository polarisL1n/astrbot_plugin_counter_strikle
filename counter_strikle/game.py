from __future__ import annotations

import json
import random
from pathlib import Path

from .models import Feedback, FeedbackKind, Player, PlayerGuessResult

DEFAULT_MAX_GUESSES = 8
DATA_PATH = Path(__file__).parent / "data" / "players.json"


def load_players(path: Path = DATA_PATH) -> list[Player]:
    raw_players = json.loads(path.read_text(encoding="utf-8"))
    return [
        Player(
            id=item["id"],
            name=item["name"],
            aliases=tuple(item.get("aliases", [])),
            age=int(item["age"]),
            country=item["country"],
            continent=item["continent"],
            team=item["team"],
            majors=int(item["majors"]),
            roles=tuple(item["roles"]),
        )
        for item in raw_players
    ]


class CounterStrikleGame:
    def __init__(
        self,
        players: list[Player],
        answer: Player,
        max_guesses: int = DEFAULT_MAX_GUESSES,
    ) -> None:
        self.players = players
        self.answer = answer
        self.max_guesses = max_guesses
        self.guesses: list[PlayerGuessResult] = []

    @property
    def is_finished(self) -> bool:
        return self.is_solved or len(self.guesses) >= self.max_guesses

    @property
    def is_solved(self) -> bool:
        return bool(self.guesses and self.guesses[-1].solved)

    def find_player(self, query: str) -> Player | None:
        normalized = normalize_name(query)
        for player in self.players:
            names = (player.name, *player.aliases)
            if normalized in {normalize_name(name) for name in names}:
                return player
        return None

    def guess(self, query: str) -> PlayerGuessResult:
        if self.is_finished:
            raise ValueError("This game has already finished.")

        player = self.find_player(query)
        if player is None:
            raise ValueError(f"Unknown player: {query}")

        solved = player.id == self.answer.id
        result = PlayerGuessResult(
            guess=player,
            answer=self.answer,
            feedback=compare_players(player, self.answer),
            solved=solved,
            guess_count=len(self.guesses) + 1,
            max_guesses=self.max_guesses,
        )
        self.guesses.append(result)
        return result


def create_game(seed: int | None = None, answer_id: str | None = None) -> CounterStrikleGame:
    players = load_players()
    if answer_id:
        answer = next(player for player in players if player.id == answer_id)
    else:
        rng = random.Random(seed)
        answer = rng.choice(players)
    return CounterStrikleGame(players=players, answer=answer)


def compare_players(guess: Player, answer: Player) -> tuple[Feedback, ...]:
    return (
        compare_number("age", guess.age, answer.age),
        compare_country(guess, answer),
        compare_exact("team", guess.team, answer.team),
        compare_number("majors", guess.majors, answer.majors),
        compare_roles(guess.roles, answer.roles),
    )


def compare_number(field: str, guessed: int, target: int) -> Feedback:
    if guessed == target:
        return Feedback(field, guessed, FeedbackKind.MATCH)

    direction = FeedbackKind.HIGHER if target > guessed else FeedbackKind.LOWER
    diff = abs(target - guessed)
    closeness = "close" if diff <= 2 else "far"
    return Feedback(field, guessed, direction, closeness)


def compare_exact(field: str, guessed: str, target: str) -> Feedback:
    kind = FeedbackKind.MATCH if guessed == target else FeedbackKind.MISS
    return Feedback(field, guessed, kind)


def compare_country(guess: Player, answer: Player) -> Feedback:
    if guess.country == answer.country:
        return Feedback("country", guess.country, FeedbackKind.MATCH)
    if guess.continent == answer.continent:
        return Feedback("country", guess.country, FeedbackKind.PARTIAL, "same continent")
    return Feedback("country", guess.country, FeedbackKind.MISS)


def compare_roles(guessed_roles: tuple[str, ...], target_roles: tuple[str, ...]) -> Feedback:
    guessed = set(guessed_roles)
    target = set(target_roles)
    if guessed == target:
        kind = FeedbackKind.MATCH
    elif guessed & target:
        kind = FeedbackKind.PARTIAL
    else:
        kind = FeedbackKind.MISS
    return Feedback("roles", ", ".join(guessed_roles), kind)


def normalize_name(name: str) -> str:
    return name.strip().lower().replace(" ", "")
