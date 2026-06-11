import sqlite3
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional


def _app_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).parent


DB_PATH = _app_dir() / "schedules.db"

NOTIFICATION_TIMES = {
    "3 hours ago": 180,
    "1 hour ago": 60,
    "30 minutes ago": 30,
    "10 minutes ago": 10,
}

REPEAT_TIMES = {
    "10 minutes": 10,
    "5 minutes": 5,
    "3 minutes": 3,
    "1 minute": 1,
}

STATUS_NOT_DONE = "not_done"
STATUS_DONE = "done"
STATUS_INCOMPLETE = "incomplete"

COMPLETION_STATUSES = (STATUS_NOT_DONE, STATUS_DONE, STATUS_INCOMPLETE)

STATUS_LABELS = {
    STATUS_NOT_DONE: "Not Done",
    STATUS_DONE: "Done",
    STATUS_INCOMPLETE: "Incomplete",
}

STATUS_CALENDAR_COLORS = {
    STATUS_DONE: ("#2f6b3f", "#c8f0d4"),
    STATUS_NOT_DONE: ("#7a2d35", "#f5c6cb"),
    STATUS_INCOMPLETE: ("#7a5a28", "#f5deb8"),
}


@dataclass
class Schedule:
    id: Optional[int]
    title: str
    start_time: datetime
    end_time: datetime
    content: str
    url: str
    notification_enabled: bool
    notification_time: str
    repeat_time: str
    completion_status: str = STATUS_NOT_DONE

    @property
    def notification_status(self) -> str:
        return "On" if self.notification_enabled else "Off"

    @property
    def completion_label(self) -> str:
        return STATUS_LABELS.get(self.completion_status, "Not Done")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _migrate(conn: sqlite3.Connection) -> None:
    columns = {
        row[1] for row in conn.execute("PRAGMA table_info(schedules)").fetchall()
    }
    if "completion_status" not in columns:
        conn.execute(
            """
            ALTER TABLE schedules
            ADD COLUMN completion_status TEXT DEFAULT 'not_done'
            """
        )


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS schedules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                content TEXT DEFAULT '',
                url TEXT DEFAULT '',
                notification_enabled INTEGER DEFAULT 1,
                notification_time TEXT DEFAULT '30 minutes ago',
                repeat_time TEXT DEFAULT '5 minutes',
                completion_status TEXT DEFAULT 'not_done'
            )
            """
        )
        _migrate(conn)


def _row_to_schedule(row: sqlite3.Row) -> Schedule:
    status = row["completion_status"] if "completion_status" in row.keys() else STATUS_NOT_DONE
    if status not in COMPLETION_STATUSES:
        status = STATUS_NOT_DONE
    return Schedule(
        id=row["id"],
        title=row["title"],
        start_time=datetime.fromisoformat(row["start_time"]),
        end_time=datetime.fromisoformat(row["end_time"]),
        content=row["content"] or "",
        url=row["url"] or "",
        notification_enabled=int(row["notification_enabled"]) == 1,
        notification_time=row["notification_time"],
        repeat_time=row["repeat_time"],
        completion_status=status,
    )


def sync_completion_statuses(now: datetime | None = None) -> int:
    now = now or datetime.now()
    now_iso = now.isoformat()
    with get_connection() as conn:
        reverted = conn.execute(
            """
            UPDATE schedules
            SET completion_status = ?
            WHERE completion_status = ? AND end_time >= ?
            """,
            (STATUS_NOT_DONE, STATUS_INCOMPLETE, now_iso),
        )
        marked = conn.execute(
            """
            UPDATE schedules
            SET completion_status = ?
            WHERE completion_status = ? AND end_time < ?
            """,
            (STATUS_INCOMPLETE, STATUS_NOT_DONE, now_iso),
        )
        conn.commit()
        return reverted.rowcount + marked.rowcount


def auto_mark_incomplete(now: datetime | None = None) -> int:
    return sync_completion_statuses(now)


def _sanitize_completion_status(
    status: str, end_time: datetime, now: datetime | None = None
) -> str:
    now = now or datetime.now()
    if status not in COMPLETION_STATUSES:
        status = STATUS_NOT_DONE
    if status == STATUS_INCOMPLETE and now < end_time:
        return STATUS_NOT_DONE
    if status == STATUS_NOT_DONE and now >= end_time:
        return STATUS_INCOMPLETE
    return status


def get_all_schedules() -> list[Schedule]:
    sync_completion_statuses()
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM schedules ORDER BY start_time ASC"
        ).fetchall()
    return [_row_to_schedule(row) for row in rows]


def get_schedule(schedule_id: int) -> Optional[Schedule]:
    sync_completion_statuses()
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM schedules WHERE id = ?", (schedule_id,)
        ).fetchone()
    return _row_to_schedule(row) if row else None


def save_schedule(schedule: Schedule) -> int:
    start_iso = schedule.start_time.isoformat()
    end_iso = schedule.end_time.isoformat()
    status = _sanitize_completion_status(
        schedule.completion_status, schedule.end_time
    )
    with get_connection() as conn:
        if schedule.id is None:
            cursor = conn.execute(
                """
                INSERT INTO schedules
                    (title, start_time, end_time, content, url,
                     notification_enabled, notification_time, repeat_time,
                     completion_status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    schedule.title,
                    start_iso,
                    end_iso,
                    schedule.content,
                    schedule.url,
                    int(schedule.notification_enabled),
                    schedule.notification_time,
                    schedule.repeat_time,
                    status,
                ),
            )
            conn.commit()
            return cursor.lastrowid
        conn.execute(
            """
            UPDATE schedules SET
                title = ?, start_time = ?, end_time = ?, content = ?, url = ?,
                notification_enabled = ?, notification_time = ?, repeat_time = ?,
                completion_status = ?
            WHERE id = ?
            """,
            (
                schedule.title,
                start_iso,
                end_iso,
                schedule.content,
                schedule.url,
                int(schedule.notification_enabled),
                schedule.notification_time,
                schedule.repeat_time,
                status,
                schedule.id,
            ),
        )
        conn.commit()
        return schedule.id


def set_completion_status(schedule_id: int, status: str) -> bool:
    if status not in COMPLETION_STATUSES:
        return False
    with get_connection() as conn:
        row = conn.execute(
            "SELECT end_time FROM schedules WHERE id = ?", (schedule_id,)
        ).fetchone()
        if not row:
            return False
        end_time = datetime.fromisoformat(row["end_time"])
        status = _sanitize_completion_status(status, end_time)
        if status == STATUS_INCOMPLETE and datetime.now() < end_time:
            return False
        conn.execute(
            "UPDATE schedules SET completion_status = ? WHERE id = ?",
            (status, schedule_id),
        )
        conn.commit()
    return True


def toggle_notification(schedule_id: int) -> bool | None:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT notification_enabled FROM schedules WHERE id = ?", (schedule_id,)
        ).fetchone()
        if not row:
            return None
        enabled = not bool(row["notification_enabled"])
        conn.execute(
            "UPDATE schedules SET notification_enabled = ? WHERE id = ?",
            (int(enabled), schedule_id),
        )
        conn.commit()
        return enabled


def delete_schedule(schedule_id: int) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM schedules WHERE id = ?", (schedule_id,))
        conn.commit()
