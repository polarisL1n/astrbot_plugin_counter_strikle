from __future__ import annotations

try:
    from .counter_strikle.solver import filter_candidates, recommend_guess
    from .counter_strikle.storage import InMemorySessionStore, build_session_key
except ImportError:
    from counter_strikle.solver import filter_candidates, recommend_guess
    from counter_strikle.storage import InMemorySessionStore, build_session_key

store = InMemorySessionStore()


def help_text() -> str:
    return "\n".join(
        [
            "Counter-Strikle 新手教程",
            "",
            "玩法：Bot 会随机选一名 CS2 选手，你有 8 次机会猜出答案。",
            "每次猜测后，会根据年龄、国籍、队伍、Major 数量、位置给出反馈。",
            "",
            "反馈说明：",
            "OK = 完全匹配",
            "~ = 半匹配，比如同大洲或位置有重叠",
            "X = 不匹配",
            "UP / DOWN = 答案比你猜的数值更大 / 更小",
            "",
            "常用命令：",
            "/cs开始 - 开始一局",
            "/cs猜 <选手名> - 提交猜测，例如 /cs猜 m0NESY",
            "/cs状态 - 查看当前进度",
            "/cs建议 - 查看下一猜建议",
            "/cs放弃 - 结束当前局并公布答案",
            "/cs帮助 - 查看这份说明",
            "",
            "会话隔离：每个人的游戏互不影响，群里其他人可以正常聊天。",
        ]
    )


def handle_command(command: str, platform: str, user_id: str, group_id: str | None = None) -> str:
    """Framework-agnostic command handler used by the AstrBot adapter."""
    parts = command.strip().split(maxsplit=1)
    action = parts[0] if parts else ""
    arg = parts[1] if len(parts) > 1 else ""
    key = build_session_key(platform, group_id, user_id)

    if action in {"/cs", "/cs帮助", "/cshelp", "/cs help"}:
        return help_text()

    if action == "/cs开始":
        store.start(key)
        return "Counter-Strikle 开始。你有 8 次机会，发送 /cs猜 <选手名>。"

    if action == "/cs放弃":
        session = store.end(key)
        if not session:
            return "你现在没有进行中的 Counter-Strikle。"
        return f"本局结束，答案是 {session.game.answer.name}。"

    session = store.get(key)
    if not session:
        return "你还没有开始游戏，先发送 /cs开始。"

    if action == "/cs状态":
        return f"当前进度：{len(session.game.guesses)}/{session.game.max_guesses}。"

    if action == "/cs建议":
        candidates = filter_candidates(session.game.players, session.game.guesses)
        suggestion = recommend_guess(candidates)
        if suggestion is None:
            return "当前没有可推荐候选，可能数据或反馈规则需要检查。"
        return f"建议下一猜：{suggestion.name}。剩余候选约 {len(candidates)} 人。"

    if action == "/cs猜":
        if not arg:
            return "用法：/cs猜 <选手名>"
        try:
            result = session.game.guess(arg)
        except ValueError as exc:
            return str(exc)

        lines = [
            f"第 {result.guess_count}/{result.max_guesses} 猜：{result.guess.name}",
            *_format_feedback(result),
        ]
        if result.solved:
            store.end(key)
            lines.append("猜中了。")
        elif session.game.is_finished:
            store.end(key)
            lines.append(f"次数用完，答案是 {result.answer.name}。")
        return "\n".join(lines)

    return help_text()


def _format_feedback(result) -> list[str]:
    icons = {
        "match": "OK",
        "partial": "~",
        "miss": "X",
        "higher": "UP",
        "lower": "DOWN",
    }
    return [
        f"{item.field}: {item.guessed} {icons[item.kind.value]} {item.note}".rstrip()
        for item in result.feedback
    ]
