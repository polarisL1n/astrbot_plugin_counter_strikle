from __future__ import annotations

from dataclasses import dataclass
from typing import Any

try:
    from .counter_strikle.commentary import (
        build_llm_comment_prompt,
        player_hint,
        sanitize_llm_comment,
        should_show_hint,
        template_comment,
    )
    from .counter_strikle.solver import filter_candidates, recommend_guess
    from .counter_strikle.storage import InMemorySessionStore, build_session_key
except ImportError:
    from counter_strikle.commentary import (
        build_llm_comment_prompt,
        player_hint,
        sanitize_llm_comment,
        should_show_hint,
        template_comment,
    )
    from counter_strikle.solver import filter_candidates, recommend_guess
    from counter_strikle.storage import InMemorySessionStore, build_session_key

try:
    from astrbot.api.event import AstrMessageEvent, filter
    from astrbot.api.star import Context, Star
except ImportError:
    AstrMessageEvent = Any
    Context = Any
    Star = object
    filter = None

store = InMemorySessionStore()


@dataclass(frozen=True)
class CommandResponse:
    text: str
    llm_prompt: str | None = None
    llm_fallback: str = ""


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
            "猜选手 - 查看这份说明",
            "猜选手 开始 - 开始一局",
            "猜选手 猜 <选手名> - 提交猜测，例如 猜选手 猜 m0NESY",
            "猜选手 状态 - 查看当前进度",
            "猜选手 建议 - 查看下一猜建议",
            "猜选手 放弃 - 结束当前局并公布答案",
            "猜选手 帮助 - 查看这份说明",
            "",
            "兼容命令：cs、/cs、/cs开始、/cs猜 <选手名>",
            "",
            "会话隔离：每个人的游戏互不影响，群里其他人可以正常聊天。",
        ]
    )


def handle_command(command: str, platform: str, user_id: str, group_id: str | None = None) -> str:
    return handle_command_response(command, platform, user_id, group_id).text


def handle_command_response(
    command: str,
    platform: str,
    user_id: str,
    group_id: str | None = None,
    *,
    enable_template_commentary: bool = True,
    enable_hints: bool = True,
    llm_comment_max_chars: int = 32,
) -> CommandResponse:
    """Framework-agnostic command handler used by the AstrBot adapter."""
    command = normalize_command(command)
    parts = command.split(maxsplit=1)
    action = parts[0] if parts else ""
    arg = parts[1] if len(parts) > 1 else ""
    key = build_session_key(platform, group_id, user_id)

    if action in {"/cs", "/cs帮助", "/cshelp", "/cs help"}:
        return CommandResponse(help_text())

    if action == "/cs开始":
        store.start(key)
        return CommandResponse("Counter-Strikle 开始。你有 8 次机会，发送 猜选手 猜 <选手名>。")

    if action == "/cs放弃":
        session = store.end(key)
        if not session:
            return CommandResponse("你现在没有进行中的 Counter-Strikle。")
        return CommandResponse(f"本局结束，答案是 {session.game.answer.name}。")

    session = store.get(key)
    if not session:
        return CommandResponse("你还没有开始游戏，先发送 猜选手 开始。")

    if action == "/cs状态":
        return CommandResponse(f"当前进度：{len(session.game.guesses)}/{session.game.max_guesses}。")

    if action == "/cs建议":
        candidates = filter_candidates(session.game.players, session.game.guesses)
        suggestion = recommend_guess(candidates)
        if suggestion is None:
            return CommandResponse("当前没有可推荐候选，可能数据或反馈规则需要检查。")
        return CommandResponse(f"建议下一猜：{suggestion.name}。剩余候选约 {len(candidates)} 人。")

    if action == "/cs猜":
        if not arg:
            return CommandResponse("用法：猜选手 猜 <选手名>")
        try:
            result = session.game.guess(arg)
        except ValueError as exc:
            return CommandResponse(str(exc))

        lines = [
            f"第 {result.guess_count}/{result.max_guesses} 猜：{result.guess.name}",
            *_format_feedback(result),
        ]
        fallback_comment = template_comment(result)
        if enable_template_commentary:
            lines.append("")
            lines.append(f"评价：{fallback_comment}")
        if enable_hints and should_show_hint(result):
            lines.append(f"提示：{player_hint(result)}")
        if result.solved:
            store.end(key)
            lines.append("猜中了。")
        elif session.game.is_finished:
            store.end(key)
            lines.append(f"次数用完，答案是 {result.answer.name}。")
        return CommandResponse(
            "\n".join(lines),
            llm_prompt=build_llm_comment_prompt(result, fallback_comment, llm_comment_max_chars),
            llm_fallback=fallback_comment,
        )

    return CommandResponse(help_text())


def normalize_command(message: str) -> str:
    stripped = message.strip()
    lowered = stripped.lower()
    compact_commands = {
        "cs": "/cs",
        "猜选手": "/cs",
        "猜选手 help": "/cs",
        "猜选手 帮助": "/cs",
        "猜选手开始": "/cs开始",
        "猜选手 开始": "/cs开始",
        "猜选手 start": "/cs开始",
        "猜选手状态": "/cs状态",
        "猜选手 状态": "/cs状态",
        "猜选手 status": "/cs状态",
        "猜选手建议": "/cs建议",
        "猜选手 建议": "/cs建议",
        "猜选手 hint": "/cs建议",
        "猜选手放弃": "/cs放弃",
        "猜选手 放弃": "/cs放弃",
        "猜选手 giveup": "/cs放弃",
        "/cs": "/cs",
        "/cs help": "/cs",
        "/cs 帮助": "/cs",
        "/cs开始": "/cs开始",
        "/cs 开始": "/cs开始",
        "/csstart": "/cs开始",
        "/cs start": "/cs开始",
        "/cs状态": "/cs状态",
        "/cs 状态": "/cs状态",
        "/csstatus": "/cs状态",
        "/cs status": "/cs状态",
        "/cs建议": "/cs建议",
        "/cs 建议": "/cs建议",
        "/cshint": "/cs建议",
        "/cs hint": "/cs建议",
        "/cs放弃": "/cs放弃",
        "/cs 放弃": "/cs放弃",
        "/csgiveup": "/cs放弃",
        "/cs giveup": "/cs放弃",
        "/cs帮助": "/cs",
        "/cshelp": "/cs",
    }
    if lowered in compact_commands:
        return compact_commands[lowered]

    for prefix in ("/cs猜 ", "/cs 猜 ", "/csguess ", "/cs guess "):
        if lowered.startswith(prefix):
            return f"/cs猜 {stripped[len(prefix):].strip()}"
    for prefix in ("猜选手猜 ", "猜选手 猜 ", "猜选手 guess "):
        if lowered.startswith(prefix):
            return f"/cs猜 {stripped[len(prefix):].strip()}"

    return stripped


def is_counter_strikle_command(message: str) -> bool:
    stripped = message.strip()
    lowered = stripped.lower()
    return (
        lowered == "cs"
        or lowered == "/cs"
        or lowered == "猜选手"
        or lowered.startswith("猜选手 ")
        or lowered.startswith(("猜选手开始", "猜选手猜", "猜选手状态", "猜选手建议", "猜选手放弃", "猜选手帮助"))
        or lowered.startswith("/cs ")
        or lowered.startswith(
        ("/cs开始", "/cs猜", "/cs状态", "/cs建议", "/cs放弃", "/cs帮助", "/cshelp")
    )
    )


def get_event_identity(event: AstrMessageEvent) -> tuple[str, str, str | None]:
    message_obj = getattr(event, "message_obj", None)
    platform = (
        _call_or_none(event, "get_platform_name")
        or _get_nested(message_obj, "platform_name")
        or _get_nested(message_obj, "adapter")
        or "astrbot"
    )
    user_id = (
        _call_or_none(event, "get_sender_id")
        or _get_nested(message_obj, "sender.user_id")
        or _get_nested(message_obj, "sender_id")
        or _get_nested(message_obj, "user_id")
        or _call_or_none(event, "get_sender_name")
        or "unknown-user"
    )
    group_id = (
        _call_or_none(event, "get_group_id")
        or _get_nested(message_obj, "group_id")
        or _get_nested(message_obj, "raw_message.group_id")
    )
    return str(platform), str(user_id), str(group_id) if group_id else None


def _call_or_none(obj: object, method_name: str) -> object | None:
    method = getattr(obj, method_name, None)
    if not callable(method):
        return None
    try:
        return method()
    except Exception:
        return None


def _get_nested(obj: object, path: str) -> object | None:
    current = obj
    for part in path.split("."):
        if current is None:
            return None
        if isinstance(current, dict):
            current = current.get(part)
        else:
            current = getattr(current, part, None)
    return current


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


class CounterStriklePlugin(Star):
    def __init__(self, context: Context, config: Any = None):
        super().__init__(context)
        self.config = config or {}

    if filter is not None:

        @filter.event_message_type(filter.EventMessageType.ALL)
        async def on_message(self, event: AstrMessageEvent):
            """处理 Counter-Strikle 指令。"""
            message = getattr(event, "message_str", "")
            if not is_counter_strikle_command(message):
                return

            platform, user_id, group_id = get_event_identity(event)
            response = handle_command_response(
                message,
                platform=platform,
                user_id=user_id,
                group_id=group_id,
                enable_template_commentary=bool(self.config.get("enable_template_commentary", True)),
                enable_hints=bool(self.config.get("enable_hints", True)),
                llm_comment_max_chars=int(self.config.get("llm_comment_max_chars", 32)),
            )
            text = response.text
            if self.config.get("enable_llm_commentary", False) and response.llm_prompt:
                llm_comment = await self._generate_llm_comment(event, response)
                if llm_comment:
                    text = replace_comment_line(text, llm_comment)
            event.stop_event()
            yield event.plain_result(text)

    async def _generate_llm_comment(
        self,
        event: AstrMessageEvent,
        response: CommandResponse,
    ) -> str | None:
        try:
            provider_id = await self.context.get_current_chat_provider_id(umo=event.unified_msg_origin)
            if not provider_id:
                return None
            llm_resp = await self.context.llm_generate(
                chat_provider_id=provider_id,
                prompt=response.llm_prompt,
            )
            return sanitize_llm_comment(
                getattr(llm_resp, "completion_text", ""),
                response.llm_fallback,
                int(self.config.get("llm_comment_max_chars", 32)),
            )
        except Exception:
            return None


def replace_comment_line(text: str, comment: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.startswith("评价："):
            lines[index] = f"评价：{comment}"
            return "\n".join(lines)
    return f"{text}\n评价：{comment}"
