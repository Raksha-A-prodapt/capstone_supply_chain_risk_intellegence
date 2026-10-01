"""Small SQLite store for user queries and acknowledged risk incidents."""

import sqlite3
from contextlib import contextmanager
from typing import Any, Dict, Iterator, List, Optional

from config.settings import settings

DB_PATH = settings.BASE_DIR / "artifacts" / "application_state.sqlite3"


def _connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS saved_queries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            query TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            incident_key TEXT NOT NULL UNIQUE,
            category TEXT NOT NULL,
            entity_id TEXT NOT NULL,
            title TEXT NOT NULL,
            severity TEXT NOT NULL,
            description TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'OPEN',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            acknowledged_at TEXT,
            acknowledged_by TEXT
        )
        """
    )
    connection.commit()
    return connection


@contextmanager
def _connection() -> Iterator[sqlite3.Connection]:
    connection = _connect()
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def create_saved_query(username: str, query: str) -> Dict[str, Any]:
    with _connection() as connection:
        cursor = connection.execute(
            "INSERT INTO saved_queries (username, query) VALUES (?, ?)",
            (username, query),
        )
        row = connection.execute(
            "SELECT id, query, created_at FROM saved_queries WHERE id = ?",
            (cursor.lastrowid,),
        ).fetchone()
        return dict(row)


def list_saved_queries(username: str) -> List[Dict[str, Any]]:
    with _connection() as connection:
        rows = connection.execute(
            "SELECT id, query, created_at FROM saved_queries WHERE username = ? ORDER BY id DESC",
            (username,),
        ).fetchall()
        return [dict(row) for row in rows]


def delete_saved_query(username: str, query_id: int) -> bool:
    with _connection() as connection:
        cursor = connection.execute(
            "DELETE FROM saved_queries WHERE id = ? AND username = ?",
            (query_id, username),
        )
        return cursor.rowcount > 0


def sync_incidents(incidents: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    with _connection() as connection:
        connection.executemany(
            """
            INSERT OR IGNORE INTO incidents
                (incident_key, category, entity_id, title, severity, description)
            VALUES (:incident_key, :category, :entity_id, :title, :severity, :description)
            """,
            incidents,
        )
        rows = connection.execute(
            """
            SELECT id, incident_key, category, entity_id, title, severity,
                   description, status, created_at, acknowledged_at, acknowledged_by
            FROM incidents ORDER BY created_at DESC, id DESC
            """
        ).fetchall()
        return [dict(row) for row in rows]


def acknowledge_incident(incident_id: int, username: str) -> Optional[Dict[str, Any]]:
    with _connection() as connection:
        connection.execute(
            """
            UPDATE incidents
            SET status = 'ACKNOWLEDGED', acknowledged_at = CURRENT_TIMESTAMP,
                acknowledged_by = ?
            WHERE id = ? AND status = 'OPEN'
            """,
            (username, incident_id),
        )
        row = connection.execute(
            """
            SELECT id, incident_key, category, entity_id, title, severity,
                   description, status, created_at, acknowledged_at, acknowledged_by
            FROM incidents WHERE id = ?
            """,
            (incident_id,),
        ).fetchone()
        return dict(row) if row else None