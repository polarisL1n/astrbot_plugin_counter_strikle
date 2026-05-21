from __future__ import annotations

from difflib import get_close_matches

from .game import normalize_name
from .models import Player


def player_search_terms(player: Player) -> tuple[str, ...]:
    return (player.name, player.id, *player.aliases)


def suggest_players(query: str, players: list[Player], limit: int = 5) -> list[Player]:
    normalized_to_player: dict[str, Player] = {}
    for player in players:
        for term in player_search_terms(player):
            normalized_to_player[normalize_name(term)] = player

    matches = get_close_matches(
        normalize_name(query),
        list(normalized_to_player.keys()),
        n=max(limit * 3, limit),
        cutoff=0.45,
    )
    suggestions: list[Player] = []
    seen: set[str] = set()
    for match in matches:
        player = normalized_to_player[match]
        if player.id in seen:
            continue
        suggestions.append(player)
        seen.add(player.id)
        if len(suggestions) >= limit:
            break
    return suggestions
