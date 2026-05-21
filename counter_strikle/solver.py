from __future__ import annotations

from .models import FeedbackKind, Player, PlayerGuessResult


def filter_candidates(players: list[Player], results: list[PlayerGuessResult]) -> list[Player]:
    candidates = players
    for result in results:
        candidates = [player for player in candidates if is_candidate_compatible(player, result)]
    return candidates


def is_candidate_compatible(candidate: Player, result: PlayerGuessResult) -> bool:
    guess = result.guess
    feedback_by_field = {item.field: item for item in result.feedback}

    age = feedback_by_field["age"]
    if age.kind == FeedbackKind.MATCH and candidate.age != guess.age:
        return False
    if age.kind == FeedbackKind.HIGHER and candidate.age <= guess.age:
        return False
    if age.kind == FeedbackKind.LOWER and candidate.age >= guess.age:
        return False

    country = feedback_by_field["country"]
    if country.kind == FeedbackKind.MATCH and candidate.country != guess.country:
        return False
    if country.kind == FeedbackKind.PARTIAL and (
        candidate.country == guess.country or candidate.continent != guess.continent
    ):
        return False
    if country.kind == FeedbackKind.MISS and candidate.continent == guess.continent:
        return False

    team = feedback_by_field["team"]
    if team.kind == FeedbackKind.MATCH and candidate.team != guess.team:
        return False
    if team.kind == FeedbackKind.MISS and candidate.team == guess.team:
        return False

    majors = feedback_by_field["majors"]
    if majors.kind == FeedbackKind.MATCH and candidate.majors != guess.majors:
        return False
    if majors.kind == FeedbackKind.HIGHER and candidate.majors <= guess.majors:
        return False
    if majors.kind == FeedbackKind.LOWER and candidate.majors >= guess.majors:
        return False

    roles = feedback_by_field["roles"]
    candidate_roles = set(candidate.roles)
    guess_roles = set(guess.roles)
    if roles.kind == FeedbackKind.MATCH and candidate_roles != guess_roles:
        return False
    if roles.kind == FeedbackKind.PARTIAL and not (candidate_roles & guess_roles):
        return False
    if roles.kind == FeedbackKind.MISS and candidate_roles & guess_roles:
        return False

    return True


def recommend_guess(candidates: list[Player]) -> Player | None:
    if not candidates:
        return None
    return sorted(candidates, key=lambda player: (player.team, player.country, player.name))[0]
