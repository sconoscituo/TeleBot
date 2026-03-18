"""
Google Calendar API 연동 서비스
GOOGLE_CALENDAR_CREDENTIALS_PATH 환경변수가 설정되어 있을 때만 동작합니다.
"""
import logging
import os
from datetime import datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo

from bot.config import config

logger = logging.getLogger(__name__)

# Google Calendar API 관련 라이브러리는 선택적 의존성으로 처리
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build

    GOOGLE_CALENDAR_AVAILABLE = True
except ImportError:
    GOOGLE_CALENDAR_AVAILABLE = False
    logger.warning(
        "Google Calendar 라이브러리가 설치되지 않았습니다. "
        "pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib"
    )

# Google Calendar API 접근 범위
SCOPES = ["https://www.googleapis.com/auth/calendar"]

# 토큰 저장 경로 (credentials 파일과 같은 디렉토리)
TOKEN_FILE = "data/google_token.json"


def _is_available() -> bool:
    """Google Calendar 연동 가능 여부 확인"""
    if not GOOGLE_CALENDAR_AVAILABLE:
        return False
    if not config.GOOGLE_CALENDAR_CREDENTIALS_PATH:
        return False
    if not os.path.exists(config.GOOGLE_CALENDAR_CREDENTIALS_PATH):
        logger.warning(
            "Google Calendar credentials 파일을 찾을 수 없습니다: %s",
            config.GOOGLE_CALENDAR_CREDENTIALS_PATH,
        )
        return False
    return True


def _get_credentials() -> "Credentials | None":
    """Google OAuth2 인증 정보 반환 (토큰 자동 갱신)"""
    if not _is_available():
        return None

    creds = None

    # 저장된 토큰이 있으면 불러오기
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)  # type: ignore[attr-defined]

    # 토큰이 없거나 만료된 경우 갱신
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())  # type: ignore[attr-defined]
            except Exception as e:
                logger.error("토큰 갱신 실패: %s", e)
                return None
        else:
            # 최초 인증 (서버 환경에서는 수동 처리 필요)
            try:
                flow = InstalledAppFlow.from_client_secrets_file(  # type: ignore[attr-defined]
                    config.GOOGLE_CALENDAR_CREDENTIALS_PATH, SCOPES
                )
                creds = flow.run_local_server(port=0)
            except Exception as e:
                logger.error("Google OAuth 인증 실패: %s", e)
                return None

        # 토큰 저장
        os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)
        with open(TOKEN_FILE, "w") as token_file:
            token_file.write(creds.to_json())

    return creds


def _get_service() -> Any:
    """Google Calendar API 서비스 객체 반환"""
    creds = _get_credentials()
    if creds is None:
        return None
    try:
        return build("calendar", "v3", credentials=creds)  # type: ignore[attr-defined]
    except Exception as e:
        logger.error("Google Calendar 서비스 생성 실패: %s", e)
        return None


async def add_event_to_calendar(
    title: str,
    scheduled_at: datetime,
    duration_minutes: int = 60,
    description: str = "",
) -> str | None:
    """
    구글 캘린더에 일정 추가
    성공 시 이벤트 ID 반환, 실패 또는 미설정 시 None 반환
    """
    if not _is_available():
        return None

    import asyncio

    service = _get_service()
    if service is None:
        return None

    tz_str = config.TIMEZONE
    tz = ZoneInfo(tz_str)

    # datetime에 타임존이 없으면 KST 적용
    if scheduled_at.tzinfo is None:
        scheduled_at = scheduled_at.replace(tzinfo=tz)

    end_time = scheduled_at + timedelta(minutes=duration_minutes)

    event_body = {
        "summary": title,
        "description": description,
        "start": {
            "dateTime": scheduled_at.isoformat(),
            "timeZone": tz_str,
        },
        "end": {
            "dateTime": end_time.isoformat(),
            "timeZone": tz_str,
        },
    }

    try:
        # googleapiclient은 동기 라이브러리이므로 executor에서 실행
        loop = asyncio.get_running_loop()
        event = await loop.run_in_executor(
            None,
            lambda: service.events().insert(calendarId="primary", body=event_body).execute(),
        )
        event_id = event.get("id")
        logger.info("구글 캘린더 일정 추가 완료: title=%s, id=%s", title, event_id)
        return event_id
    except Exception as e:
        logger.error("구글 캘린더 일정 추가 실패: %s", e)
        return None


async def get_today_events() -> list[dict[str, Any]]:
    """
    오늘 구글 캘린더 일정 조회
    반환값: [{"title": str, "start": str, "end": str}, ...]
    """
    if not _is_available():
        return []

    import asyncio

    service = _get_service()
    if service is None:
        return []

    tz = ZoneInfo(config.TIMEZONE)
    now = datetime.now(tz)
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=0)

    try:
        loop = asyncio.get_running_loop()
        events_result = await loop.run_in_executor(
            None,
            lambda: service.events()
            .list(
                calendarId="primary",
                timeMin=start_of_day.isoformat(),
                timeMax=end_of_day.isoformat(),
                singleEvents=True,
                orderBy="startTime",
            )
            .execute(),
        )
        items = events_result.get("items", [])
        result = []
        for item in items:
            start = item["start"].get("dateTime", item["start"].get("date", ""))
            end = item["end"].get("dateTime", item["end"].get("date", ""))
            result.append(
                {
                    "title": item.get("summary", "제목 없음"),
                    "start": start,
                    "end": end,
                }
            )
        return result
    except Exception as e:
        logger.error("구글 캘린더 일정 조회 실패: %s", e)
        return []
