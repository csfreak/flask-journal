import logging
import logging.config
import warnings

from flask import Flask


def init_logging(app: Flask) -> None:
    logging_config = {
        'version': 1,
        'formatters': {'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        }},
        'handlers': {'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default'
        }},
        'root': {
            'level': 'INFO',
            'handlers': ['wsgi']
        }
    }

    if app.testing:
        logging_config['root']['level'] = 'ERROR'

    if app.debug:
        logging_config['root']['level'] = 'DEBUG'
        logging_config.update({
            'sqlalchemy': {
                'level': 'DEBUG',
                'handlers': ['wsgi']
            }
        })
    else:
        warnings.filterwarnings("ignore", category=DeprecationWarning)

    logging.config.dictConfig(logging_config)
