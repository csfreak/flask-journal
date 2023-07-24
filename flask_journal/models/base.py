import typing as t
from datetime import datetime

from flask_sqlalchemy.model import Model
from sqlalchemy import DateTime, Integer, sql
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.schema import MetaData
from sqlalchemy_easy_softdelete.mixin import generate_soft_delete_mixin_class

metadata = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
)


class JournalBaseModel(
    Model,
    generate_soft_delete_mixin_class(
        delete_method_default_value=lambda: datetime.utcnow().replace(microsecond=0)
    ),
):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), server_default=sql.func.now(), nullable=False
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=sql.func.now()
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), server_default=None
    )

    @hybrid_property
    def active(self: t.Self) -> bool:
        return self.deleted_at is None

    @active.inplace.setter
    def _active_setter(self: t.Self, value: bool) -> None:
        if self.active != value:
            self.deleted_at = datetime.utcnow() if self.active else None

    @property
    def immutable_attrs(self: t.Self) -> list[str]:
        return ["id", "created_at", "updated_at", "deleted_at"]
