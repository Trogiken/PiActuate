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
            'filename': 'f',
            'when': 'f',
            'interval': 'f',
            'backupCount': 'f'
        },
    },
    'loggers': {
        '': {  # root logger
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': False
        },
    }
}


"""
How to modify suffix of class within config, Check if handler is created by config alone

fh = TimedRotatingFileHandler(filename=os.path.join(logdir, lg['filename']), when='midnight', interval=1, backupCount=lg['backups'])
fh.suffix = lg['suffix']

formatter = logging.Formatter(formatting['format'], datefmt=formatting['date'])
fh.setFormatter(formatter)

log.addHandler(fh)
"""

logging.config.dictConfig(loggingConfig)

log = logging.getLogger('')
