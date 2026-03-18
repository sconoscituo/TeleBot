"""
APScheduler 기반 리마인더 및 모닝 브리핑 스케줄러
"""
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from telegram import Bot

from bot.config import config
from bot.database import crud

logger = logging.getLogger(__name__)

# 전역 스케줄러 인스턴스
scheduler = AsyncIOScheduler(timezone="Asia/Seoul")


async def check_and_send_reminders(bot: Bot) -> None:
    """
    전송되지 않은 리마인더를 조회하여 텔레그램으로 알림 발송
    매 분 실행됨
    """
    try:
        pending = await crud.get_pending_reminders()
        for reminder in pending:
            user_id = reminder["user_id"]
            content = reminder["content"]
            remind_id = reminder["id"]
            remind_at = reminder["remind_at"]

            try:
                await bot.send_message(
                    chat_id=user_id,
                    text=(
                        f"⏰ **리마인더 알림**\n\n"
                        f"📌 {content}\n\n"
                        f"🕐 설정 시각: {remind_at}"
                    ),
                    parse_mode="Markdown",
                )
                await crud.mark_reminder_sent(remind_id)
                logger.info("리마인더 전송 완료: user_id=%d, id=%d", user_id, remind_id)
            except Exception as e:
                logger.error(
                    "리마인더 전송 실패: user_id=%d, id=%d, error=%s",
                    user_id, remind_id, e,
                )
    except Exception as e:
        logger.error("리마인더 조회 실패: %s", e)


async def send_morning_briefing(bot: Bot) -> None:
    """
    매일 07:00 KST에 구독 중인 모든 유저에게 모닝 브리핑 전송
    브리핑 내용: 날씨 + 오늘 일정 + 뉴스 요약
    """
    # 지연 임포트 — 순환 참조 방지 및 선택적 의존성 처리
    from bot.services.weather import get_weather
    from bot.services.news import get_news_summary

    try:
        subscribers = await crud.get_briefing_subscribers()
        if not subscribers:
            logger.info("브리핑 구독자가 없습니다.")
            return

        logger.info("모닝 브리핑 전송 시작: 구독자 %d명", len(subscribers))

        # 공통 콘텐츠 미리 수집 (구독자마다 중복 API 호출 방지)
        today = datetime.now(ZoneInfo(config.TIMEZONE))
        date_str = today.strftime("%Y년 %m월 %d일 (%a)")

        weather_text = await get_weather(config.DEFAULT_CITY)
        news_text = await get_news_summary(max_articles=5)

        for user_id in subscribers:
            try:
                # 해당 유저의 오늘 일정 조회
                schedules = await crud.list_schedules(user_id, only_upcoming=True)
                today_schedules = [
                    s for s in schedules
                    if s["scheduled_at"].startswith(today.strftime("%Y-%m-%d"))
                ]

                if today_schedules:
                    schedule_lines = "\n".join(
                        f"  • {s['scheduled_at'][11:16]} {s['title']}"
                        for s in today_schedules
                    )
                    schedule_section = f"📅 **오늘의 일정**\n{schedule_lines}"
                else:
                    schedule_section = "📅 **오늘의 일정**\n  등록된 일정이 없습니다."

                briefing_message = (
                    f"🌅 **모닝 브리핑 — {date_str}**\n\n"
                    f"{weather_text}\n\n"
                    f"{'─' * 20}\n\n"
                    f"{schedule_section}\n\n"
                    f"{'─' * 20}\n\n"
                    f"{news_text}"
                )

                await bot.send_message(
                    chat_id=user_id,
                    text=briefing_message,
                    parse_mode="Markdown",
                )
                logger.info("브리핑 전송 완료: user_id=%d", user_id)

            except Exception as e:
                logger.error("브리핑 전송 실패: user_id=%d, error=%s", user_id, e)

    except Exception as e:
        logger.error("모닝 브리핑 실행 오류: %s", e)


def start_scheduler(bot: Bot) -> None:
    """스케줄러 시작 — 리마인더 체크 및 모닝 브리핑 작업 등록"""
    # 매 1분마다 리마인더 체크
    scheduler.add_job(
        check_and_send_reminders,
        trigger=IntervalTrigger(minutes=1),
        args=[bot],
        id="reminder_check",
        replace_existing=True,
        name="리마인더 체크",
    )

    # 매일 오전 07:00 KST에 모닝 브리핑 전송
    scheduler.add_job(
        send_morning_briefing,
        trigger=CronTrigger(hour=7, minute=0, timezone="Asia/Seoul"),
        args=[bot],
        id="morning_briefing",
        replace_existing=True,
        name="모닝 브리핑",
    )

    scheduler.start()
    logger.info("스케줄러 시작됨 (리마인더 체크, 모닝 브리핑 07:00 KST)")


def stop_scheduler() -> None:
    """스케줄러 종료"""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("스케줄러 종료됨")
