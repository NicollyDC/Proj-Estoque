"""Fila local de operações pendentes, preparada para futura sincronização."""

from dataclasses import dataclass
from datetime import datetime
import json
import re
import uuid


_TABELAS_SINCRONIZAVEIS = {
    "produtos",
    "notas",
    "itens",
    "vinculos",
    "saidas",
    "itens_saida",
    "ajustes_estoque",
}

_DML = re.compile(
    r"^\s*(INSERT\s+(?:OR\s+\w+\s+)?INTO|UPDATE|DELETE\s+FROM)\s+[`\"\[]?([\w]+)",
    re.IGNORECASE,
)


def _agora():
    return datetime.now().astimezone().isoformat(timespec="seconds")


@dataclass(frozen=True)
class PendingOperation:
    operation_id: str
    entity: str
    action: str
    payload: dict
    created_at: str


@dataclass(frozen=True)
class SyncStatus:
    state: str
    pending_count: int
    last_sync_at: str | None
    last_error: str | None


class SyncTracker:
    """Armazena alterações pendentes dentro do banco local recebido."""

    def __init__(self, connection):
        self._connection = connection
        self._listeners = set()
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS sync_operations (
                operation_id TEXT PRIMARY KEY,
                entity TEXT NOT NULL,
                action TEXT NOT NULL,
                payload TEXT NOT NULL,
                created_at TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending'
                    CHECK (status IN ('pending', 'synced'))
            );
            CREATE INDEX IF NOT EXISTS idx_sync_operations_status_created
                ON sync_operations(status, created_at, operation_id);
            CREATE TABLE IF NOT EXISTS sync_metadata (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                state TEXT NOT NULL DEFAULT 'local_only'
                    CHECK (state IN ('local_only', 'pending', 'syncing', 'synced', 'failed')),
                last_sync_at TEXT,
                last_error TEXT
            );
            INSERT OR IGNORE INTO sync_metadata(id, state)
                VALUES (1, 'local_only');
            """
        )
        connection.commit()

    def add_listener(self, callback):
        self._listeners.add(callback)
        return lambda: self._listeners.discard(callback)

    def _notify(self):
        for callback in tuple(self._listeners):
            callback()

    def record_sql(self, sql, parameters=(), result_id=None):
        """Registra apenas DML confirmado sobre tabelas de negócio conhecidas."""
        match = _DML.match(sql or "")
        if not match:
            return None
        statement, entity = match.groups()
        entity = entity.lower()
        if entity not in _TABELAS_SINCRONIZAVEIS:
            return None

        action = statement.split()[0].upper()
        operation_id = str(uuid.uuid4())
        if isinstance(parameters, dict):
            normalized_parameters = parameters
        else:
            normalized_parameters = list(parameters or ())
        payload = {
            "sql": sql,
            "parameters": normalized_parameters,
            "result_id": result_id,
        }
        connection = self._connection
        connection.execute(
            """INSERT INTO sync_operations
               (operation_id, entity, action, payload, created_at, status)
               VALUES (?, ?, ?, ?, ?, 'pending')""",
            (
                operation_id,
                entity,
                action,
                json.dumps(payload, ensure_ascii=False, default=str),
                _agora(),
            ),
        )
        connection.execute(
            """UPDATE sync_metadata SET state='pending', last_error=NULL
               WHERE id=1 AND state!='syncing'"""
        )
        self._notify()
        return operation_id

    def status(self):
        row = self._connection.execute(
            """SELECT m.state, m.last_sync_at, m.last_error,
                      (SELECT COUNT(*) FROM sync_operations WHERE status='pending') AS pending_count
               FROM sync_metadata m WHERE m.id=1"""
        ).fetchone()
        return SyncStatus(
            state=row[0],
            pending_count=int(row[3]),
            last_sync_at=row[1],
            last_error=row[2],
        )

    def pending_operations(self, limit=None):
        sql = """SELECT operation_id, entity, action, payload, created_at
                 FROM sync_operations WHERE status='pending'
                 ORDER BY created_at, operation_id"""
        params = ()
        if limit is not None:
            sql += " LIMIT ?"
            params = (max(0, int(limit)),)
        rows = self._connection.execute(sql, params).fetchall()
        return [
            PendingOperation(
                operation_id=row[0],
                entity=row[1],
                action=row[2],
                payload=json.loads(row[3]),
                created_at=row[4],
            )
            for row in rows
        ]

    def start_sync(self):
        """Reserva as operações pendentes para uma futura implementação de sync."""
        if not self.status().pending_count:
            return []
        self._connection.execute(
            "UPDATE sync_metadata SET state='syncing', last_error=NULL WHERE id=1"
        )
        self._connection.commit()
        self._notify()
        return self.pending_operations()

    def mark_synced(self, operation_ids):
        """Marca somente IDs confirmados pelo futuro serviço remoto."""
        ids = tuple(dict.fromkeys(operation_ids or ()))
        if not ids:
            return
        placeholders = ",".join("?" for _ in ids)
        self._connection.execute(
            f"UPDATE sync_operations SET status='synced' WHERE status='pending' AND operation_id IN ({placeholders})",
            ids,
        )
        remaining = self.status().pending_count
        if remaining:
            self._connection.execute(
                "UPDATE sync_metadata SET state='pending', last_error=NULL WHERE id=1"
            )
        else:
            self._connection.execute(
                "UPDATE sync_metadata SET state='synced', last_sync_at=?, last_error=NULL WHERE id=1",
                (_agora(),),
            )
        self._connection.commit()
        self._notify()

    def mark_failed(self, error):
        """Mantém a fila pendente quando uma futura sincronização falhar."""
        self._connection.execute(
            "UPDATE sync_metadata SET state='failed', last_error=? WHERE id=1",
            (str(error),),
        )
        self._connection.commit()
        self._notify()
