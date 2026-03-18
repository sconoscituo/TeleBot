"""
RSS 뉴스 수집 및 Gemini 요약 서비스
"""
import asyncio
import logging
import re
from dataclasses import dataclass

import feedparser

from bot.config import config
from bot.services.gemini import gemini_service

logger = logging.getLogger(__name__)


@dataclass
class NewsItem:
    title: str
    link: str
    summary: str
    source: str


async def fetch_rss_news(max_per_feed: int = 5) -> list[NewsItem]:
    """
    설정된 RSS 피드에서 최신 뉴스 항목을 수집합니다.
    feedparser는 동기 라이브러리이므로 asyncio executor를 통해 실행합니다.
    """
    loop = asyncio.get_running_loop()
    items: list[NewsItem] = []

    for feed_url in config.NEWS_RSS_FEEDS:
        try:
            # feedparser의 동기 호출을 executor에서 실행
            feed = await loop.run_in_executor(None, feedparser.parse, feed_url)
            source = feed.feed.get("title", feed_url)
            for entry in feed.entries[:max_per_feed]:
                title = entry.get("title", "제목 없음")
                link = entry.get("link", "")
                raw_summary = entry.get("summary", entry.get("description", ""))
                clean_summary = re.sub(r"<[^>]+>", "", raw_summary).strip()
                items.append(NewsItem(
                    title=title,
                    link=link,
                    summary=clean_summary[:300],
                    source=source,
                ))
        except Exception as e:
            logger.warning("RSS 피드 파싱 실패 (%s): %s", feed_url, e)

    return items


async def get_news_summary(max_articles: int = 10) -> str:
    """
    최신 뉴스를 수집하고 Gemini로 요약하여 반환합니다.
    """
    items = await fetch_rss_news()
    if not items:
        return "현재 뉴스를 가져올 수 없습니다. RSS 피드를 확인해주세요."

    # 최대 기사 수 제한
    items = items[:max_articles]

    # Gemini에 전달할 텍스트 구성
    articles_text = "\n\n".join(
        f"[{i + 1}] {item.title}\n출처: {item.source}\n{item.summary}"
        for i, item in enumerate(items)
    )

    prompt_prefix = (
        "다음은 최신 뉴스 기사 목록입니다. "
        "각 기사의 핵심 내용을 한 줄씩 요약하고, "
        "전체적인 오늘의 주요 트렌드를 2-3문장으로 정리해주세요.\n"
        "형식: \n"
        "📰 **주요 뉴스 요약**\n"
        "1. [제목] - [한 줄 요약]\n"
        "...\n"
        "🔍 **오늘의 트렌드**: ..."
    )

    summary = await gemini_service.summarize(articles_text, prompt_prefix)
    return summary
