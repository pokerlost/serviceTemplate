"""Reusable timestamp persistence mixin."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from .created_at_mixin import CreatedAtMixin


class TimestampMixin(CreatedAtMixin):
    """Provide standard timezone-aware persistence timestamps."""

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
