"""
Google Gemini API 클라이언트
"""
import logging

import google.generativeai as genai

from bot.config import config
from bot.database import crud

logger = logging.getLogger(__name__)


class GeminiService:
    """Gemini AI 서비스 (지연 초기화)"""

    def __init__(self) -> None:
        self._model = None

    def _ensure_initialized(self) -> None:
        if self._model is None:
            genai.configure(api_key=config.GEMINI_API_KEY)
            self._model = genai.GenerativeModel(
                model_name=config.GEMINI_MODEL,
                system_instruction=(
                    "당신은 친절하고 유능한 한국어 개인 AI 어시스턴트입니다. "
                    "사용자의 질문에 명확하고 간결하게 답변하세요. "
                    "필요한 경우 마크다운 형식을 사용해 답변을 구조화하세요."
                ),
            )

    @property
    def model(self):
        self._ensure_initialized()
        return self._model

    async def chat(self, user_id: int, user_message: str) -> str:
        """
        대화 기록을 포함한 Gemini 채팅 응답 생성
        """
        try:
            # 최근 대화 기록 불러오기
            history_rows = await crud.get_chat_history(user_id, limit=10)
            history = [
                {"role": row["role"], "parts": [row["message"]]}
                for row in history_rows
            ]

            chat_session = self.model.start_chat(history=history)
            response = await chat_session.send_message_async(user_message)
            reply = response.text

            # 대화 기록 저장
            await crud.save_chat_message(user_id, "user", user_message)
            await crud.save_chat_message(user_id, "model", reply)

            return reply

        except Exception as e:
            logger.error("Gemini 응답 생성 실패: %s", e)
            return f"AI 응답 생성 중 오류가 발생했습니다: {e}"

    async def summarize(self, text: str, prompt_prefix: str = "") -> str:
        """
        주어진 텍스트를 요약하는 단순 생성 호출
        """
        try:
            prompt = (prompt_prefix + "\n\n" + text) if prompt_prefix else text
            response = await self.model.generate_content_async(prompt)
            return response.text
        except Exception as e:
            logger.error("Gemini 요약 실패: %s", e)
            return f"요약 중 오류가 발생했습니다: {e}"

    async def clear_history(self, user_id: int) -> None:
        """사용자 대화 기록 초기화"""
        await crud.clear_chat_history(user_id)


# 싱글톤 인스턴스
gemini_service = GeminiService()
