import typing as t

from sqlalchemy import Column, ForeignKey, Integer, String, Table, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import db
from .mixin import OwnableMixin


class Tag(db.Model, OwnableMixin):
    __table_args__ = (UniqueConstraint("name", "user_id"),)

    name: Mapped[str] = mapped_column(String(64))

    entries: Mapped[list] = relationship(
        "Entry", secondary="entry_tags", back_populates="tags"
    )

    def __repr__(self: t.Self) -> str:
        return f"Tag: {self.name}"

    def __str__(self: t.Self) -> str:
        return self.name


EntryTags = Table(
    "entry_tags",
    db.metadata,
    Column("entry_id", Integer(), ForeignKey("entry.id"), primary_key=True),
    Column("tag_id", Integer(), ForeignKey("tag.id"), primary_key=True),
)
