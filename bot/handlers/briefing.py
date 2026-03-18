"""
모닝 브리핑 구독 핸들러
명령어:
  /briefing_on  - 매일 아침 브리핑 구독 시작
  /briefing_off - 브리핑 구독 해제
"""
import logging

from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

from bot.database import crud

logger = logging.getLogger(__name__)


async def cmd_briefing_on(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/briefing_on — 모닝 브리핑 구독 시작"""
    if not update.effective_user or not update.message:
        return

    user_id = update.effective_user.id
    await crud.subscribe_briefing(user_id)

    await update.message.reply_text(
        "✅ 모닝 브리핑 구독이 시작되었습니다!\n\n"
        "매일 오전 7시에 날씨, 오늘의 일정, 뉴스 요약을 보내드립니다. 🌅\n\n"
        "구독을 해제하려면 `/briefing_off`를 입력하세요.",
        parse_mode="Markdown",
    )
    logger.info("브리핑 구독 등록: user_id=%d", user_id)


async def cmd_briefing_off(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/briefing_off — 모닝 브리핑 구독 해제"""
    if not update.effective_user or not update.message:
        return

    user_id = update.effective_user.id
    await crud.unsubscribe_briefing(user_id)

    await update.message.reply_text(
        "🔕 모닝 브리핑 구독이 해제되었습니다.\n\n"
        "다시 구독하려면 `/briefing_on`을 입력하세요.",
        parse_mode="Markdown",
    )
    logger.info("브리핑 구독 해제: user_id=%d", user_id)


def get_briefing_handlers():
    """브리핑 관련 핸들러 목록 반환"""
    return [
        CommandHandler("briefing_on", cmd_briefing_on),
        CommandHandler("briefing_off", cmd_briefing_off),
    ]
