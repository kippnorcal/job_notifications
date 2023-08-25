from job_notifications.notifications import Notifications
from job_notifications.utils.handled_exception import HandledException

from job_notifications import handled_exception

import pytest


@pytest.fixture
def function_for_testing():
    @handled_exception((IndexError, ValueError))
    def func_test(x, y, cat=None, dog=None):
        # return 5
        raise ValueError
    return func_test


# def test_handled_exception(function_for_testing):
#     result = function_for_testing()
#     assert result is None


def test_exceptions_stack(function_for_testing):
    notifications = Notifications('test')
    function_for_testing(2, 'blue', dog="Maisy")
    stack = notifications.exception_stack()
    print(stack[0])
    assert len(stack) == 1
    assert isinstance(stack[0], HandledException)
