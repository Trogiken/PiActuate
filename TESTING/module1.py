import logging.config

loggingConfig = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'standard',
            'filename': 'logconfig',
            'maxBytes': 1024,
            'backupCount': '5'
        },
    },
    'loggers': {
        'root': {
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': False
        },
    }
}

"""
Have root use a handler that uses the SteamHandler class and then add a timed rotating handler in code

fh = TimedRotatingFileHandler(os.path.join(logdir, lg['filename']), when='midnight', interval=1, backupCount=lg['backups'])
fh.suffix = lg['suffix']

formatter = logging.Formatter(formatting['format'], datefmt=formatting['date'])
fh.setFormatter(formatter)

log.addHandler(fh)
"""

logging.config.dictConfig(loggingConfig)

log = logging.getLogger('root')
