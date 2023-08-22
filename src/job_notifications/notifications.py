from functools import wraps
from typing import Union


class Notifications:

    _exception_stack = []

    def __init__(self):
        pass

    def add_log(self):
        pass

    @classmethod
    def add_to_exception_stack(cls, e):
        cls._exception_stack.append(e)

    @classmethod
    def exception_stack(cls):
        return cls._exception_stack

    def notify(self):
        """
        Sends out notification of job completion and the status.
        :return:
        """
        pass

    def simple_email(self):
        """

        :return:
        """
        pass

