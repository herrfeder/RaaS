import os

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m' 

if not os.path.exists("raaslog"):
	os.mkdir("raaslog")


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
                    'level': 'DEBUG',
					'formatter': 'default'
					},
				'file_handle_info': {
					'class': 'logging.handlers.RotatingFileHandler',
					'formatter': 'default',
					'filename': 'raaslog/log_info.log',
					'maxBytes': 1024,
					'backupCount': 3
					},
                'file_handle_error': {
					'class': 'logging.handlers.RotatingFileHandler',
					'formatter': 'default',
                    'level':'ERROR',
					'filename': 'raaslog/log_error.log',
					'maxBytes': 1024,
					'backupCount': 3
					},
                'file_handle_warning': {
					'class': 'logging.handlers.RotatingFileHandler',
					'formatter': 'default',
                    'level':'ERROR',
					'filename': 'raaslog/log_error.log',
					'maxBytes': 1024,
					'backupCount': 3
					},


				},
    'root': {
        'level': 'DEBUG',
        'handlers': ['stdout_handle','file_handle_info','file_handle_error']
	}
}
