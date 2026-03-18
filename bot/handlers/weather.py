"""
날씨 조회 핸들러
명령어:
  /weather          - 기본 도시(서울) 날씨
  /weather <도시명> - 특정 도시 날씨
"""
import logging

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import CommandHandler, ContextTypes

from bot.config import config
from bot.services.weather import get_weather

logger = logging.getLogger(__name__)


async def cmd_weather(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/weather [도시명] — 날씨 조회"""
    if not update.message:
        return
    city = " ".join(context.args) if context.args else config.DEFAULT_CITY

    await update.effective_chat.send_action(ChatAction.TYPING)
    result = await get_weather(city)

    try:
        await update.message.reply_text(result, parse_mode="Markdown")
    except Exception:
        await update.message.reply_text(result)


def get_weather_handlers():
    """날씨 관련 핸들러 목록 반환"""
    return [
        CommandHandler("weather", cmd_weather),
    ]
