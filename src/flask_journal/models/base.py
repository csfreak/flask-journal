import logging
import typing as t
from datetime import UTC, datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DateTime, Integer, select, sql
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.schema import MetaData

logger = logging.getLogger(__name__)


class JournalBaseModel(DeclarativeBase):
    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }
    )

    __fsa__: SQLAlchemy  # instantiated SQLalchemy added during init

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[t.Optional[datetime]] = mapped_column(
        DateTime(timezone=True), server_default=sql.func.now(), nullable=False
    )
    updated_at: Mapped[t.Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=sql.func.now()
    )
    deleted_at: Mapped[t.Optional[datetime]] = mapped_column(DateTime(timezone=True))

    ownable: bool = False
    shareable: bool = False

    @hybrid_property
    def active(self: t.Self) -> bool:
        return self.deleted_at is None

    @active.inplace.setter
    def _active_setter(self: t.Self, value: bool) -> None:
        if self.active != value:
            self.undelete() if value else self.delete()

    @property
    def immutable_attrs(self: t.Self) -> list[str]:
        return ["id", "created_at", "updated_at", "deleted_at"]

    @classmethod
    def find_by_id(cls: t.Self, id: int) -> t.Self:
        return cls.__fsa__.session.get(cls, id)

    @classmethod
    def find_by_attr(
        cls: t.Self, attr: str | InstrumentedAttribute, value: t.Any
    ) -> t.Self:
        if not isinstance(attr, InstrumentedAttribute):
            if not hasattr(cls, attr):
                raise AttributeError(cls, attr)
            attr = getattr(cls, attr)
        return cls.__fsa__.session.scalar(select(cls).where(attr == value))

    def delete(self: t.Self) -> None:
        if self.deleted_at:
            logger.warning(
                "Unable to delete %s: already deleted at %s", self, self.deleted_at
            )
            return None
        self.deleted_at = datetime.now(UTC).replace(microsecond=0)

    def undelete(self: t.Self) -> None:
        if self.deleted_at is None:
            logger.warning("Unable to undelete %s: 'deleted_at' is None")
            return None
        self.deleted_at = None

    def __str__(self: t.Self) -> str:
        return f"{self.__class__.__name__}: {self.id}"
