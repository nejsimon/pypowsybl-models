from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column

from pypowsybl_models.base import Base


class NetworkSnapshot(Base):
    __tablename__ = "network_snapshot"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    scenario_time: Mapped[datetime] = mapped_column(index=True)
