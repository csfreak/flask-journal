from flask_sqlalchemy import SQLAlchemy

from .base import JournalBaseModel, metadata

# create the extension
db = SQLAlchemy(model_class=JournalBaseModel, metadata=metadata)  # type: ignore
