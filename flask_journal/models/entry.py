import base64
import typing as t

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import db


class Entry(db.Model):
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False)
    _title: Mapped[str] = mapped_column(String(), nullable=False)
    _data: Mapped[str] = mapped_column(Text, nullable=False, default="")
    encrypted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    user = relationship("User", back_populates="entries", uselist=False)
    tags = relationship(
        "Tag", secondary="entry_tags", back_populates="entries", uselist=True
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

    def _decode_data(self: t.Self, data: str | bytes) -> str:
        b: bytes = base64.b64decode(data)
        if self.encrypted:
            b = self._decrypt(b)  # pragma: no cover
        return b.decode("UTF-8")

    def _encode_data(self: t.Self, value: str) -> str:
        b: bytes = value.encode("UTF-8")
        if self.encrypted:
            b = self._encrypt(b)  # pragma: no cover
        return base64.b64encode(b).decode("UTF-8")

    def _encrypt(self: t.Self, data: bytes) -> bytes:  # pragma: no cover
        # TODO
        return data

    def _decrypt(self: t.Self, data: bytes) -> bytes:  # pragma: no cover
        # TODO
        return data
