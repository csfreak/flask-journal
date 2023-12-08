import logging
import typing as t
from datetime import datetime
from math import ceil

Model = t.TypeVar("Model", bound="MockModel")
Form = t.TypeVar("Form", bound="MockForm")
logger = logging.getLogger(__name__)


class MockPagination:
    page: int
    per_page: int

    _items: list[Model]

    def __init__(self: t.Self, page: int, per_page: int, _items: list[Model]) -> None:
        self.page = page
        self.per_page = per_page
        self._items = _items
        logger.debug("Initialize New MockPagination")
        logger.debug(
            "page %d contains %d items with ids %s out of %d total items",
            self.page,
            len(self.items),
            [m.id for m in self.items],
            self.total,
        )

    @property
    def first(self: t.Self) -> int:
        return ((self.page - 1) * self.per_page) + 1

    @property
    def last(self: t.Self) -> int:
        return min(self.first + self.per_page, len(self._items) + 1)

    @property
    def items(self: t.Self) -> list[Model]:
        return self._items[self.first - 1 : self.last - 1]

    @property
    def total(self: t.Self) -> int:
        return len(self._items)

    @property
    def pages(self: t.Self) -> int:
        if self.total == 0 or self.total is None:
            return 0

        return ceil(self.total / self.per_page)

    def iter_pages(self: t.Self) -> t.Iterator[int | None]:
        if self.pages <= 1:
            return

        yield from range(1, self.pages + 1)


class MockInstAttr:
    _shared_with: list

    def __init__(self: t.Self, _shared_with: list | t.Any = None) -> None:
        if isinstance(_shared_with, list):
            self._shared_with = _shared_with
        else:
            self._shared_with = [_shared_with]

    def any(self: t.Self, *args: bool) -> str:
        self.any = args
        return any(args)

    def contains(self: t.Self, obj: t.Any) -> str:
        self.contains = obj
        return obj in self._shared_with


class MockModel:
    id: int = None
    created_at: datetime = None
    deleted_at: datetime = None
    ownable: bool = True
    shareable: bool = False
    shared_with: MockInstAttr = MockInstAttr()

    def __init__(self: t.Self, **kwargs: t.Any) -> None:
        logger.debug("Initialize new MockModel")
        self.user = kwargs.get("user")
        self.created_at = kwargs.get("created_at", datetime.now())
        self._shared_users = kwargs.get("shared_with", list())
        self.shared_with._shared_with = self._shared_users

    def delete(self: t.Self) -> None:
        self.deleted_at = datetime.now()

    def undelete(self: t.Self) -> None:
        self.deleted_at = None


class MockSelect:
    filter: dict[str, t.Any]
    include_deleted: bool = False
    order_field: bool = False
    order_desc: bool = False
    _items: list[Model] = []
    where_exp = False

    def __init__(self: t.Self, model: MockModel) -> None:
        self.model = model
        logger.debug("Initialize New MockQuery")
        self.filter = {}

    def __call__(self: t.Self, *args: t.Any) -> t.Self:
        match len(args):
            case 0:
                return self
            case 1:
                if args[0] is self.model:
                    return self
                raise AttributeError("wrong value passed to select")
            case _:
                raise ValueError("to many values passed to select")

    def filter_by(self: t.Self, **kwargs: t.Any) -> t.Self:
        logger.debug("filter_by called with %s", kwargs)
        self.filter.update(kwargs)
        return self

    def execution_options(self: t.Self, include_deleted: bool) -> t.Self:
        logger.debug(
            "execution_options called with include_deleted=%s", include_deleted
        )
        self.include_deleted = include_deleted
        return self

    def order_by(self: t.Self, order_exp: t.Any) -> t.Self:
        logger.debug("order_by called with %s", order_exp)
        if isinstance(order_exp, str):
            self.order_desc = True

        self.order_field = True
        return self

    def where(self: t.Self, exp: t.Any) -> t.Self:
        self.where_exp = exp
        return self


class MockForm:
    _valid: bool = False

    def __init__(self: t.Self, *args: t.Any, **kwargs: t.Any) -> None:
        logger.debug("Initialize new MockForm")
        if not hasattr(self, "args"):
            self.args = []
        self.args.extend(args)
        if not hasattr(self, "populated"):
            self.populated = None
        if not hasattr(self, "data"):
            self.data = {}
        self.process(**kwargs)

    def populate_obj(self: t.Self, obj: Model) -> None:
        logger.debug("populate obj %s from form", obj)
        self.populated = obj
        obj.data = self.data

    def validate_on_submit(self: t.Self) -> bool:
        return self._valid

    def process(self: t.Self, **kwargs: t.Any) -> None:
        logger.debug("proccess form data %s", kwargs)
        for k, v in kwargs.items():
            setattr(self, k, v)


class MockSession:
    def __init__(self: t.Self) -> None:
        logger.debug("Initialize new MockSession")

    def add(self: t.Self, obj: Model) -> None:
        if not Model:
            raise ValueError("add called without obj")
        self.add = obj

    def commit(self: t.Self) -> None:
        if not hasattr(self, "add"):
            raise ValueError("commit called without add")

    def scalar(self: t.Self, select: MockSelect) -> Model:
        return select._items[0] if select._items else None


class MockDB:
    def __init__(self: t.Self) -> None:
        logger.debug("Initialize new MockDB")
        self.session = MockSession()

    def paginate(self: t.Self, select: MockSelect, **kwargs: t.Any) -> MockPagination:
        return MockPagination(**kwargs, _items=select._items)


class MockFlash:
    def __init__(self: t.Self, **kwargs: str) -> None:
        self.called = {}
        self.expected = kwargs if kwargs else {}
        logger.debug("Initialize new MockFlash")

    def flash(self: t.Self, message: str, **kwargs: t.Any) -> None:
        self.called.update(kwargs)
        self.called.update(message=message)
