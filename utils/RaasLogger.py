import logging
import os
import sys

class RaasLogger():

    def __init__(self, logger_name, debug=False, filelog=True):

        self.debug_mode = debug
        self.filelog = filelog

        self.default_format = '%(asctime)s::[%(name)s]::%(levelname)s - %(message)s'

        self.mainlogger = logging.getLogger(logger_name)
        self.mainlogger = self.init_logger(self.mainlogger, self.debug, self.filelog)
    

    def init_logger(self, logger, debug_mode=False, filelog=True):

        if debug_mode == True:
            self.basic_loglevel = logging.DEBUG
        elif debug_mode == False:
            self.basic_loglevel = logging.INFO
        else:
            self.basic_loglevel = logging.INFO

        logger.setLevel(self.basic_loglevel)

        if not logger.hasHandlers():
            stdout_basic_handler = logging.StreamHandler(sys.stdout)
            stdout_basic_handler.setLevel(self.basic_loglevel)
            stdout_basic_format = logging.Formatter(self.default_format)
            stdout_basic_handler.setFormatter(stdout_basic_format)

            if filelog:
                if not os.path.exists("logs"):
                    os.mkdir("logs")

                file_basic_handler = logging.FileHandler('logs/info.log')
                file_basic_handler.setLevel(self.basic_loglevel)
                file_basic_format = logging.Formatter(self.default_format)
                file_basic_handler.setFormatter(file_basic_format)

                file_error_handler = logging.FileHandler('logs/error.log')
                file_error_handler.setLevel(logging.ERROR)
                file_error_format = logging.Formatter(self.default_format)
                file_error_handler.setFormatter(file_error_format)

                logger.addHandler(file_basic_handler)
                logger.addHandler(file_error_handler)

            # Add handlers to the logger
            logger.addHandler(stdout_basic_handler)


        return logger


    def info(self, logtext):
        self.mainlogger.info(logtext)

    def debug(self, logtext):
        self.mainlogger.debug(logtext)

    def warning(self, logtext):
        self.mainlogger.warning(logtext)

    def error(self, logtext):
        self.mainlogger.error(logtext)