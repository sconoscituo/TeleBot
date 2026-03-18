"""
봇 진입점 - Application 빌드 및 실행
"""
import logging
import sys

from telegram import BotCommand, Update
from telegram.ext import Application, CommandHandler, ContextTypes

from bot.config import config
from bot.database.models import init_database
from bot.handlers.chat import get_chat_handlers
from bot.handlers.memo import get_memo_handlers
from bot.handlers.news import get_news_handlers
from bot.handlers.reminder import get_reminder_handlers
from bot.handlers.schedule import get_schedule_handlers
from bot.handlers.weather import get_weather_handlers
from bot.services.scheduler import start_scheduler, stop_scheduler
from bot.utils.helpers import build_help_message

# 로깅 설정
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# 공통 명령어 핸들러
# ─────────────────────────────────────────────

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/start — 봇 시작 인사 및 도움말"""
    if not update.message:
        return
    user = update.effective_user
    name = user.first_name if user else "사용자"
    await update.message.reply_text(
        f"안녕하세요, {name}님! 👋\n\n" + build_help_message(),
        parse_mode="Markdown",
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/help — 도움말"""
    if not update.message:
        return
    await update.message.reply_text(
        build_help_message(),
        parse_mode="Markdown",
    )


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """전역 에러 핸들러"""
    logger.error("Update '%s' caused error: %s", update, context.error, exc_info=context.error)
    if isinstance(update, Update) and update.message:
        await update.message.reply_text(
            "처리 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
        )


# ─────────────────────────────────────────────
# 봇 커맨드 메타 등록
# ─────────────────────────────────────────────

async def post_init(application: Application) -> None:
    """봇 초기화 완료 후 실행 — 명령어 목록 등록 및 스케줄러 시작"""
    commands = [BotCommand(cmd, desc) for cmd, desc in config.BOT_COMMANDS]
    await application.bot.set_my_commands(commands)
    logger.info("봇 명령어 목록 등록 완료 (%d개)", len(commands))

    # 리마인더 스케줄러 시작
    start_scheduler(application.bot)


async def post_shutdown(application: Application) -> None:
    """봇 종료 시 실행"""
    stop_scheduler()
    logger.info("봇이 정상 종료되었습니다.")


# ─────────────────────────────────────────────
# 메인 함수
# ─────────────────────────────────────────────

def main() -> None:
    """봇 실행"""
    # 환경변수 검증
    config.validate()

    import asyncio
    asyncio.run(init_database())
    logger.info("데이터베이스 초기화 완료")

    # Application 빌드
    application = (
        Application.builder()
        .token(config.TELEGRAM_BOT_TOKEN)
        .post_init(post_init)
        .post_shutdown(post_shutdown)
        .build()
    )

    # 공통 핸들러 등록
    application.add_handler(CommandHandler("start", cmd_start))
    application.add_handler(CommandHandler("help", cmd_help))

    # 기능별 핸들러 등록
    for handler in get_schedule_handlers():
        application.add_handler(handler)

    for handler in get_reminder_handlers():
        application.add_handler(handler)

    for handler in get_memo_handlers():
        application.add_handler(handler)

    for handler in get_weather_handlers():
        application.add_handler(handler)

    for handler in get_news_handlers():
        application.add_handler(handler)

    # 채팅 핸들러는 마지막에 등록 (텍스트 메시지 폴백)
    for handler in get_chat_handlers():
        application.add_handler(handler)

    # 전역 에러 핸들러
    application.add_error_handler(error_handler)

    logger.info("봇을 시작합니다...")
    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True,
    )


if __name__ == "__main__":
    main()
