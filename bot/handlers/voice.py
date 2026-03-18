"""
음성 메시지 인식 핸들러
텔레그램 음성 메시지를 수신하여 Gemini로 텍스트 변환 후 AI 대화로 처리합니다.
"""
import logging
import os
import tempfile

import google.generativeai as genai
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes, MessageHandler, filters

from bot.config import config
from bot.services.gemini import gemini_service

logger = logging.getLogger(__name__)


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """음성 메시지 수신 → Gemini 텍스트 변환 → AI 응답"""
    if not update.message or not update.message.voice or not update.effective_user:
        return

    user_id = update.effective_user.id
    voice = update.message.voice

    # 처리 중 타이핑 표시
    await update.effective_chat.send_action(ChatAction.TYPING)

    # 임시 파일에 음성 다운로드
    tmp_path = None
    try:
        voice_file = await context.bot.get_file(voice.file_id)

        with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as tmp:
            tmp_path = tmp.name

        await voice_file.download_to_drive(tmp_path)
        logger.info("음성 파일 다운로드 완료: user_id=%d, path=%s", user_id, tmp_path)

        # Gemini API 초기화 확인
        genai.configure(api_key=config.GEMINI_API_KEY)

        # Gemini Files API로 음성 업로드 후 텍스트 변환
        uploaded = genai.upload_file(path=tmp_path, mime_type="audio/ogg")
        model = genai.GenerativeModel(model_name=config.GEMINI_MODEL)
        transcription_response = await model.generate_content_async(
            [
                uploaded,
                "이 음성을 한국어로 텍스트로 변환해주세요. "
                "변환된 텍스트만 출력하고 다른 설명은 하지 마세요.",
            ]
        )
        transcribed_text = transcription_response.text.strip()

        if not transcribed_text:
            await update.message.reply_text(
                "음성을 인식하지 못했습니다. 더 명확하게 말씀해주세요. 🎙️"
            )
            return

        # 인식된 텍스트 안내
        await update.message.reply_text(
            f"🎙️ **인식된 텍스트:**\n_{transcribed_text}_",
            parse_mode="Markdown",
        )

        # AI 대화 처리
        await update.effective_chat.send_action(ChatAction.TYPING)
        ai_reply = await gemini_service.chat(user_id, transcribed_text)

        await update.message.reply_text(ai_reply, parse_mode="Markdown")
        logger.info("음성 메시지 처리 완료: user_id=%d", user_id)

    except Exception as e:
        logger.error("음성 메시지 처리 오류: user_id=%d, error=%s", user_id, e)
        await update.message.reply_text(
            "음성 메시지 처리 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요. 😥"
        )
    finally:
        # 임시 파일 삭제
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass


def get_voice_handlers():
    """음성 관련 핸들러 목록 반환"""
    return [
        MessageHandler(filters.VOICE, handle_voice),
    ]
