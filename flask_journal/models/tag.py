import typing as t

from sqlalchemy import (Boolean, ForeignKey, Integer, String, Text,
                        UniqueConstraint)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from .db import db


class Tag(db.Model):
    __table_args__ = (
        UniqueConstraint("name", "user_id"),
    )

    name: Mapped[str] = mapped_column(String(64), nullable=False)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('user.id'), nullable=False)

    user = relationship('User', back_populates='tags', uselist=False)
    entries = relationship('Entry', secondary="entry_tags",
                           back_populates='tags', uselist=True)


class EntryTags(db.Model):
    __tablename__ = 'entry_tags'
    __table_args__ = (
        UniqueConstraint("entry_id", "tag_id"),
    )

    entry_id: Mapped[int] = mapped_column(
        'entry_id', Integer(), ForeignKey('entry.id'))
    tag_id: Mapped[int] = mapped_column(
        'tag_id', Integer(), ForeignKey('tag.id'))
