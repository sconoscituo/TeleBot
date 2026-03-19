"""
주식 시세 조회 핸들러
명령어:
  /stock AAPL    - 애플 주식 시세
  /stock 005930  - 삼성전자 (한국 주식, .KS 자동 추가)
"""
import logging

import yfinance as yf
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import CommandHandler, ContextTypes

logger = logging.getLogger(__name__)

# 한국 주식 코드 판별 (6자리 숫자)
def _is_korean_ticker(symbol: str) -> bool:
    return symbol.isdigit() and len(symbol) == 6


def _build_ticker(symbol: str) -> str:
    if _is_korean_ticker(symbol):
        return f"{symbol}.KS"
    return symbol.upper()


async def cmd_stock(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/stock <종목코드> — 주식 시세 조회"""
    if not update.message:
        return

    if not context.args:
        await update.message.reply_text(
            "사용법: `/stock AAPL` 또는 `/stock 005930`\n"
            "미국 주식은 티커 심볼, 한국 주식은 6자리 종목 코드를 입력하세요.",
            parse_mode="Markdown",
        )
        return

    raw_symbol = context.args[0]
    ticker_str = _build_ticker(raw_symbol)

    await update.effective_chat.send_action(ChatAction.TYPING)

    try:
        ticker = yf.Ticker(ticker_str)
        info = ticker.info

        name = info.get("longName") or info.get("shortName") or ticker_str
        currency = info.get("currency", "")
        current_price = info.get("currentPrice") or info.get("regularMarketPrice")
        prev_close = info.get("previousClose") or info.get("regularMarketPreviousClose")
        week_high = info.get("fiftyTwoWeekHigh")
        week_low = info.get("fiftyTwoWeekLow")

        if current_price is None:
            await update.message.reply_text(
                f"종목 `{ticker_str}` 정보를 가져올 수 없습니다. 종목 코드를 확인해주세요.",
                parse_mode="Markdown",
            )
            return

        # 등락률 계산
        change_pct = ""
        change_str = ""
        if prev_close and prev_close != 0:
            diff = current_price - prev_close
            pct = (diff / prev_close) * 100
            sign = "▲" if diff >= 0 else "▼"
            change_str = f"{sign} {abs(diff):,.2f}"
            change_pct = f"({pct:+.2f}%)"

        lines = [
            f"📈 *{name}* (`{ticker_str}`)",
            f"",
            f"현재가: *{current_price:,.2f} {currency}*",
        ]
        if change_str:
            lines.append(f"등락: {change_str} {change_pct}")
        if week_high:
            lines.append(f"52주 고가: {week_high:,.2f} {currency}")
        if week_low:
            lines.append(f"52주 저가: {week_low:,.2f} {currency}")

        await update.message.reply_text("\n".join(lines), parse_mode="Markdown")

    except Exception as e:
        logger.error("주식 시세 조회 실패 [%s]: %s", ticker_str, e)
        await update.message.reply_text(
            f"시세 조회 중 오류가 발생했습니다. 종목 코드를 확인해주세요.\n`{ticker_str}`",
            parse_mode="Markdown",
        )


def get_stock_handlers():
    """주식 관련 핸들러 목록 반환"""
    return [
        CommandHandler("stock", cmd_stock),
    ]
