from job_notifications.notifications import NotificationBase
from job_notifications.utils.handled_exception import HandledException

from job_notifications import handled_exception

import pytest


@pytest.fixture
def function_for_testing_exception_raised_by_code():
    @handled_exception((IndexError, ValueError))
    def func_test(x, y, cat=None, dog=None):
        # return 5
        raise ValueError
    return func_test


@pytest.fixture
def function_for_testing_exception_not_explicitly_raised_by_code():
    @handled_exception(KeyError)
    def func_test(key):
        d = {"red": 5}
        return d[key]
    return func_test


def test_exceptions_stack(function_for_testing_exception_raised_by_code):
    notifications = NotificationBase()
    function_for_testing_exception_raised_by_code(2, 'blue', dog="Maisy")
    stack = notifications.exception_stack()
    print(stack[0])
    # assert len(stack) == 1
    assert isinstance(stack[0], HandledException)


def test_exceptions_stack_two(function_for_testing_exception_not_explicitly_raised_by_code):
    notifications = NotificationBase()
    function_for_testing_exception_not_explicitly_raised_by_code('green')
    stack = notifications.exception_stack()
    print(stack[1])
    # assert len(stack) == 1
    assert isinstance(stack[0], HandledException)
