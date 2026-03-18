"""
공통 유틸리티 함수
"""
import re
from datetime import datetime
from zoneinfo import ZoneInfo

from bot.config import config


def get_seoul_time() -> datetime:
    """서울 시간 기준 현재 시각 반환"""
    return datetime.now(ZoneInfo(config.TIMEZONE))


def parse_datetime_string(text: str) -> datetime | None:
    """
    자연어 날짜/시간 문자열을 datetime으로 변환
    지원 형식: 'YYYY-MM-DD HH:MM', 'MM-DD HH:MM', 'HH:MM'
    """
    now = get_seoul_time()
    tz = ZoneInfo(config.TIMEZONE)

    # YYYY-MM-DD HH:MM
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})\s+(\d{2}):(\d{2})", text)
    if m:
        y, mo, d, h, mi = map(int, m.groups())
        return datetime(y, mo, d, h, mi, tzinfo=tz)

    # MM-DD HH:MM
    m = re.match(r"(\d{2})-(\d{2})\s+(\d{2}):(\d{2})", text)
    if m:
        mo, d, h, mi = map(int, m.groups())
        return datetime(now.year, mo, d, h, mi, tzinfo=tz)

    # HH:MM (오늘 날짜)
    m = re.match(r"(\d{1,2}):(\d{2})", text)
    if m:
        h, mi = map(int, m.groups())
        return datetime(now.year, now.month, now.day, h, mi, tzinfo=tz)

    return None


def format_datetime(dt: datetime) -> str:
    """datetime을 한국어 형식 문자열로 변환"""
    return dt.strftime("%Y년 %m월 %d일 %H:%M")


def truncate_text(text: str, max_length: int = 4000) -> str:
    """텔레그램 메시지 길이 제한을 위한 텍스트 자르기"""
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."


def build_help_message() -> str:
    """도움말 메시지 생성"""
    return (
        "안녕하세요! 개인 AI 어시스턴트 봇입니다. 🤖\n\n"
        "**사용 가능한 기능:**\n\n"
        "💬 **AI 대화**\n"
        "  `/chat <질문>` — Gemini AI와 대화\n"
        "  또는 그냥 메시지를 보내면 AI가 답변합니다\n\n"
        "📅 **일정 관리**\n"
        "  `/add_schedule <날짜시간> <제목>` — 일정 추가\n"
        "    예: `/add_schedule 2024-12-25 14:00 크리스마스 파티`\n"
        "  `/list_schedule` — 예정된 일정 목록\n"
        "  `/schedule` — 일정 관리 메뉴\n\n"
        "⏰ **리마인더**\n"
        "  `/reminder <날짜시간> <내용>` — 리마인더 설정\n"
        "    예: `/reminder 2024-12-25 09:00 선물 포장하기`\n\n"
        "📝 **메모**\n"
        "  `/add_memo <내용>` — 메모 저장\n"
        "  `/search_memo <키워드>` — 메모 검색\n"
        "  `/memo` — 메모 관리 메뉴\n\n"
        "🌤 **날씨**\n"
        "  `/weather` — 서울 날씨\n"
        "  `/weather <도시명>` — 특정 도시 날씨\n\n"
        "📰 **뉴스**\n"
        "  `/news` — 최신 뉴스 AI 요약\n\n"
        "❓ `/help` — 이 도움말 보기"
    )
