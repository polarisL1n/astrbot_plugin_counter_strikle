from main import handle_command, handle_command_response, is_counter_strikle_command, normalize_command


def test_cs_root_command_returns_onboarding_help():
    text = handle_command("猜选手", platform="test", group_id="group-1", user_id="user-1")

    assert "Counter-Strikle 新手教程" in text
    assert "猜选手 开始" in text
    assert "会话隔离" in text


def test_normalize_spaced_commands():
    assert normalize_command("/cs 开始") == "/cs开始"
    assert normalize_command("/cs 猜 monesy") == "/cs猜 monesy"
    assert normalize_command("/cs guess m0NESY") == "/cs猜 m0NESY"
    assert normalize_command("猜选手 开始") == "/cs开始"
    assert normalize_command("猜选手 猜 monesy") == "/cs猜 monesy"
    assert normalize_command("猜选手 guess m0NESY") == "/cs猜 m0NESY"


def test_command_prefix_detection():
    assert is_counter_strikle_command("cs")
    assert is_counter_strikle_command("猜选手")
    assert is_counter_strikle_command("猜选手 猜 m0NESY")
    assert is_counter_strikle_command("/cs 猜 m0NESY")
    assert is_counter_strikle_command("/cs开始")
    assert not is_counter_strikle_command("今天聊 cs 吗")
    assert not is_counter_strikle_command("我要猜选手吗")
    assert not is_counter_strikle_command("/csgo")


def test_guess_response_includes_short_commentary():
    handle_command("猜选手 开始", platform="comment-test", group_id="group-1", user_id="user-1")

    text = handle_command("猜选手 猜 m0NESY", platform="comment-test", group_id="group-1", user_id="user-1")

    assert "评价：" in text


def test_fourth_guess_response_includes_hint():
    handle_command("/cs开始", platform="hint-test", group_id="group-1", user_id="user-1")
    for name in ["m0NESY", "ZywOo", "NiKo"]:
        handle_command(f"/cs猜 {name}", platform="hint-test", group_id="group-1", user_id="user-1")

    text = handle_command("/cs猜 ropz", platform="hint-test", group_id="group-1", user_id="user-1")

    assert "提示：" in text


def test_guess_response_exposes_llm_prompt_for_adapter():
    handle_command("/cs开始", platform="llm-test", group_id="group-1", user_id="user-1")

    response = handle_command_response(
        "/cs猜 m0NESY",
        platform="llm-test",
        group_id="group-1",
        user_id="user-1",
    )

    assert response.llm_prompt
    assert response.llm_fallback
