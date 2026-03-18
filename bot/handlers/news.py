"""
뉴스 요약 핸들러
명령어:
  /news - 최신 뉴스 수집 및 AI 요약
"""
import logging

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import CommandHandler, ContextTypes

from bot.services.news import get_news_summary
from bot.utils.helpers import truncate_text

logger = logging.getLogger(__name__)


async def cmd_news(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/news — 최신 뉴스 AI 요약"""
    if not update.message:
        return
    await update.effective_chat.send_action(ChatAction.TYPING)
    await update.message.reply_text("📰 뉴스를 수집하고 요약 중입니다... 잠시만 기다려주세요.")

    summary = await get_news_summary()
    summary = truncate_text(summary)

    try:
        await update.message.reply_text(summary, parse_mode="Markdown")
    except Exception:
        await update.message.reply_text(summary)


def get_news_handlers():
    """뉴스 관련 핸들러 목록 반환"""
    return [
        CommandHandler("news", cmd_news),
    ]
