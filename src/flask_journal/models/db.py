from flask_sqlalchemy import SQLAlchemy

from .base import JournalBaseModel

# create the extension
db = SQLAlchemy(model_class=JournalBaseModel)  # type: ignore
