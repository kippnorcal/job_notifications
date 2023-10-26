from datetime import timedelta
import logging
from functools import wraps
import time
from typing import Union, Tuple, List

from job_notifications.notifications import NotificationBase, Notifications
from job_notifications.utils.handled_exception import HandledException
from job_notifications.mail_services import create_mail_service
from job_notifications.utils.helpers import join_kwargs, join_args


def create_notifications(job_name: str,
                         mail_service: str,
                         logs: Union[None, str, List[str]] = None, *args, **kwargs) -> Notifications:
    """Entry point to package"""
    mail_service_obj = create_mail_service(mail_service, args, kwargs)
    notifications_obj = Notifications(job_name, mail_service_obj)
    if isinstance(logs, str):
        notifications_obj.add_log(logs)
    elif isinstance(logs, list):
        for log in logs:
            notifications_obj.add_log(log)
    return notifications_obj


def handled_exception(exceptions: Union[BaseException, Tuple[BaseException]], re_raise: Union[list, bool] = False):
    """
    Decorator that handles any exception(s) passed as an arg and logs it. re_raise param will re-raise any of the
    exceptions the decorator handles after it has been logged. Pass True to re_raise param to re-raise all exceptions or
    a list of exceptions to be re-raised.
    """
    if not isinstance(exceptions, tuple):
        exceptions = (exceptions,)

    def decorator_exceptions(func):
        @wraps(func)
        def wrapper_exceptions(*args, **kwargs):
            logger = logging.getLogger(__name__)
            try:
                return func(*args, **kwargs)
            except exceptions as e:  # type: ignore
                handled_exception_obj = HandledException(func=func, exception=e, call_args=args, call_kwargs=kwargs)
                logger.info(handled_exception_obj)
                NotificationBase().add_to_exception_stack(handled_exception_obj)
                if re_raise:
                    if isinstance(re_raise, list):
                        for element in re_raise:
                            if type(e) == element:
                                raise e
                    elif not isinstance(re_raise, list):
                        raise e
        return wrapper_exceptions
    return decorator_exceptions


def timer(name: Union[None, str] = None):
    """Decorator that logs the runtime of the decorated function"""
    def decorator_timer(func):
        @wraps(func)
        def wrapper_timer(*args, **kwargs):
            logger = logging.getLogger(__name__)
            start_time = time.perf_counter()
            value = func(*args, **kwargs)
            end_time = time.perf_counter()
            run_time = end_time - start_time
            if name is not None:
                logger.info(f"{name} finished in {timedelta(seconds=run_time)}")
            else:
                logger.info(f"{func.__module__}.{func.__name__} finished in {timedelta(seconds=run_time)}")
            return value
        return wrapper_timer
    return decorator_timer


def log_call(func):
    """Decorator that logs the call args and return value of the decorated function"""
    @wraps(func)
    def wrapper_exceptions(*args, **kwargs):
        logger = logging.getLogger(__name__)
        value = func(*args, **kwargs)
        args = join_args(args)
        kwargs = join_kwargs(kwargs)
        logger.info(f"{func.__module__}.{func.__name__}> args: {args} | kwargs: {kwargs} > returned: {value}")
        return value
    return wrapper_exceptions
