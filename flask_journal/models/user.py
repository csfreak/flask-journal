import uuid
from datetime import datetime

from flask_security.core import UserMixin
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import db


class User(db.Model, UserMixin):

    email: Mapped[str] = mapped_column(String(255), unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    fs_uniquifier: Mapped[str] = mapped_column(
        String(64), unique=True, nullable=False, default=uuid.uuid4().hex)

    # Tracking Attributes
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(), nullable=True)
    current_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(), nullable=True)
    last_login_ip: Mapped[str] = mapped_column(String(100), nullable=True)
    current_login_ip: Mapped[str] = mapped_column(String(100), nullable=True)
    login_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0)

    roles = relationship('Role', secondary='roles_users', uselist=True)
    entries = relationship('Entry', back_populates='user', uselist=True)
    tags = relationship('Tag', back_populates='user', uselist=True)

    settings = relationship(
        "UserSettings", back_populates='user', uselist=False)


class UserSettings(db.Model):
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id"), nullable=False)
    encrypt_entries: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False)
    encryption_key: Mapped[str] = mapped_column(String, nullable=True)

    user = relationship('User', back_populates='settings', uselist=False)
