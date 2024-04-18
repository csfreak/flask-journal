import typing as t
import uuid
from datetime import datetime

from flask_security.core import UserMixin
from sqlalchemy import DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_easy_softdelete.hook import IgnoredTable

from ..views.themes import Theme
from .db import db

if t.TYPE_CHECKING:
    Entry = db.Model
    Tag = db.Model
    Role = db.Model


class User(db.Model, UserMixin):
    email: Mapped[str] = mapped_column(String(255), unique=True)
    name: Mapped[t.Optional[str]] = mapped_column(String(255), unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    fs_uniquifier: Mapped[str] = mapped_column(
        String(64), unique=True, default=uuid.uuid4().hex
    )
    confirmed_at: Mapped[t.Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Tracking Attributes
    last_login_at: Mapped[t.Optional[datetime]] = mapped_column(DateTime(timezone=True))
    current_login_at: Mapped[t.Optional[datetime]] = mapped_column(
        DateTime(timezone=True)
    )
    last_login_ip: Mapped[t.Optional[str]] = mapped_column(String(100))
    current_login_ip: Mapped[t.Optional[str]] = mapped_column(String(100))
    login_count: Mapped[int] = mapped_column(default=0)

    roles: Mapped[t.Optional[list["Role"]]] = relationship(secondary="roles_users")
    # entries: Mapped[t.Optional[list["Entry"]]] = relationship(back_populates="user")
    # tags: Mapped[t.Optional[list["Tag"]]] = relationship(back_populates="user")

    settings: Mapped["UserSettings"] = relationship(back_populates="user")

    def __repr__(self: t.Self) -> str:
        return f"User: {self.email}"

    def __str__(self: t.Self) -> str:
        return self.name if self.name else self.email

    @property
    def immutable_attrs(self: t.Self) -> list[str]:
        return ["tracking"] + super().immutable_attrs

    @property
    def tracking(self: t.Self) -> t.Self:
        return self


class UserSettings(db.Model, IgnoredTable):
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))

    theme: Mapped[Theme] = mapped_column(Enum(Theme), default="default")
    home_tags: Mapped[bool] = mapped_column(default=True)
    home_preview: Mapped[bool] = mapped_column(default=True)

    user: Mapped["User"] = relationship(back_populates="settings")
