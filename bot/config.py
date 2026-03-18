"""
환경변수 및 설정 관리
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # 텔레그램 봇 토큰
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")

    # Google Gemini API 키
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    # OpenWeatherMap API 키
    OPENWEATHER_API_KEY: str = os.getenv("OPENWEATHER_API_KEY", "")

    # 날씨 API 기본 URL
    OPENWEATHER_BASE_URL: str = "https://api.openweathermap.org/data/2.5"

    # SQLite 데이터베이스 경로
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", "data/assistant.db")

    # Gemini 모델명
    GEMINI_MODEL: str = "gemini-1.5-flash"

    # 뉴스 RSS 피드 목록 (한국어 뉴스)
    NEWS_RSS_FEEDS: tuple[str, ...] = (
        "https://feeds.feedburner.com/yonhapnews_all",  # 연합뉴스
        "https://rss.etnews.com/Section901.xml",        # 전자신문 IT
        "https://www.hani.co.kr/rss/",                  # 한겨레
    )

    # 날씨 기본 도시
    DEFAULT_CITY: str = "Seoul"

    # 타임존
    TIMEZONE: str = "Asia/Seoul"

    # Google Calendar OAuth2 credentials 파일 경로 (선택 사항)
    GOOGLE_CALENDAR_CREDENTIALS_PATH: str = os.getenv(
        "GOOGLE_CALENDAR_CREDENTIALS_PATH", ""
    )

    # 봇 명령어 목록
    BOT_COMMANDS: tuple[tuple[str, str], ...] = (
        ("start", "봇 시작 및 도움말"),
        ("help", "사용 가능한 명령어 목록"),
        ("chat", "AI와 대화하기"),
        ("schedule", "일정 관리"),
        ("add_schedule", "일정 추가"),
        ("list_schedule", "일정 목록 조회"),
        ("reminder", "리마인더 설정"),
        ("memo", "메모 관리"),
        ("add_memo", "메모 추가"),
        ("search_memo", "메모 검색"),
        ("weather", "날씨 조회"),
        ("news", "뉴스 요약"),
        ("briefing_on", "모닝 브리핑 구독"),
        ("briefing_off", "모닝 브리핑 해제"),
        ("expense", "지출 기록"),
        ("expense_today", "오늘 지출 조회"),
        ("expense_month", "이번 달 지출 요약"),
    )

    @classmethod
    def validate(cls) -> None:
        """필수 환경변수 검증"""
        missing = []
        if not cls.TELEGRAM_BOT_TOKEN:
            missing.append("TELEGRAM_BOT_TOKEN")
        if not cls.GEMINI_API_KEY:
            missing.append("GEMINI_API_KEY")
        if missing:
            raise ValueError(f"필수 환경변수가 설정되지 않았습니다: {', '.join(missing)}")


config = Config()
