"""
AI 대화 핸들러 - Gemini와 자연어 대화
"""
import logging

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import CommandHandler, ContextTypes, MessageHandler, filters

from bot.services.gemini import gemini_service
from bot.utils.helpers import truncate_text

logger = logging.getLogger(__name__)


async def cmd_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/chat <질문> 명령어 처리"""
    if not update.message:
        return
    if not context.args:
        await update.message.reply_text(
            "사용법: `/chat <질문>`\n\n예: `/chat 파이썬과 자바의 차이점은?`",
            parse_mode="Markdown",
        )
        return

    user_message = " ".join(context.args)
    await _handle_ai_chat(update, context, user_message)


async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """일반 텍스트 메시지를 AI 대화로 처리"""
    if not update.message or not update.message.text:
        return
    # 명령어로 시작하는 메시지는 무시 (다른 핸들러가 처리)
    if update.message.text.startswith("/"):
        return
    await _handle_ai_chat(update, context, update.message.text)


async def _handle_ai_chat(
    update: Update, context: ContextTypes.DEFAULT_TYPE, user_message: str
) -> None:
    """AI 응답 생성 및 전송 공통 로직"""
    if not update.effective_user or not update.message:
        return
    user_id = update.effective_user.id

    await update.effective_chat.send_action(ChatAction.TYPING)

    reply = await gemini_service.chat(user_id, user_message)
    reply = truncate_text(reply)

    try:
        await update.message.reply_text(reply, parse_mode="Markdown")
    except Exception:
        await update.message.reply_text(reply)


async def cmd_clear_history(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/clear 명령어: 대화 기록 초기화"""
    if not update.effective_user or not update.message:
        return
    user_id = update.effective_user.id
    await gemini_service.clear_history(user_id)
    await update.message.reply_text("대화 기록이 초기화되었습니다. 새로운 대화를 시작하세요!")


def get_chat_handlers():
    """채팅 관련 핸들러 목록 반환"""
    return [
        CommandHandler("chat", cmd_chat),
        CommandHandler("clear", cmd_clear_history),
        # 일반 텍스트 메시지 — 명령어가 아닌 일반 텍스트 폴백
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message),
    ]
