import typing as t

from flask_security.core import RoleMixin
from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .db import db


class Role(db.Model, RoleMixin):
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    description: Mapped[str] = mapped_column(String(255))

    @classmethod
    def find_by_name(cls: t.Self, _name: str) -> t.Self:
        return cls.query.filter_by(name=_name).first()


class RolesUsers(db.Model):
    __tablename__ = 'roles_users'
    __table_args__ = (
        UniqueConstraint("user_id", "role_id"),
    )

    user_id: Mapped[int] = mapped_column(
        'user_id', Integer(), ForeignKey('user.id'))
    role_id: Mapped[int] = mapped_column(
        'role_id', Integer(), ForeignKey('role.id'))
