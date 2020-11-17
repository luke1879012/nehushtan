#  Copyright (c) 2020. Sinri Edogawa

import json
import logging
import logging.handlers
import sys


class NehushtanLogger:
    """
    A Logger Class For Shovel
    """

    def __init__(self, logger_name: str, handlers=(), universal_log_level=logging.DEBUG):
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(universal_log_level)
        for handler in handlers:
            handler.setFormatter(
                logging.Formatter("%(asctime)s <%(shovel_name)s> [%(levelname)s] %(message)s | %(json_string)s")
            )
            self.logger.addHandler(handler)

    def debug(self, message: str, extra=None):
        self.logger.debug(
            msg=message,
            extra=self.ensure_extra_as_dict(extra)
        )

    def info(self, message: str, extra=None):
        self.logger.info(
            msg=message,
            extra=self.ensure_extra_as_dict(extra)
        )

    def warning(self, message: str, extra=None):
        self.logger.warning(
            msg=message,
            extra=self.ensure_extra_as_dict(extra)
        )

    def error(self, message: str, extra=None):
        self.logger.error(
            msg=message,
            extra=self.ensure_extra_as_dict(extra)
        )

    def exception(self, message: str, exception: BaseException):
        """
        Since version 1.2 彭启航之野望
        :param message:
        :param exception:
        :return:
        """
        self.logger.exception(
            msg=message,
            extra=self.ensure_extra_as_dict(exception.__str__()),
            stack_info=True,
        )

    def critical(self, message: str, extra=None):
        self.logger.critical(
            msg=message,
            extra=self.ensure_extra_as_dict(extra)
        )

    @staticmethod
    def make_silent_handler():
        s_handler = logging.NullHandler()
        return s_handler

    @staticmethod
    def make_stdout_handler(logger_level=logging.DEBUG):
        s_handler = logging.StreamHandler(stream=sys.stdout)
        s_handler.setLevel(logger_level)
        return s_handler

    @staticmethod
    def make_stderr_handler(logger_level=logging.WARN):
        s_handler = logging.StreamHandler(stream=sys.stderr)
        s_handler.setLevel(logger_level)
        return s_handler

    @staticmethod
    def make_timed_rotating_file_handler(file_name='shovel.log', logger_level=logging.DEBUG, backup_count=7):
        rf_handler = logging.handlers.TimedRotatingFileHandler(
            filename=file_name,
            when='midnight',
            interval=1,
            backupCount=backup_count
        )
        rf_handler.setLevel(logger_level)
        return rf_handler

    @staticmethod
    def make_fixed_file_handler(file_name='shovel.log', logger_level=logging.DEBUG):
        f_handler = logging.FileHandler(file_name)
        f_handler.setLevel(logger_level)
        return f_handler

    def ensure_extra_as_dict(self, extra):
        return {
            "json_string": json.dumps(extra, default=lambda inner_x: inner_x.__str__()),
            "shovel_name": self.logger.name
        }

    @staticmethod
    def get_shovel_logger_for_runner(logger_name: str):
        """
        Just output to STDERR
        :param logger_name:
        :return:
        """
        return NehushtanLogger(
            logger_name=logger_name,
            handlers=[NehushtanLogger.make_stderr_handler()]
        )

    @staticmethod
    def get_shovel_logger_for_job(logger_name: str):
        """
        Just output to STDOUT
        :param logger_name:
        :return:
        """
        return NehushtanLogger(
            logger_name=logger_name,
            handlers=[NehushtanLogger.make_stdout_handler()]
        )

    @staticmethod
    def get_shovel_logger_for_detail(logger_name: str, file_name: str, backup_count=7, logger_level=logging.DEBUG):
        """
        Just output to a rotating file
        :param logger_name:
        :param file_name:
        :param backup_count:
        :param logger_level:
        :return:
        """
        return NehushtanLogger(
            logger_name=logger_name,
            handlers=[
                NehushtanLogger.make_timed_rotating_file_handler(
                    file_name=file_name, backup_count=backup_count, logger_level=logger_level
                )
            ]
        )

    @staticmethod
    def get_silent_logger(logger_name: str):
        return NehushtanLogger(
            logger_name=logger_name,
            handlers=[NehushtanLogger.make_silent_handler()]
        )
