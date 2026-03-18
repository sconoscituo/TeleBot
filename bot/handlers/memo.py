"""
메모 핸들러
명령어:
  /add_memo <내용>         - 메모 저장
  /search_memo <키워드>    - 메모 검색
  /list_memo               - 최근 메모 목록
  /del_memo <id>           - 메모 삭제
  /memo                    - 메모 관리 안내
"""
import logging

from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

from bot.database import crud

logger = logging.getLogger(__name__)


async def cmd_memo_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/memo — 메모 관리 안내"""
    if not update.message:
        return
    await update.message.reply_text(
        "📝 **메모 관리**\n\n"
        "• `/add_memo <내용>` — 메모 저장\n"
        "  예: `/add_memo 파이썬 공부 - 비동기 프로그래밍 정리`\n\n"
        "• `/list_memo` — 최근 메모 10개 조회\n\n"
        "• `/search_memo <키워드>` — 메모 검색\n"
        "  예: `/search_memo 파이썬`\n\n"
        "• `/del_memo <ID>` — 메모 삭제\n"
        "  예: `/del_memo 5`",
        parse_mode="Markdown",
    )


async def cmd_add_memo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/add_memo <내용> — 메모 저장"""
    if not update.effective_user or not update.message:
        return
    if not context.args:
        await update.message.reply_text(
            "사용법: `/add_memo <내용>`\n"
            "예: `/add_memo 회의 아이디어 - 신규 기능 A, B, C`",
            parse_mode="Markdown",
        )
        return

    content = " ".join(context.args)
    user_id = update.effective_user.id
    memo_id = await crud.add_memo(user_id, content)

    await update.message.reply_text(
        f"✅ 메모가 저장되었습니다!\n\n"
        f"📝 {content}\n"
        f"🔢 ID: {memo_id}",
        parse_mode="Markdown",
    )


async def cmd_list_memo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/list_memo — 최근 메모 목록"""
    if not update.effective_user or not update.message:
        return
    user_id = update.effective_user.id
    memos = await crud.list_memos(user_id, limit=10)

    if not memos:
        await update.message.reply_text(
            "📝 저장된 메모가 없습니다.\n"
            "`/add_memo`로 메모를 추가해보세요!",
            parse_mode="Markdown",
        )
        return

    lines = ["📝 **최근 메모 목록**\n"]
    for m in memos:
        created = m["created_at"][:16] if m.get("created_at") else ""
        lines.append(
            f"🔢 ID {m['id']} | 🕐 {created}\n"
            f"   {m['content']}"
        )

    await update.message.reply_text(
        "\n\n".join(lines),
        parse_mode="Markdown",
    )


async def cmd_search_memo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/search_memo <키워드> — 메모 검색"""
    if not update.effective_user or not update.message:
        return
    if not context.args:
        await update.message.reply_text(
            "사용법: `/search_memo <키워드>`\n"
            "예: `/search_memo 파이썬`",
            parse_mode="Markdown",
        )
        return

    keyword = " ".join(context.args)
    user_id = update.effective_user.id
    memos = await crud.search_memos(user_id, keyword)

    if not memos:
        await update.message.reply_text(
            f"🔍 '{keyword}'에 대한 검색 결과가 없습니다.",
        )
        return

    lines = [f"🔍 **'{keyword}' 검색 결과** ({len(memos)}건)\n"]
    for m in memos:
        created = m["created_at"][:16] if m.get("created_at") else ""
        lines.append(
            f"🔢 ID {m['id']} | 🕐 {created}\n"
            f"   {m['content']}"
        )

    await update.message.reply_text(
        "\n\n".join(lines),
        parse_mode="Markdown",
    )


async def cmd_del_memo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/del_memo <id> — 메모 삭제"""
    if not update.effective_user or not update.message:
        return
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text(
            "사용법: `/del_memo <ID>`\n"
            "ID는 `/list_memo`에서 확인할 수 있습니다.",
            parse_mode="Markdown",
        )
        return

    memo_id = int(context.args[0])
    user_id = update.effective_user.id
    success = await crud.delete_memo(memo_id, user_id)

    if success:
        await update.message.reply_text(f"✅ 메모 (ID: {memo_id}) 가 삭제되었습니다.")
    else:
        await update.message.reply_text(
            f"삭제할 메모를 찾을 수 없습니다. (ID: {memo_id})\n"
            "`/list_memo`로 ID를 확인해주세요.",
            parse_mode="Markdown",
        )


def get_memo_handlers():
    """메모 관련 핸들러 목록 반환"""
    return [
        CommandHandler("memo", cmd_memo_help),
        CommandHandler("add_memo", cmd_add_memo),
        CommandHandler("list_memo", cmd_list_memo),
        CommandHandler("search_memo", cmd_search_memo),
        CommandHandler("del_memo", cmd_del_memo),
    ]
