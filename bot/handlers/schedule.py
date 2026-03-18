"""
일정 관리 핸들러
명령어:
  /add_schedule <날짜시간> <제목>  - 일정 추가
  /list_schedule                  - 일정 목록 조회
  /del_schedule <id>              - 일정 삭제
  /schedule                       - 일정 관리 안내
"""
import logging

from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

from bot.database import crud
from bot.utils.helpers import format_datetime, parse_datetime_string

logger = logging.getLogger(__name__)


async def cmd_schedule_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/schedule — 일정 관리 안내 메시지"""
    if not update.message:
        return
    await update.message.reply_text(
        "📅 **일정 관리**\n\n"
        "• `/add_schedule <날짜시간> <제목>` — 일정 추가\n"
        "  형식: `YYYY-MM-DD HH:MM 제목`\n"
        "  예: `/add_schedule 2024-12-25 14:00 크리스마스 파티`\n\n"
        "• `/list_schedule` — 예정된 일정 목록\n\n"
        "• `/del_schedule <번호>` — 일정 삭제\n"
        "  예: `/del_schedule 3`",
        parse_mode="Markdown",
    )


async def cmd_add_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/add_schedule <YYYY-MM-DD HH:MM> <제목> — 일정 추가"""
    if not update.effective_user or not update.message:
        return
    if not context.args or len(context.args) < 3:
        await update.message.reply_text(
            "사용법: `/add_schedule <날짜> <시간> <제목>`\n"
            "예: `/add_schedule 2024-12-25 14:00 크리스마스 파티`",
            parse_mode="Markdown",
        )
        return

    # 첫 두 인자를 날짜시간으로, 나머지를 제목으로 처리
    datetime_str = f"{context.args[0]} {context.args[1]}"
    title = " ".join(context.args[2:])

    dt = parse_datetime_string(datetime_str)
    if dt is None:
        await update.message.reply_text(
            "날짜/시간 형식이 올바르지 않습니다.\n"
            "형식: `YYYY-MM-DD HH:MM`\n"
            "예: `2024-12-25 14:00`",
            parse_mode="Markdown",
        )
        return

    user_id = update.effective_user.id
    schedule_id = await crud.add_schedule(user_id, title, dt)

    await update.message.reply_text(
        f"✅ 일정이 추가되었습니다!\n\n"
        f"📌 **{title}**\n"
        f"🕐 {format_datetime(dt)}\n"
        f"🔢 ID: {schedule_id}",
        parse_mode="Markdown",
    )


async def cmd_list_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/list_schedule — 예정된 일정 목록"""
    if not update.effective_user or not update.message:
        return
    user_id = update.effective_user.id
    schedules = await crud.list_schedules(user_id, only_upcoming=True)

    if not schedules:
        await update.message.reply_text(
            "📅 예정된 일정이 없습니다.\n"
            "`/add_schedule`로 일정을 추가해보세요!",
            parse_mode="Markdown",
        )
        return

    lines = ["📅 **예정된 일정 목록**\n"]
    for s in schedules:
        lines.append(
            f"🔢 ID {s['id']} | 🕐 {s['scheduled_at'][:16]}\n"
            f"   📌 {s['title']}"
        )

    await update.message.reply_text(
        "\n\n".join(lines),
        parse_mode="Markdown",
    )


async def cmd_del_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/del_schedule <id> — 일정 삭제"""
    if not update.effective_user or not update.message:
        return
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text(
            "사용법: `/del_schedule <ID>`\n"
            "ID는 `/list_schedule`에서 확인할 수 있습니다.",
            parse_mode="Markdown",
        )
        return

    schedule_id = int(context.args[0])
    user_id = update.effective_user.id
    success = await crud.delete_schedule(schedule_id, user_id)

    if success:
        await update.message.reply_text(f"✅ 일정 (ID: {schedule_id}) 이 삭제되었습니다.")
    else:
        await update.message.reply_text(
            f"삭제할 일정을 찾을 수 없습니다. (ID: {schedule_id})\n"
            "`/list_schedule`로 ID를 확인해주세요.",
            parse_mode="Markdown",
        )


def get_schedule_handlers():
    """일정 관련 핸들러 목록 반환"""
    return [
        CommandHandler("schedule", cmd_schedule_help),
        CommandHandler("add_schedule", cmd_add_schedule),
        CommandHandler("list_schedule", cmd_list_schedule),
        CommandHandler("del_schedule", cmd_del_schedule),
    ]
