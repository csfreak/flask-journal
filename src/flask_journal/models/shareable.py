import logging
import typing as t

from sqlalchemy import Column, ForeignKey, Integer, Table, UniqueConstraint
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, declared_attr, relationship

from .user import User

logger = logging.getLogger(__name__)


class ShareableMixin:
    _share_name: str = ""
    _share_table: Table = None

    @classmethod
    def _make_user_rel(cls: t.Self) -> Mapped[t.Optional[list[t.Self]]]:
        return (
            relationship(
                cls,
                secondary=cls._share_name,
                back_populates="shared_with",
                uselist=True,
            ),
        )

    @classmethod
    def _make_share_table(cls: t.Self) -> str:
        if not cls._share_name:
            cls._share_name = f"shared_{cls.__tablename__}"
        if not cls._share_table:
            cls._share_table = Table(
                cls._share_name,
                cls.metadata,
                Column(
                    f"{cls.__tablename__}_id",
                    Integer(),
                    ForeignKey(f"{cls.__tablename__}.id"),
                ),
                Column("user_id", Integer(), ForeignKey("user.id")),
                UniqueConstraint(f"{cls.__tablename__}_id", "user_id"),
            )
        return cls._share_table

    @declared_attr
    def shared_with(self: t.Self) -> Mapped[t.Optional[list[User]]]:
        return relationship(
            "User",
            secondary=lambda: self._make_share_table(),
            uselist=True,
        )

    @hybrid_property
    def shared(self: t.Self) -> bool:
        return self.public or len(self.shared_with) != 0

    @shared.inplace.setter
    def _shared_setter(self: t.Self, value: bool) -> None:
        self.shared_with = []
