import logging
import logging.config
import re
import typing as t
import warnings

from flask import Flask


def init_logging(app: Flask) -> None:
    logging_config = {
        "version": 1,
        "formatters": {"default": {"()": Formatter}},
        "handlers": {
            "wsgi": {
                "class": "logging.StreamHandler",
                "stream": "ext://flask.logging.wsgi_errors_stream",
                "formatter": "default",
            },
            "null": {"class": "logging.NullHandler"},
        },
        "root": {"level": "INFO", "handlers": ["wsgi"]},
        "loggers": {
            "sqlalchemy": {
                "level": "WARNING",
            },
            "werkzeug": {"level": "INFO"},
        },
    }

    if app.debug or app.testing:
        logging_config["root"]["level"] = "DEBUG"
        logging_config["loggers"]["sqlalchemy"]["level"] = "INFO"
        logging_config["loggers"]["sqlalchemy.engine.Engine"] = {
            "level": "INFO",
            "handlers": ["null"],
        }
    else:
        warnings.filterwarnings("ignore", category=DeprecationWarning)

    logging.config.dictConfig(logging_config)


DEFAULT_FMT = "[%(asctime)s] %(levelname)s from %(name)s: %(message)s"
FLASK_FMT = "[%(asctime)s] %(levelname)s from %(name)s in %(funcName)s: %(message)s"

REQUEST_LOG_RE = re.compile(
    r'(?P<ip>\d{1,3}(\.\d{1,3}){3}) - - \[\d{2}/\w{3}/\d{4} \d{2}:\d{2}:\d{2}\] "%s"'
    r" %s %s"
)

NEWLINE_LOG_RE = re.compile(r" ?\n ?")


class Formatter(logging.Formatter):
    def __init__(self: t.Self, **kwargs: t.Any) -> None:
        kwargs.update(
            {
                "fmt": DEFAULT_FMT,
                "style": "%",
                "validate": True,
            }
        )
        super().__init__(**kwargs)

        self.default_style = self._style
        self.flask_style = logging.PercentStyle(FLASK_FMT)
        self.flask_style.validate()

    def format(self: t.Self, record: logging.LogRecord) -> str:
        """
        Format the specified record as text.

        The record's attribute dictionary is used as the operand to a
        string formatting operation which yields the returned string.
        Before formatting the dictionary, a couple of preparatory steps
        are carried out. The message attribute of the record is computed
        using LogRecord.getMessage(). If the formatting string uses the
        time (as determined by a call to usesTime(), formatTime() is
        called to format the event time. If there is exception information,
        it is formatted using formatException() and appended to the message.
        """

        # All records need asctime
        record.asctime = self.formatTime(record, self.datefmt)

        # Substitute request log record.msg
        if record.name == "werkzeug":
            record.msg = REQUEST_LOG_RE.sub(r"\g<ip> %s %s %s", record.msg)

        # Process record.msg with passed args
        record.message = record.getMessage()
        record.message = NEWLINE_LOG_RE.sub(" ", record.message)

        # apply flask_style format if record uses a flask_journal logger
        s: str = (
            self.flask_style.format(record)
            if record.name.startswith("flask_journal")
            else self.formatMessage(record)
        )

        # no change from parent
        if record.exc_info:
            # Cache the traceback text to avoid converting it multiple times
            # (it's constant anyway)
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)
        if record.exc_text:
            if s[-1:] != "\n":
                s = s + "\n"
            s = s + record.exc_text
        if record.stack_info:
            if s[-1:] != "\n":
                s = s + "\n"
            s = s + self.formatStack(record.stack_info)
        return s
