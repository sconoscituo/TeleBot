"""
암호화폐 시세 조회 핸들러
명령어:
  /crypto BTC — 비트코인 현재가
  /crypto ETH — 이더리움
CoinGecko 무료 API 사용 (인증 불필요)
"""
import logging

import httpx
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import CommandHandler, ContextTypes

logger = logging.getLogger(__name__)

COINGECKO_API_URL = "https://api.coingecko.com/api/v3"

# 심볼 → CoinGecko ID 매핑 (주요 코인)
SYMBOL_TO_ID: dict[str, str] = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "BNB": "binancecoin",
    "XRP": "ripple",
    "SOL": "solana",
    "ADA": "cardano",
    "DOGE": "dogecoin",
    "AVAX": "avalanche-2",
    "DOT": "polkadot",
    "MATIC": "matic-network",
    "LINK": "chainlink",
    "UNI": "uniswap",
    "LTC": "litecoin",
    "BCH": "bitcoin-cash",
    "ATOM": "cosmos",
    "NEAR": "near",
    "APT": "aptos",
    "ARB": "arbitrum",
    "OP": "optimism",
    "SUI": "sui",
}


def _resolve_coin_id(symbol: str) -> str:
    """심볼 또는 CoinGecko ID를 CoinGecko ID로 변환"""
    upper = symbol.upper()
    return SYMBOL_TO_ID.get(upper, symbol.lower())


async def cmd_crypto(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/crypto <심볼> — 암호화폐 시세 조회"""
    if not update.message:
        return

    if not context.args:
        await update.message.reply_text(
            "사용법: `/crypto BTC` 또는 `/crypto ETH`\n"
            "지원 심볼: BTC, ETH, BNB, XRP, SOL, ADA, DOGE 등",
            parse_mode="Markdown",
        )
        return

    raw = context.args[0]
    coin_id = _resolve_coin_id(raw)

    await update.effective_chat.send_action(ChatAction.TYPING)

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(
                f"{COINGECKO_API_URL}/coins/{coin_id}",
                params={
                    "localization": "false",
                    "tickers": "false",
                    "community_data": "false",
                    "developer_data": "false",
                },
            )
            if response.status_code == 404:
                await update.message.reply_text(
                    f"코인 `{raw.upper()}` 을(를) 찾을 수 없습니다.\n"
                    "심볼(BTC, ETH 등) 또는 CoinGecko ID를 확인해주세요.",
                    parse_mode="Markdown",
                )
                return
            response.raise_for_status()
            data = response.json()

        name = data.get("name", raw.upper())
        symbol = data.get("symbol", "").upper()
        market_data = data.get("market_data", {})

        current_price = market_data.get("current_price", {}).get("usd")
        price_change_24h = market_data.get("price_change_percentage_24h")
        price_change_7d = market_data.get("price_change_percentage_7d")
        market_cap = market_data.get("market_cap", {}).get("usd")
        high_24h = market_data.get("high_24h", {}).get("usd")
        low_24h = market_data.get("low_24h", {}).get("usd")

        if current_price is None:
            await update.message.reply_text("시세 데이터를 가져올 수 없습니다.")
            return

        # 24시간 등락 표시
        change_24h_str = ""
        if price_change_24h is not None:
            sign = "▲" if price_change_24h >= 0 else "▼"
            change_24h_str = f"{sign} {abs(price_change_24h):.2f}%"

        change_7d_str = ""
        if price_change_7d is not None:
            sign = "▲" if price_change_7d >= 0 else "▼"
            change_7d_str = f"{sign} {abs(price_change_7d):.2f}%"

        lines = [
            f"🪙 *{name}* (`{symbol}`)",
            f"",
            f"현재가: *${current_price:,.4f}*",
        ]
        if change_24h_str:
            lines.append(f"24h 등락: {change_24h_str}")
        if change_7d_str:
            lines.append(f"7일 등락: {change_7d_str}")
        if high_24h:
            lines.append(f"24h 고가: ${high_24h:,.4f}")
        if low_24h:
            lines.append(f"24h 저가: ${low_24h:,.4f}")
        if market_cap:
            lines.append(f"시가총액: ${market_cap:,.0f}")

        await update.message.reply_text("\n".join(lines), parse_mode="Markdown")

    except httpx.HTTPStatusError as e:
        logger.error("CoinGecko API 오류 [%s]: %s", coin_id, e)
        await update.message.reply_text("시세 조회 중 API 오류가 발생했습니다. 잠시 후 다시 시도해주세요.")
    except Exception as e:
        logger.error("암호화폐 시세 조회 실패 [%s]: %s", coin_id, e)
        await update.message.reply_text("시세 조회 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.")


def get_crypto_handlers():
    """암호화폐 관련 핸들러 목록 반환"""
    return [
        CommandHandler("crypto", cmd_crypto),
    ]
