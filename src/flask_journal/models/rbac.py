import typing as t

from flask_security.core import RoleMixin
from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import Mapped, mapped_column

from .db import db


class Role(db.Model, RoleMixin):
    name: Mapped[str] = mapped_column(String(80))
    description: Mapped[t.Optional[str]] = mapped_column(String(255))

    @classmethod
    def find_by_name(cls: t.Self, value: str) -> t.Self:
        return cls.find_by_attr(cls.name, value)

    def __repr__(self: t.Self) -> str:
        return f"Role: {self.name}"

    def __str__(self: t.Self) -> str:
        return self.name


RoleUsers = Table(
    "roles_users",
    db.metadata,
    Column("user_id", Integer(), ForeignKey("user.id"), primary_key=True),
    Column("role_id", Integer(), ForeignKey("role.id"), primary_key=True),
)
