"""
AI 번역 핸들러
명령어:
  /translate 안녕하세요 — 한국어 → 영어
  /translate Hello world — 영어 → 한국어
Gemini를 사용해 언어를 자동 감지하고 번역합니다.
"""
import logging

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import CommandHandler, ContextTypes

from bot.services.gemini import gemini_service

logger = logging.getLogger(__name__)

_TRANSLATE_PROMPT = """\
다음 텍스트의 언어를 자동으로 감지하세요.
- 한국어이면 영어로 번역하세요.
- 영어이면 한국어로 번역하세요.
- 그 외 언어이면 한국어와 영어 두 가지로 번역하세요.

번역 결과만 출력하세요. 설명이나 부연은 필요 없습니다.

텍스트:
"""


async def cmd_translate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/translate <텍스트> — AI 자동 번역 (한↔영)"""
    if not update.message:
        return

    if not context.args:
        await update.message.reply_text(
            "사용법: `/translate 번역할 텍스트`\n"
            "한국어는 영어로, 영어는 한국어로 자동 번역합니다.",
            parse_mode="Markdown",
        )
        return

    text = " ".join(context.args)

    await update.effective_chat.send_action(ChatAction.TYPING)

    result = await gemini_service.summarize(text, prompt_prefix=_TRANSLATE_PROMPT)

    try:
        await update.message.reply_text(result, parse_mode="Markdown")
    except Exception:
        await update.message.reply_text(result)


def get_translate_handlers():
    """번역 관련 핸들러 목록 반환"""
    return [
        CommandHandler("translate", cmd_translate),
    ]
