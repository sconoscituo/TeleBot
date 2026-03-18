"""
지출 기록 핸들러
명령어:
  /expense <금액> <설명>        - 지출 기록 (예: /expense 5000 스타벅스)
  /expense <설명> <금액>        - 지출 기록 (예: /expense 스타벅스 5000)
  /expense_today               - 오늘 지출 합계 조회
  /expense_month               - 이번 달 지출 요약
  /del_expense <id>            - 지출 기록 삭제
"""
import logging
import re

from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

from bot.database import crud

logger = logging.getLogger(__name__)


def _parse_expense_args(args: list[str]) -> tuple[int, str] | None:
    """
    인자에서 금액과 설명을 파싱합니다.
    지원 형식:
      /expense 5000 스타벅스
      /expense 스타벅스 5000
      /expense 스타벅스 5,000
    반환값: (금액, 설명) 또는 파싱 실패 시 None
    """
    if not args:
        return None

    text = " ".join(args)
    # 쉼표 제거 후 숫자 추출
    cleaned = text.replace(",", "")
    numbers = re.findall(r"\d+", cleaned)
    if not numbers:
        return None

    amount = int(numbers[0])
    # 설명: 숫자(와 쉼표) 부분을 제거한 나머지
    description = re.sub(r"[\d,]+", "", text).strip()
    if not description:
        description = "내역 없음"

    return amount, description


async def cmd_expense(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/expense <금액> <설명> 또는 /expense <설명> <금액> — 지출 기록"""
    if not update.effective_user or not update.message:
        return

    if not context.args:
        await update.message.reply_text(
            "💸 **지출 기록 사용법**\n\n"
            "`/expense <금액> <설명>` — 지출 추가\n"
            "예: `/expense 5000 스타벅스`\n"
            "예: `/expense 12500 점심`\n\n"
            "`/expense_today` — 오늘 지출 합계\n"
            "`/expense_month` — 이번 달 지출 요약",
            parse_mode="Markdown",
        )
        return

    parsed = _parse_expense_args(list(context.args))
    if parsed is None:
        await update.message.reply_text(
            "금액을 인식할 수 없습니다.\n"
            "예: `/expense 5000 스타벅스` 또는 `/expense 스타벅스 5000`",
            parse_mode="Markdown",
        )
        return

    amount, description = parsed
    user_id = update.effective_user.id
    expense_id = await crud.add_expense(user_id, amount, description)

    await update.message.reply_text(
        f"✅ 지출이 기록되었습니다!\n\n"
        f"📝 내역: {description}\n"
        f"💰 금액: {amount:,}원\n"
        f"🔢 ID: {expense_id}",
        parse_mode="Markdown",
    )
    logger.info("지출 기록: user_id=%d, amount=%d, desc=%s", user_id, amount, description)


async def cmd_expense_today(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/expense_today — 오늘 지출 합계 조회"""
    if not update.effective_user or not update.message:
        return

    user_id = update.effective_user.id
    expenses = await crud.get_expenses_today(user_id)

    if not expenses:
        await update.message.reply_text(
            "📊 오늘 기록된 지출이 없습니다.\n"
            "`/expense <금액> <설명>`으로 지출을 기록해보세요!",
            parse_mode="Markdown",
        )
        return

    total = sum(e["amount"] for e in expenses)
    lines = ["📊 **오늘의 지출 내역**\n"]
    for e in expenses:
        lines.append(
            f"🔢 ID {e['id']} | {e['created_at'][11:16]}\n"
            f"   {e['description']} — {e['amount']:,}원"
        )
    lines.append(f"\n💰 **오늘 총 지출: {total:,}원**")

    await update.message.reply_text(
        "\n".join(lines),
        parse_mode="Markdown",
    )


async def cmd_expense_month(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/expense_month — 이번 달 지출 요약"""
    if not update.effective_user or not update.message:
        return

    user_id = update.effective_user.id
    expenses = await crud.get_expenses_this_month(user_id)

    if not expenses:
        await update.message.reply_text(
            "📊 이번 달 기록된 지출이 없습니다.\n"
            "`/expense <금액> <설명>`으로 지출을 기록해보세요!",
            parse_mode="Markdown",
        )
        return

    total = sum(e["amount"] for e in expenses)

    # 카테고리별 합계
    category_totals: dict[str, int] = {}
    for e in expenses:
        cat = e["category"]
        category_totals[cat] = category_totals.get(cat, 0) + e["amount"]

    lines = ["📊 **이번 달 지출 요약**\n"]

    # 카테고리별 내역
    for cat, amt in sorted(category_totals.items(), key=lambda x: -x[1]):
        lines.append(f"  • {cat}: {amt:,}원")

    lines.append(f"\n📋 총 거래 건수: {len(expenses)}건")
    lines.append(f"💰 **이번 달 총 지출: {total:,}원**")

    await update.message.reply_text(
        "\n".join(lines),
        parse_mode="Markdown",
    )


async def cmd_del_expense(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/del_expense <id> — 지출 기록 삭제"""
    if not update.effective_user or not update.message:
        return

    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text(
            "사용법: `/del_expense <ID>`\n"
            "ID는 `/expense_today` 또는 `/expense_month`에서 확인할 수 있습니다.",
            parse_mode="Markdown",
        )
        return

    expense_id = int(context.args[0])
    user_id = update.effective_user.id
    success = await crud.delete_expense(expense_id, user_id)

    if success:
        await update.message.reply_text(f"✅ 지출 기록 (ID: {expense_id}) 이 삭제되었습니다.")
    else:
        await update.message.reply_text(
            f"삭제할 지출 기록을 찾을 수 없습니다. (ID: {expense_id})\n"
            "`/expense_today`로 ID를 확인해주세요.",
            parse_mode="Markdown",
        )


def get_expense_handlers():
    """지출 관련 핸들러 목록 반환"""
    return [
        CommandHandler("expense", cmd_expense),
        CommandHandler("expense_today", cmd_expense_today),
        CommandHandler("expense_month", cmd_expense_month),
        CommandHandler("del_expense", cmd_del_expense),
    ]
