"""
APScheduler 기반 리마인더 스케줄러
"""
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from telegram import Bot

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


def start_scheduler(bot: Bot) -> None:
    """스케줄러 시작 및 리마인더 체크 작업 등록"""
    scheduler.add_job(
        check_and_send_reminders,
        trigger=IntervalTrigger(minutes=1),
        args=[bot],
        id="reminder_check",
        replace_existing=True,
        name="리마인더 체크",
    )
    scheduler.start()
    logger.info("스케줄러 시작됨")


def stop_scheduler() -> None:
    """스케줄러 종료"""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("스케줄러 종료됨")
