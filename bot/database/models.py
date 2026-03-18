"""
SQLite 데이터베이스 스키마 정의 및 초기화
"""
import aiosqlite

from bot.config import config

# DDL 쿼리 모음
CREATE_SCHEDULES_TABLE = """
CREATE TABLE IF NOT EXISTS schedules (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL,
    title       TEXT    NOT NULL,
    scheduled_at DATETIME NOT NULL,
    created_at  DATETIME DEFAULT (datetime('now', 'localtime')),
    is_done     INTEGER DEFAULT 0
);
"""

CREATE_REMINDERS_TABLE = """
CREATE TABLE IF NOT EXISTS reminders (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL,
    content     TEXT    NOT NULL,
    remind_at   DATETIME NOT NULL,
    created_at  DATETIME DEFAULT (datetime('now', 'localtime')),
    is_sent     INTEGER DEFAULT 0
);
"""

CREATE_MEMOS_TABLE = """
CREATE TABLE IF NOT EXISTS memos (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL,
    content     TEXT    NOT NULL,
    tags        TEXT    DEFAULT '',
    created_at  DATETIME DEFAULT (datetime('now', 'localtime'))
);
"""

CREATE_CHAT_HISTORY_TABLE = """
CREATE TABLE IF NOT EXISTS chat_history (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL,
    role        TEXT    NOT NULL,
    message     TEXT    NOT NULL,
    created_at  DATETIME DEFAULT (datetime('now', 'localtime'))
);
"""

# 인덱스
CREATE_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_schedules_user ON schedules(user_id);",
    "CREATE INDEX IF NOT EXISTS idx_reminders_user ON reminders(user_id);",
    "CREATE INDEX IF NOT EXISTS idx_reminders_sent ON reminders(is_sent, remind_at);",
    "CREATE INDEX IF NOT EXISTS idx_memos_user ON memos(user_id);",
    "CREATE INDEX IF NOT EXISTS idx_chat_user ON chat_history(user_id);",
]


async def init_database() -> None:
    """데이터베이스 및 테이블 초기화"""
    import os

    # 데이터 디렉토리 생성
    db_dir = os.path.dirname(config.DATABASE_PATH)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

    async with aiosqlite.connect(config.DATABASE_PATH) as db:
        await db.execute(CREATE_SCHEDULES_TABLE)
        await db.execute(CREATE_REMINDERS_TABLE)
        await db.execute(CREATE_MEMOS_TABLE)
        await db.execute(CREATE_CHAT_HISTORY_TABLE)
        for idx_sql in CREATE_INDEXES:
            await db.execute(idx_sql)
        await db.commit()
