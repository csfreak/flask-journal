import typing as t
import uuid
from datetime import datetime

from flask_security.core import UserMixin
from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..views.themes import Theme
from .db import db


class User(db.Model, UserMixin):
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    fs_uniquifier: Mapped[str] = mapped_column(
        String(64), unique=True, nullable=False, default=uuid.uuid4().hex
    )
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Tracking Attributes
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(), nullable=True)
    current_login_at: Mapped[datetime | None] = mapped_column(DateTime(), nullable=True)
    last_login_ip: Mapped[str] = mapped_column(String(100), nullable=True)
    current_login_ip: Mapped[str] = mapped_column(String(100), nullable=True)
    login_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    roles = relationship("Role", secondary="roles_users", uselist=True)
    entries = relationship("Entry", back_populates="user", uselist=True)
    tags = relationship("Tag", back_populates="user", uselist=True)

    settings = relationship("UserSettings", back_populates="user", uselist=False)

    def __repr__(self: t.Self) -> str:
        return f"User: {self.email}"

    def __str__(self: t.Self) -> str:
        return self.email

    @property
    def immutable_attrs(self: t.Self) -> list[str]:
        return ["tracking"] + super().immutable_attrs

    @property
    def tracking(self: t.Self) -> t.Self:
        return self


class UserSettings(db.Model):
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False)
    # encrypt_entries: Mapped[bool] = mapped_column(
    #     Boolean, nullable=False, default=False)
    # encryption_key: Mapped[str] = mapped_column(String, nullable=True)

    theme: Mapped[Theme] = mapped_column(Enum(Theme), nullable=False, default="default")
    home_tags: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    home_preview: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    user = relationship("User", back_populates="settings", uselist=False)
