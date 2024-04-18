import logging
import typing as t

from flask_security.core import UserMixin
from sqlalchemy import Column, ForeignKey, Integer, Table
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, backref, declared_attr, mapped_column, relationship

from ..utils import pluralize

logger = logging.getLogger(__name__)


class OwnableMixin:
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))

    @declared_attr
    def user(self: t.Self) -> Mapped[UserMixin]:
        return relationship(
            "User",
            backref=backref(
                pluralize(self.__tablename__),
                uselist=True,
                single_parent=True,
            ),
            uselist=False,
        )

    def __init_subclass__(cls: t.Self, **kwargs: t.Any) -> None:
        super().__init_subclass__(**kwargs)
        cls.ownable = True


class ShareableMixin(OwnableMixin):
    _share_name: str = ""
    _share_table: Table = None

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
                    primary_key=True,
                ),
                Column("user_id", Integer(), ForeignKey("user.id"), primary_key=True),
            )
        return cls._share_table

    @declared_attr
    def shared_with(self: t.Self) -> Mapped[t.Optional[list[UserMixin]]]:
        return relationship(
            "User",
            secondary=lambda: self._make_share_table(),
            backref=backref(f"shared_{pluralize(self.__tablename__)}", uselist=True),
            uselist=True,
        )

    @hybrid_property
    def shared(self: t.Self) -> bool:
        return self.public or len(self.shared_with) != 0

    @shared.inplace.setter
    def _shared_setter(self: t.Self, value: bool) -> None:
        self.shared_with = []

    def __init_subclass__(cls: t.Self, **kwargs: t.Any) -> None:
        super().__init_subclass__(**kwargs)
        cls.shareable = True
