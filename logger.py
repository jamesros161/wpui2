# -*- coding: utf-8 -*-
"""Constructs Application logger
"""
import logging
import sys
import io
import getpass
import inspect


class Log():
    """Logging class for application logger
    """
    def __init__(self, settings):

        self.app_logger, self.error_log = self.applogger(settings)

        self.info = self.app_logger.info
        self.debug = self.app_logger.debug
        self.warning = self.app_logger.warning

        # self.debug('Number of Handlers = %s', len(self.app_logger.handlers))

    def applogger(self, settings):
        """Defines the logger for this applaication

        Arguments:
            settings {obj} -- Settings object

        Returns:
            obj -- logger object
        """

        logger = logging.getLogger('appLogger')

        if not logger.handlers:
            logging.addLevelName(10, "**DEBUG**")
            logging.addLevelName(20, "**INFO** ")
            logging.addLevelName(30, "*WARNING*")
            logging.addLevelName(40, "**ERROR**")
            logging.addLevelName(50, "**FATAL**")

            logger.setLevel(settings.logging['level'])

            log_name = "wpui.log"
            log_datefmt = "[%m/%d/%Y] %H:%M:%S"
            logpath = ''
            if getpass.getuser() == 'root':
                logpath = '/root/' + log_name
            else:
                logpath = '/home/' + getpass.getuser() + '/' + log_name

            handler = logging.FileHandler(logpath)

            log_format = (
                "%(asctime)s.%(msecs)03d (%(levelname)s)\n    %(module)s "
                "/ %(funcName)s:%(lineno)4d\n        %(message)s"
            )
            formatter = logging.Formatter(log_format, log_datefmt)
            handler.setFormatter(formatter)

            logger.addHandler(handler)

            error_capture_string = io.StringIO()
            error_handler = logging.StreamHandler(error_capture_string)
            error_handler.setLevel(logging.WARNING)

            error_formatter = logging.Formatter(
                '%(module)s.%(funcName)s (%(lineno)s) :: %(message)s')
            error_handler.setFormatter(error_formatter)

            logger.addHandler(handler)
            logger.addHandler(error_handler)

        return logger, error_capture_string

    def change_format(self, format_name):
        """Changes format type

        Arguments:
            format_name {str} -- format name
        """

        if format_name == 'exit_with_errors':
            self.app_logger.handlers[0].setFormatter(
                logging.Formatter(
                    '%(message)s'))

    @staticmethod
    def handle_exception(exc_type, exc_value, exc_traceback):
        """Handles all otherwise unhandled exceptions, sending them to the Log

        Arguments:
            exc_type {[str]} -- [Type of exception]
            exc_value {[str]} -- [Value of exception]
            exc_traceback {[str]} -- [Exception traceback]
        """
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        app_logger = logging.getLogger('appLogger')
        app_logger.error(
            "Uncaught exception",
            exc_info=(
                exc_type,
                exc_value,
                exc_traceback))

    def set_level(self, level):
        """"Sets the logger level"""
        self.app_logger.setLevel(level)
