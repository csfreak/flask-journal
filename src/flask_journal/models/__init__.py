from flask import Flask
from flask_migrate import Migrate, upgrade
from sqlalchemy.event import listens_for
from sqlalchemy.orm import ORMExecuteState, Session
from sqlalchemy_easy_softdelete.handler.rewriter import SoftDeleteQueryRewriter
from sqlalchemy_easy_softdelete.hook import IgnoredTable

from .db import db
from .entry import Entry  # noqa: F401
from .rbac import Role  # noqa: F401
from .setup import init_data
from .tag import Tag  # noqa: F401
from .user import User, UserSettings  # noqa: F401

migrate = Migrate()


def init_db(app: Flask) -> None:
    db.init_app(app)
    init_soft_delete()
    migrate.init_app(app, db)
    with app.app_context():
        upgrade()
    init_data(app)


def init_soft_delete() -> None:
    global global_rewriter
    global_rewriter = SoftDeleteQueryRewriter(
        deleted_field_name="deleted_at",
        disable_soft_delete_option_name="include_deleted",
        ignored_tables=[
            table
            for table in db.metadata.tables.values()
            if isinstance(table, IgnoredTable)
        ],
    )

    # Enable Soft Delete on all Relationship Loads
    @listens_for(Session, identifier="do_orm_execute")
    def soft_delete_execute(state: ORMExecuteState) -> None:
        if not state.is_select:
            return

        # Rewrite the statement
        adapted = global_rewriter.rewrite_statement(state.statement)

        # Replace the statement
        state.statement = adapted
