"""
Работа с базой данных SQLite.
Хранит пользователей, их ответы и прогресс по воронке.
"""

import aiosqlite
from datetime import datetime
import os

DB_DIR = os.getenv("DB_DIR", ".")
DB_PATH = os.path.join(DB_DIR, "bot_data.db")


async def init_db():
    """Создаёт таблицы при первом запуске."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id     INTEGER PRIMARY KEY,
                username    TEXT,
                full_name   TEXT,
                started_at  TEXT,
                step        INTEGER DEFAULT 0,
                q1 TEXT, q2 TEXT, q3 TEXT, q4 TEXT, q5 TEXT,
                finished    INTEGER DEFAULT 0,
                branch      TEXT,
                updated_at  TEXT
            )
            """
        )
        await db.commit()


async def register_user(user_id: int, username: str, full_name: str):
    """Регистрирует нового пользователя или ничего не делает, если уже есть."""
    now = datetime.now().isoformat(timespec="seconds")
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO users (user_id, username, full_name, started_at, step, updated_at)
            VALUES (?, ?, ?, ?, 0, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                username=excluded.username,
                full_name=excluded.full_name,
                updated_at=excluded.updated_at
            """,
            (user_id, username, full_name, now, now),
        )
        await db.commit()


async def save_answer(user_id: int, step: int, answer: str):
    """Сохраняет ответ на конкретный вопрос и обновляет прогресс."""
    col = f"q{step}"
    now = datetime.now().isoformat(timespec="seconds")
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            f"UPDATE users SET {col}=?, step=?, updated_at=? WHERE user_id=?",
            (answer, step, now, user_id),
        )
        await db.commit()


async def mark_finished(user_id: int, branch: str):
    """Отмечает, что человек дошёл до финала, и какую ветку выбрал."""
    now = datetime.now().isoformat(timespec="seconds")
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET finished=1, branch=?, step=5, updated_at=? WHERE user_id=?",
            (branch, now, user_id),
        )
        await db.commit()


async def get_stats() -> dict:
    """Собирает статистику для админки."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        total = (await (await db.execute("SELECT COUNT(*) c FROM users")).fetchone())["c"]

        steps = {}
        for s in range(1, 6):
            row = await (
                await db.execute("SELECT COUNT(*) c FROM users WHERE step >= ?", (s,))
            ).fetchone()
            steps[s] = row["c"]

        finished = (
            await (await db.execute("SELECT COUNT(*) c FROM users WHERE finished=1")).fetchone())
        )["c"]

        branches = {}
        for b in ("yes", "depends", "no"):
            row = await (
                await db.execute("SELECT COUNT(*) c FROM users WHERE branch=?", (b,))
            ).fetchone()
            branches[b] = row["c"]

        return {
            "total": total,
            "steps": steps,
            "finished": finished,
            "branches": branches,
        }


async def get_all_user_ids() -> list[int]:
    """Все ID для рассылки."""
    async with aiosqlite.connect(DB_PATH) as db:
        rows = await (await db.execute("SELECT user_id FROM users")).fetchall()
        return [r[0] for r in rows]


async def get_recent_users(limit: int = 20) -> list[dict]:
    """Последние пользователи для просмотра."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        rows = await (
            await db.execute(
                "SELECT user_id, username, full_name, step, finished, branch, started_at "
                "FROM users ORDER BY updated_at DESC LIMIT ?",
                (limit,),
            )
        ).fetchall()
        return [dict(r) for r in rows]


async def search_user(query: str) -> dict:
    """Поиск пользователя по username или ID."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        
        if query.isdigit():
            row = await (
                await db.execute("SELECT * FROM users WHERE user_id=?", (int(query),))
            ).fetchone()
        else:
            query = query.lstrip("@")
            row = await (
                await db.execute("SELECT * FROM users WHERE username=?", (query,))
            ).fetchone()
        
        return dict(row) if row else None


async def export_csv() -> str:
    """Экспортирует всех пользователей в CSV-строку."""
    import csv
    import io

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        rows = await (await db.execute("SELECT * FROM users ORDER BY started_at")).fetchall()

    buf = io.StringIO()
    if rows:
        writer = csv.DictWriter(buf, fieldnames=rows[0].keys())
        writer.writeheader()
        for r in rows:
            writer.writerow(dict(r))
    return buf.getvalue()
