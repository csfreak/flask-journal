import typing as t
from datetime import datetime

from flask import Flask
from mock import MagicMock, patch

from flask_journal.models.base import JournalBaseModel
from flask_journal.views import base as base_view

from ...base import UserAppTestBase
from ...config import html_test_strings

# @pytest.mark.parametrize(
#     "logged_in_user_context", ["user3@example.test"], indirect=True
# )
# @pytest.mark.usefixtures("logged_in_user_context")


class TableViewFunctionTest(UserAppTestBase):
    def setUp(self: t.Self, app: Flask) -> None:
        self.test_table_route = "/tests"

        self.mock_utils: MagicMock = patch("flask_journal.views.base.utils").start()
        self.model_class = MagicMock(name="JournalBaseModel", spec=JournalBaseModel)
        self.model_class.configure_mock(__name__="JournalBaseModelMock")
        self.model_class.side_effect = self._new_model_class

        self.pg_order_query_mock = (
            self.mock_utils.build_query.return_value.order_by.return_value.paginate.return_value
        )
        self.pg_query_mock = (
            self.mock_utils.build_query.return_value.paginate.return_value
        )

        @app.route(self.test_table_route)
        def test() -> None:
            pass

        return super().setUp(app)

    def tearDown(self: t.Self, app: Flask) -> None:
        patch.stopall()
        return super().tearDown(app)

    def _new_model_class(self: t.Self) -> MagicMock:
        return MagicMock(name="JournalBaseModel", spec=JournalBaseModel)

    def _make_table_items(self: t.Self, count: int) -> list[MagicMock]:
        response: list[MagicMock] = []
        for i in range(count):
            m: MagicMock = self.model_class()
            m.configure_mock(id=i, created_at=datetime.now(), deleted_at=None)
            response.append(m)
        return response

    def test_no_results(self: t.Self, app: Flask) -> None:
        self.pg_order_query_mock.items = []

        with app.test_request_context(self.test_table_route):
            rv = base_view.table_view(self.model_class, endpoint="test")
            self.assertIn(html_test_strings["title"] % "Test", rv)
            self.assertIn(html_test_strings["table"]["base"], rv)
            self.assertIn(html_test_strings["table"]["pager"]["form"], rv)
            self.assertIn(
                html_test_strings["table"]["create"] % self.test_table_route, rv
            )

    def test_1_result(self: t.Self, app: Flask) -> None:
        test_items = self._make_table_items(1)
        self.pg_order_query_mock.items = test_items
        test_titles = [("id", "Test_ID", 2), ("created_at", "Test Value", 4)]
        with app.test_request_context(self.test_table_route):
            rv = base_view.table_view(
                self.model_class, endpoint="test", titles=test_titles
            )
            self.assertIn(html_test_strings["title"] % "Test", rv)
            self.assertIn(html_test_strings["table"]["base"], rv)
            for _, name, size in test_titles:
                self.assertIn(html_test_strings["table"]["title"] % (size, name), rv)
            for item in test_items:
                self.assertIn(
                    html_test_strings["table"]["row"]
                    % (item.id, item.id, item.created_at),
                    rv,
                )
            self.assertIn(html_test_strings["table"]["pager"]["form"], rv)
            self.assertIn(
                html_test_strings["table"]["create"] % self.test_table_route, rv
            )

    def test_20_result(self: t.Self, app: Flask) -> None:
        test_items = self._make_table_items(20)
        self.pg_order_query_mock.items = test_items[0:10]
        self.pg_order_query_mock.page = 1
        self.pg_order_query_mock.iter_pages.return_value = [1, 2]
        test_titles = [("id", "Test_ID", 2), ("created_at", "Test Value", 4)]
        with app.test_request_context(self.test_table_route):
            rv = base_view.table_view(
                self.model_class, endpoint="test", titles=test_titles
            )
            self.assertIn(html_test_strings["title"] % "Test", rv)
            self.assertIn(html_test_strings["table"]["base"], rv)
            for _, name, size in test_titles:
                self.assertIn(html_test_strings["table"]["title"] % (size, name), rv)
            for item in test_items[0:10]:
                self.assertIn(
                    html_test_strings["table"]["row"]
                    % (item.id, item.id, item.created_at),
                    rv,
                )
            for item in test_items[10:]:
                self.assertNotIn(
                    html_test_strings["table"]["row"]
                    % (item.id, item.id, item.created_at),
                    rv,
                )
            self.assertIn(html_test_strings["table"]["pager"]["form"], rv)
            self.assertIn(html_test_strings["table"]["pager"]["current_page"] % 1, rv)
            self.assertIn(html_test_strings["table"]["pager"]["other_page"] % 2, rv)
            self.assertIn(
                html_test_strings["table"]["create"] % self.test_table_route, rv
            )

    def test_20_result_page_2(self: t.Self, app: Flask) -> None:
        test_items = self._make_table_items(20)
        self.pg_order_query_mock.items = test_items[10:]
        self.pg_order_query_mock.page = 2
        self.pg_order_query_mock.iter_pages.return_value = [1, 2]
        test_titles = [("id", "Test_ID", 2), ("created_at", "Test Value", 4)]
        with app.test_request_context(self.test_table_route):
            rv = base_view.table_view(
                self.model_class, endpoint="test", titles=test_titles
            )
            self.assertIn(html_test_strings["title"] % "Test", rv)
            self.assertIn(html_test_strings["table"]["base"], rv)
            for _, name, size in test_titles:
                self.assertIn(html_test_strings["table"]["title"] % (size, name), rv)
            for item in test_items[0:10]:
                self.assertNotIn(
                    html_test_strings["table"]["row"]
                    % (item.id, item.id, item.created_at),
                    rv,
                )
            for item in test_items[10:]:
                self.assertIn(
                    html_test_strings["table"]["row"]
                    % (item.id, item.id, item.created_at),
                    rv,
                )
            self.assertIn(html_test_strings["table"]["pager"]["form"], rv)
            self.assertIn(html_test_strings["table"]["pager"]["current_page"] % 2, rv)
            self.assertIn(html_test_strings["table"]["pager"]["other_page"] % 1, rv)
            self.assertIn(
                html_test_strings["table"]["create"] % self.test_table_route, rv
            )

    def test_order(self: t.Self, app: Flask) -> None:
        self.pg_order_query_mock.items = []

        with app.test_request_context(self.test_table_route):
            rv = base_view.table_view(
                self.model_class, endpoint="test", order_field="created_at"
            )
            self.assertIn(html_test_strings["title"] % "Test", rv)
            self.assertIn(html_test_strings["table"]["base"], rv)
            self.assertIn(html_test_strings["table"]["pager"]["form"], rv)
            self.assertIn(
                html_test_strings["table"]["create"] % self.test_table_route, rv
            )
            self.mock_utils.build_query.return_value.order_by.assert_called_once_with(
                self.model_class.created_at
            )
            self.mock_utils.build_query.return_value.order_by.return_value.paginate.assert_called_once_with(
                page=1, per_page=10
            )

    def test_order_none(self: t.Self, app: Flask) -> None:
        self.pg_query_mock.items = []

        with app.test_request_context(self.test_table_route):
            rv = base_view.table_view(
                self.model_class, endpoint="test", order_field=None
            )
            self.assertIn(html_test_strings["title"] % "Test", rv)
            self.assertIn(html_test_strings["table"]["base"], rv)
            self.assertIn(html_test_strings["table"]["pager"]["form"], rv)
            self.assertIn(
                html_test_strings["table"]["create"] % self.test_table_route, rv
            )
            self.mock_utils.build_query.return_value.order_by.assert_not_called()
            self.mock_utils.build_query.return_value.order_by.return_value.paginate.assert_not_called()
            self.mock_utils.build_query.return_value.paginate.assert_called_once_with(
                page=1, per_page=10
            )

    def test_order_invalid_field(self: t.Self, app: Flask) -> None:
        self.pg_query_mock.items = []
        del self.model_class.unknown

        with app.test_request_context(self.test_table_route):
            rv = base_view.table_view(
                self.model_class, endpoint="test", order_field="unknown"
            )
            self.assertIn(html_test_strings["title"] % "Test", rv)
            self.assertIn(html_test_strings["table"]["base"], rv)
            self.assertIn(html_test_strings["table"]["pager"]["form"], rv)
            self.assertIn(
                html_test_strings["table"]["create"] % self.test_table_route, rv
            )
            self.mock_utils.build_query.return_value.order_by.assert_not_called()
            self.mock_utils.build_query.return_value.order_by.return_value.paginate.assert_not_called()
            self.mock_utils.build_query.return_value.paginate.assert_called_once_with(
                page=1, per_page=10
            )
