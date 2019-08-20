from logging.config import dictConfig
import os

if not os.path.exists("log"):
	os.mkdir("log")


raas_dictconfig = {
    'version': 1,
    'formatters': {'default': {
					'class': 'logging.Formatter',
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
		}
	},
    'handlers': {'stdout_handle': {
					'class': 'logging.StreamHandler',
					'stream': 'ext://sys.stdout',
					'formatter': 'default'
					},
				'file_handle_info': {
					'class': 'logging.handlers.RotatingFileHandler',
					'formatter': 'default',
					'filename': 'log/log_info.log',
					'maxBytes': 1024,
					'backupCount': 3
					},
                'file_handle_error': {
					'class': 'logging.handlers.RotatingFileHandler',
					'formatter': 'default',
                    'level':'ERROR',
					'filename': 'log/log_error.log',
					'maxBytes': 1024,
					'backupCount': 3
					},
                'file_handle_warning': {
					'class': 'logging.handlers.RotatingFileHandler',
					'formatter': 'default',
                    'level':'ERROR',
					'filename': 'log/log_error.log',
					'maxBytes': 1024,
					'backupCount': 3
					},


				},
    'root': {
        'level': 'DEBUG',
        'handlers': ['stdout_handle','file_handle_info','file_handle_error']
	}
}