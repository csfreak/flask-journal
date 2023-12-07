import base64
import typing as t

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import db
from .tag import Tag
from .user import User


class Entry(db.Model):
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    _title: Mapped[str] = mapped_column(String(255))
    _data: Mapped[str] = mapped_column(Text, default="")

    user: Mapped[User] = relationship(back_populates="entries")
    tags: Mapped[list[Tag]] = relationship(
        secondary="entry_tags", back_populates="entries"
    )

    @hybrid_property
    def content(self: t.Self) -> str:
        return self._decode_data(self._data)

    @content.inplace.setter
    def _content_setter(self: t.Self, value: str) -> None:
        self._data = self._encode_data(value)

    @hybrid_property
    def title(self: t.Self) -> str:
        return self._decode_data(self._title)

    @title.inplace.setter
    def _title_setter(self: t.Self, value: str) -> None:
        self._title = self._encode_data(value)

    def _decode_data(self: t.Self, data: str | bytes = None) -> str:
        if not data:
            return ""
        b: bytes = base64.b64decode(data)
        return b.decode("UTF-8")

    def _encode_data(self: t.Self, value: str) -> str:
        b: bytes = value.encode("UTF-8")
        return base64.b64encode(b).decode("UTF-8")
