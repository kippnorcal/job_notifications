from dataclasses import dataclass, field
import logging
from functools import wraps
from typing import Union
from types import FunctionType

from job_notifications.notifications import Notifications

logger = logging.getLogger(__name__)


def handled_exception(exceptions: Union[Exception, tuple]):
    if not isinstance(exceptions, tuple):
        exceptions = (exceptions,)

    def decorator_exceptions(func):
        @wraps(func)
        def wrapper_exceptions(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exceptions as e:
                handled_exception_obj = HandledException(func=func, exception=e, call_args=args, call_kwargs=kwargs)
                logger.info(handled_exception_obj)
                Notifications().add_to_exception_stack(handled_exception_obj)
        return wrapper_exceptions
    return decorator_exceptions


def timer():
    pass


def log_call():
    pass


@dataclass
class HandledException:
    func: FunctionType
    exception: Exception
    call_args: field(default_factory=list)
    call_kwargs: field(default_factory=dict)

    def _join_kwargs(self):
        if self.call_kwargs:
            return ', '.join([f"{k}={v}" for k, v in self.call_kwargs.items()])
        else:
            return "None"

    def _join_args(self):
        if self.call_args:
            return ', '.join([str(x) for x in self.call_args])
        else:
            return "None"

    def __str__(self):
        return f"{self.exception.__class__.__name__} raised on {self.func.__name__} in {self.func.__module__}" \
               f"\nArgs: {self._join_args()}" \
               f"\nKwargs: {self._join_kwargs()}"
