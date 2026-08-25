"""Registration facade for concrete SQLAlchemy models.

Import each concrete ``*Model`` here so Alembic discovers its table through ``Base.metadata``.
The pristine generated service intentionally defines no concrete persistence entity.
"""

from __future__ import annotations

__all__: tuple[str, ...] = ()
