from main import handle_command, is_counter_strikle_command, normalize_command


def test_cs_root_command_returns_onboarding_help():
    text = handle_command("/cs", platform="test", group_id="group-1", user_id="user-1")

    assert "Counter-Strikle 新手教程" in text
    assert "/cs开始" in text
    assert "会话隔离" in text


def test_normalize_spaced_commands():
    assert normalize_command("/cs 开始") == "/cs开始"
    assert normalize_command("/cs 猜 monesy") == "/cs猜 monesy"
    assert normalize_command("/cs guess m0NESY") == "/cs猜 m0NESY"


def test_command_prefix_detection():
    assert is_counter_strikle_command("cs")
    assert is_counter_strikle_command("/cs 猜 m0NESY")
    assert is_counter_strikle_command("/cs开始")
    assert not is_counter_strikle_command("今天聊 cs 吗")
    assert not is_counter_strikle_command("/csgo")
