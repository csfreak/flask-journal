import typing as t

from sqlalchemy import ForeignKey, String, UniqueConstraint
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


class EntryTags(db.Model):
    __tablename__ = "entry_tags"
    __table_args__ = (UniqueConstraint("entry_id", "tag_id"),)

    entry_id: Mapped[int] = mapped_column("entry_id", ForeignKey("entry.id"))
    tag_id: Mapped[int] = mapped_column("tag_id", ForeignKey("tag.id"))
