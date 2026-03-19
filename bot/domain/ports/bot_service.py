"""
헥사고날 아키텍처 - TeleBot Service Port
텔레그램 봇 도메인 서비스 추상 인터페이스
"""
from abc import abstractmethod
from typing import Any, Dict, Optional

from .base_service import AbstractService


class AbstractBotService(AbstractService):
    """텔레그램 봇 서비스 포트 - 구현체는 이 인터페이스를 따라야 함"""

    @abstractmethod
    async def handle_message(
        self,
        user_id: int,
        message: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        사용자 메시지 처리 및 응답 생성
        :param user_id: 텔레그램 사용자 ID
        :param message: 수신된 메시지 텍스트
        :param context: 대화 컨텍스트 (이전 대화 이력 등)
        :return: 봇 응답 텍스트
        """
        ...

    @abstractmethod
    async def send_notification(
        self,
        user_id: int,
        message: str,
        parse_mode: str = "HTML",
    ) -> bool:
        """
        사용자에게 알림 메시지 전송
        :param user_id: 텔레그램 사용자 ID
        :param message: 전송할 메시지
        :param parse_mode: 메시지 파싱 모드 (HTML, Markdown)
        :return: 전송 성공 여부
        """
        ...

    @abstractmethod
    async def process_command(
        self,
        user_id: int,
        command: str,
        args: Optional[str] = None,
    ) -> str:
        """
        봇 커맨드 처리 (/start, /help, /weather 등)
        :param user_id: 텔레그램 사용자 ID
        :param command: 커맨드명 (슬래시 제외, 예: 'start')
        :param args: 커맨드 인자 문자열
        :return: 커맨드 처리 결과 응답 텍스트
        """
        ...
