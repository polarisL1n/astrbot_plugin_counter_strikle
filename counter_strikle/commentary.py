from __future__ import annotations

from .models import FeedbackKind, PlayerGuessResult


def template_comment(result: PlayerGuessResult) -> str:
    if result.solved:
        return "可以，这都被你锁到了。"

    feedback = result.feedback
    matches = sum(item.kind == FeedbackKind.MATCH for item in feedback)
    partials = sum(item.kind == FeedbackKind.PARTIAL for item in feedback)
    close_numbers = sum(
        item.kind in {FeedbackKind.HIGHER, FeedbackKind.LOWER} and item.note == "close"
        for item in feedback
    )

    score = matches * 2 + partials + close_numbers
    if score >= 5:
        return "这手很接近了，已经闻到答案味了。"
    if score >= 3:
        return "方向不算歪，可以继续顺着这个线摸。"
    if result.guess_count <= 2:
        return "前期试探可以，先把范围切开。"
    return "这手有点飞，但排除信息也算信息。"


def should_show_hint(result: PlayerGuessResult, hint_after_guesses: int = 4) -> bool:
    return result.guess_count == hint_after_guesses and not result.solved


def player_hint(result: PlayerGuessResult) -> str:
    return result.answer.hint or result.answer.trivia or "这名选手在顶级赛事里有比较鲜明的个人标签。"


def build_llm_comment_prompt(result: PlayerGuessResult, fallback: str, max_chars: int) -> str:
    feedback_lines = "; ".join(
        f"{item.field}={item.kind.value}{'(' + item.note + ')' if item.note else ''}"
        for item in result.feedback
    )
    return "\n".join(
        [
            "你是群聊里的 CS2 猜选手小游戏主持人。",
            "请根据当前机器人原本人设口吻，生成一句很短的猜测评价。",
            "要求：只输出一句话；不要超过指定字数；不要透露答案；不要复述完整反馈；不要加解释。",
            f"字数上限：{max_chars}",
            f"当前第 {result.guess_count}/{result.max_guesses} 猜",
            f"玩家猜测：{result.guess.name}",
            f"是否猜中：{result.solved}",
            f"结构化反馈：{feedback_lines}",
            f"本地备用评价：{fallback}",
        ]
    )


def sanitize_llm_comment(text: str, fallback: str, max_chars: int) -> str:
    cleaned = text.strip().splitlines()[0].strip("「」\"' ")
    if not cleaned:
        return fallback
    if len(cleaned) > max_chars:
        return cleaned[:max_chars].rstrip() + "..."
    return cleaned
