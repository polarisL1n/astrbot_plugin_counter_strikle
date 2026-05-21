from counter_strikle.game import create_game, load_players
from counter_strikle.models import FeedbackKind
from counter_strikle.solver import filter_candidates


def test_guess_feedback_compares_core_fields():
    game = create_game(answer_id="donk")

    result = game.guess("m0NESY")
    feedback = {item.field: item for item in result.feedback}

    assert feedback["age"].kind == FeedbackKind.LOWER
    assert feedback["country"].kind == FeedbackKind.MATCH
    assert feedback["team"].kind == FeedbackKind.MISS
    assert feedback["roles"].kind == FeedbackKind.MISS


def test_solver_keeps_answer_after_feedback():
    game = create_game(answer_id="donk")
    game.guess("m0NESY")

    candidates = filter_candidates(game.players, game.guesses)

    assert "donk" in {player.id for player in candidates}


def test_player_seed_data_has_expected_size_and_unique_ids():
    players = load_players()

    assert len(players) == 100
    assert len({player.id for player in players}) == len(players)
    assert all(player.hint for player in players)
    assert all(player.trivia for player in players)
