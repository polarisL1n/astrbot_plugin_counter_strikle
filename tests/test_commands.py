from main import handle_command


def test_cs_root_command_returns_onboarding_help():
    text = handle_command("/cs", platform="test", group_id="group-1", user_id="user-1")

    assert "Counter-Strikle 新手教程" in text
    assert "/cs开始" in text
    assert "会话隔离" in text
