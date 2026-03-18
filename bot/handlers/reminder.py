"""
리마인더 핸들러
명령어:
  /reminder <날짜시간> <내용>  - 리마인더 설정
  /list_reminder               - 리마인더 목록
  /del_reminder <id>           - 리마인더 삭제
"""
import logging

from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

from bot.database import crud
from bot.utils.helpers import format_datetime, get_seoul_time, parse_datetime_string

logger = logging.getLogger(__name__)


async def cmd_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/reminder <YYYY-MM-DD HH:MM> <내용> — 리마인더 설정"""
    if not update.effective_user or not update.message:
        return
    if not context.args or len(context.args) < 3:
        await update.message.reply_text(
            "⏰ **리마인더 설정**\n\n"
            "사용법: `/reminder <날짜> <시간> <내용>`\n"
            "예: `/reminder 2024-12-25 09:00 선물 포장하기`\n\n"
            "다른 명령어:\n"
            "• `/list_reminder` — 리마인더 목록\n"
            "• `/del_reminder <ID>` — 리마인더 삭제",
            parse_mode="Markdown",
        )
        return

    datetime_str = f"{context.args[0]} {context.args[1]}"
    content = " ".join(context.args[2:])

    dt = parse_datetime_string(datetime_str)
    if dt is None:
        await update.message.reply_text(
            "날짜/시간 형식이 올바르지 않습니다.\n"
            "형식: `YYYY-MM-DD HH:MM`",
            parse_mode="Markdown",
        )
        return

    now = get_seoul_time()
    if dt <= now:
        await update.message.reply_text(
            "리마인더 시간은 현재 시각보다 미래여야 합니다.\n"
            f"현재 시각: {format_datetime(now)}",
        )
        return

    user_id = update.effective_user.id
    reminder_id = await crud.add_reminder(user_id, content, dt)

    await update.message.reply_text(
        f"✅ 리마인더가 설정되었습니다!\n\n"
        f"📌 **{content}**\n"
        f"⏰ {format_datetime(dt)}\n"
        f"🔢 ID: {reminder_id}",
        parse_mode="Markdown",
    )


async def cmd_list_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/list_reminder — 설정된 리마인더 목록"""
    if not update.effective_user or not update.message:
        return
    user_id = update.effective_user.id
    reminders = await crud.list_reminders(user_id)

    if not reminders:
        await update.message.reply_text(
            "⏰ 설정된 리마인더가 없습니다.\n"
            "`/reminder`로 리마인더를 추가해보세요!",
            parse_mode="Markdown",
        )
        return

    lines = ["⏰ **리마인더 목록**\n"]
    for r in reminders:
        lines.append(
            f"🔢 ID {r['id']} | 🕐 {r['remind_at'][:16]}\n"
            f"   📌 {r['content']}"
        )

    await update.message.reply_text(
        "\n\n".join(lines),
        parse_mode="Markdown",
    )


async def cmd_del_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/del_reminder <id> — 리마인더 삭제"""
    if not update.effective_user or not update.message:
        return
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text(
            "사용법: `/del_reminder <ID>`\n"
            "ID는 `/list_reminder`에서 확인할 수 있습니다.",
            parse_mode="Markdown",
        )
        return

    reminder_id = int(context.args[0])
    user_id = update.effective_user.id
    success = await crud.delete_reminder(reminder_id, user_id)

    if success:
        await update.message.reply_text(f"✅ 리마인더 (ID: {reminder_id}) 가 삭제되었습니다.")
    else:
        await update.message.reply_text(
            f"삭제할 리마인더를 찾을 수 없습니다. (ID: {reminder_id})\n"
            "`/list_reminder`로 ID를 확인해주세요.",
            parse_mode="Markdown",
        )


def get_reminder_handlers():
    """리마인더 관련 핸들러 목록 반환"""
    return [
        CommandHandler("reminder", cmd_reminder),
        CommandHandler("list_reminder", cmd_list_reminder),
        CommandHandler("del_reminder", cmd_del_reminder),
    ]
