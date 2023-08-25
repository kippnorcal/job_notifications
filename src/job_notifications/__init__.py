from datetime import timedelta
import logging
from functools import wraps
import time
from typing import Union

from job_notifications.notifications import NotificationBase, Notifications
from job_notifications.utils.handled_exception import HandledException
from job_notifications.mail_services import create_mail_service
from job_notifications.utils.helpers import join_kwargs, join_args


logger = logging.getLogger(__name__)


def create_notifications(job_name: str, mail_service: str, *args, **kwargs) -> Notifications:
    """Entry point to package"""
    mail_service = create_mail_service(mail_service, args, kwargs)
    logs = kwargs.get('logs')
    return Notifications(job_name, mail_service, logs=logs)


def handled_exception(exceptions: Union[Exception, tuple]):
    """Decorator that handles any exception passed as an arg and logs it"""
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
                NotificationBase().add_to_exception_stack(handled_exception_obj)
        return wrapper_exceptions
    return decorator_exceptions


def timer(func):
    """Decorator that logs the runtime of the decorated function"""
    @wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = time.perf_counter()
        value = func(*args, **kwargs)
        end_time = time.perf_counter()
        run_time = end_time - start_time
        logger.info(f"{func.__module__}.{func.__name__} finished in {timedelta(seconds=run_time)}")
        return value
    return wrapper_timer


def log_call(func):
    """Decorator that logs the call args and return value of the decorated function"""
    @wraps(func)
    def wrapper_exceptions(*args, **kwargs):
        value = func(*args, **kwargs)
        args = join_args(args)
        kwargs = join_kwargs(kwargs)
        logger.info(f"{func.__module__}.{func.__name__}> args: {args} | kwargs: {kwargs} > returned: {value}")
        return value
    return wrapper_exceptions
