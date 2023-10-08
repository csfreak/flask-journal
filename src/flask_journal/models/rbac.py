import typing as t

from flask_security.core import RoleMixin
from sqlalchemy import ForeignKey, String, UniqueConstraint
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


class RolesUsers(db.Model):
    __tablename__ = "roles_users"
    __table_args__ = (UniqueConstraint("user_id", "role_id"),)

    user_id: Mapped[int] = mapped_column("user_id", ForeignKey("user.id"))
    role_id: Mapped[int] = mapped_column("role_id", ForeignKey("role.id"))
