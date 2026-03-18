"""
데이터베이스 CRUD 함수
"""
from datetime import datetime
from typing import Any

import aiosqlite

from bot.config import config


# ─────────────────────────────────────────────
# 일정 (Schedules)
# ─────────────────────────────────────────────

async def add_schedule(user_id: int, title: str, scheduled_at: datetime) -> int:
    """일정 추가. 생성된 row id 반환"""
    async with aiosqlite.connect(config.DATABASE_PATH) as db:
        cursor = await db.execute(
            "INSERT INTO schedules (user_id, title, scheduled_at) VALUES (?, ?, ?)",
            (user_id, title, scheduled_at.strftime("%Y-%m-%d %H:%M:%S")),
        )
        await db.commit()
        return cursor.lastrowid  # type: ignore[return-value]


async def list_schedules(user_id: int, only_upcoming: bool = True) -> list[dict[str, Any]]:
    """사용자 일정 목록 반환"""
    async with aiosqlite.connect(config.DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        if only_upcoming:
            cursor = await db.execute(
                "SELECT * FROM schedules WHERE user_id=? AND is_done=0 "
                "AND scheduled_at >= datetime('now','localtime') "
                "ORDER BY scheduled_at ASC",
                (user_id,),
            )
        else:
            cursor = await db.execute(
                "SELECT * FROM schedules WHERE user_id=? ORDER BY scheduled_at DESC",
                (user_id,),
            )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


async def delete_schedule(schedule_id: int, user_id: int) -> bool:
    """일정 삭제. 성공 여부 반환"""
    async with aiosqlite.connect(config.DATABASE_PATH) as db:
        cursor = await db.execute(
            "DELETE FROM schedules WHERE id=? AND user_id=?",
            (schedule_id, user_id),
        )
        await db.commit()
        return cursor.rowcount > 0


async def mark_schedule_done(schedule_id: int) -> None:
    """일정 완료 처리"""
    async with aiosqlite.connect(config.DATABASE_PATH) as db:
        await db.execute(
            "UPDATE schedules SET is_done=1 WHERE id=?",
            (schedule_id,),
        )
        await db.commit()


# ─────────────────────────────────────────────
# 리마인더 (Reminders)
# ─────────────────────────────────────────────

async def add_reminder(user_id: int, content: str, remind_at: datetime) -> int:
    """리마인더 추가. 생성된 row id 반환"""
    async with aiosqlite.connect(config.DATABASE_PATH) as db:
        cursor = await db.execute(
            "INSERT INTO reminders (user_id, content, remind_at) VALUES (?, ?, ?)",
            (user_id, content, remind_at.strftime("%Y-%m-%d %H:%M:%S")),
        )
        await db.commit()
        return cursor.lastrowid  # type: ignore[return-value]


async def get_pending_reminders() -> list[dict[str, Any]]:
    """아직 전송되지 않은 리마인더 중 현재 시각 이후인 항목 반환"""
    async with aiosqlite.connect(config.DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM reminders WHERE is_sent=0 "
            "AND remind_at <= datetime('now','localtime') "
            "ORDER BY remind_at ASC"
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


async def mark_reminder_sent(reminder_id: int) -> None:
    """리마인더 전송 완료 처리"""
    async with aiosqlite.connect(config.DATABASE_PATH) as db:
        await db.execute(
            "UPDATE reminders SET is_sent=1 WHERE id=?",
            (reminder_id,),
        )
        await db.commit()


async def list_reminders(user_id: int) -> list[dict[str, Any]]:
    """사용자의 미전송 리마인더 목록"""
    async with aiosqlite.connect(config.DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM reminders WHERE user_id=? AND is_sent=0 "
            "ORDER BY remind_at ASC",
            (user_id,),
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


async def delete_reminder(reminder_id: int, user_id: int) -> bool:
    """리마인더 삭제"""
    async with aiosqlite.connect(config.DATABASE_PATH) as db:
        cursor = await db.execute(
            "DELETE FROM reminders WHERE id=? AND user_id=?",
            (reminder_id, user_id),
        )
        await db.commit()
        return cursor.rowcount > 0


# ─────────────────────────────────────────────
# 메모 (Memos)
# ─────────────────────────────────────────────

async def add_memo(user_id: int, content: str, tags: str = "") -> int:
    """메모 추가. 생성된 row id 반환"""
    async with aiosqlite.connect(config.DATABASE_PATH) as db:
        cursor = await db.execute(
            "INSERT INTO memos (user_id, content, tags) VALUES (?, ?, ?)",
            (user_id, content, tags),
        )
        await db.commit()
        return cursor.lastrowid  # type: ignore[return-value]


async def search_memos(user_id: int, keyword: str) -> list[dict[str, Any]]:
    """메모 키워드 검색 (내용 + 태그)"""
    async with aiosqlite.connect(config.DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM memos WHERE user_id=? "
            "AND (content LIKE ? OR tags LIKE ?) "
            "ORDER BY created_at DESC",
            (user_id, f"%{keyword}%", f"%{keyword}%"),
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


async def list_memos(user_id: int, limit: int = 10) -> list[dict[str, Any]]:
    """최근 메모 목록"""
    async with aiosqlite.connect(config.DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM memos WHERE user_id=? ORDER BY created_at DESC LIMIT ?",
            (user_id, limit),
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


async def delete_memo(memo_id: int, user_id: int) -> bool:
    """메모 삭제"""
    async with aiosqlite.connect(config.DATABASE_PATH) as db:
        cursor = await db.execute(
            "DELETE FROM memos WHERE id=? AND user_id=?",
            (memo_id, user_id),
        )
        await db.commit()
        return cursor.rowcount > 0


# ─────────────────────────────────────────────
# 대화 기록 (Chat History)
# ─────────────────────────────────────────────

async def save_chat_message(user_id: int, role: str, message: str) -> None:
    """대화 메시지 저장 (role: 'user' | 'model')"""
    async with aiosqlite.connect(config.DATABASE_PATH) as db:
        await db.execute(
            "INSERT INTO chat_history (user_id, role, message) VALUES (?, ?, ?)",
            (user_id, role, message),
        )
        await db.commit()


async def get_chat_history(user_id: int, limit: int = 10) -> list[dict[str, Any]]:
    """최근 대화 기록 반환 (오래된 순)"""
    async with aiosqlite.connect(config.DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT role, message FROM chat_history WHERE user_id=? "
            "ORDER BY created_at DESC LIMIT ?",
            (user_id, limit),
        )
        rows = await cursor.fetchall()
        # 최신 → 오래된 순으로 가져왔으므로 역순 반환
        return [dict(row) for row in reversed(rows)]


async def clear_chat_history(user_id: int) -> None:
    """대화 기록 초기화"""
    async with aiosqlite.connect(config.DATABASE_PATH) as db:
        await db.execute(
            "DELETE FROM chat_history WHERE user_id=?",
            (user_id,),
        )
        await db.commit()


# ─────────────────────────────────────────────
# 브리핑 구독자 (Briefing Subscribers)
# ─────────────────────────────────────────────

async def subscribe_briefing(user_id: int) -> None:
    """모닝 브리핑 구독 등록 또는 활성화"""
    async with aiosqlite.connect(config.DATABASE_PATH) as db:
        await db.execute(
            """
            INSERT INTO briefing_subscribers (user_id, is_active)
            VALUES (?, 1)
            ON CONFLICT(user_id) DO UPDATE SET is_active=1
            """,
            (user_id,),
        )
        await db.commit()


async def unsubscribe_briefing(user_id: int) -> None:
    """모닝 브리핑 구독 비활성화"""
    async with aiosqlite.connect(config.DATABASE_PATH) as db:
        await db.execute(
            "UPDATE briefing_subscribers SET is_active=0 WHERE user_id=?",
            (user_id,),
        )
        await db.commit()


async def get_briefing_subscribers() -> list[int]:
    """활성 구독자의 user_id 목록 반환"""
    async with aiosqlite.connect(config.DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT user_id FROM briefing_subscribers WHERE is_active=1"
        )
        rows = await cursor.fetchall()
        return [row["user_id"] for row in rows]


async def is_briefing_subscribed(user_id: int) -> bool:
    """해당 유저의 브리핑 구독 여부 확인"""
    async with aiosqlite.connect(config.DATABASE_PATH) as db:
        cursor = await db.execute(
            "SELECT is_active FROM briefing_subscribers WHERE user_id=?",
            (user_id,),
        )
        row = await cursor.fetchone()
        if row is None:
            return False
        return bool(row[0])


# ─────────────────────────────────────────────
# 지출 기록 (Expenses)
# ─────────────────────────────────────────────

async def add_expense(
    user_id: int, amount: int, description: str, category: str = "기타"
) -> int:
    """지출 추가. 생성된 row id 반환"""
    async with aiosqlite.connect(config.DATABASE_PATH) as db:
        cursor = await db.execute(
            "INSERT INTO expenses (user_id, amount, description, category) VALUES (?, ?, ?, ?)",
            (user_id, amount, description, category),
        )
        await db.commit()
        return cursor.lastrowid  # type: ignore[return-value]


async def get_expenses_today(user_id: int) -> list[dict[str, Any]]:
    """오늘 지출 목록 반환"""
    async with aiosqlite.connect(config.DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            """
            SELECT * FROM expenses
            WHERE user_id=?
              AND date(created_at) = date('now', 'localtime')
            ORDER BY created_at ASC
            """,
            (user_id,),
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


async def get_expenses_this_month(user_id: int) -> list[dict[str, Any]]:
    """이번 달 지출 목록 반환"""
    async with aiosqlite.connect(config.DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            """
            SELECT * FROM expenses
            WHERE user_id=?
              AND strftime('%Y-%m', created_at) = strftime('%Y-%m', 'now', 'localtime')
            ORDER BY created_at ASC
            """,
            (user_id,),
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


async def delete_expense(expense_id: int, user_id: int) -> bool:
    """지출 기록 삭제. 성공 여부 반환"""
    async with aiosqlite.connect(config.DATABASE_PATH) as db:
        cursor = await db.execute(
            "DELETE FROM expenses WHERE id=? AND user_id=?",
            (expense_id, user_id),
        )
        await db.commit()
        return cursor.rowcount > 0
