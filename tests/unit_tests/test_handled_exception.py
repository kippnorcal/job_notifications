from contextlib import contextmanager

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


def test_handled_exception_catch_error():
    @handled_exception(KeyError)
    def to_be_decorated(num):
        if num == 1:
            raise KeyError
        else:
            return True
    result = to_be_decorated(1)
    assert result is not True


def test_handled_exception_re_raises_error():
    @handled_exception(KeyError, re_raise=True)
    def to_be_decorated():
        raise KeyError
    with pytest.raises(KeyError):
        to_be_decorated()


def test_handled_exception_re_raises_multiple_error_value_error():
    @handled_exception((KeyError, ValueError), re_raise=True)
    def to_be_decorated():
        raise ValueError
    with pytest.raises(ValueError):
        to_be_decorated()


def test_handled_exception_re_raises_multiple_error_key_error():
    @handled_exception((KeyError, ValueError), re_raise=True)
    def to_be_decorated():
        raise KeyError
    with pytest.raises(KeyError):
        to_be_decorated()


@pytest.mark.xfail(reason="Expecting that KeyError will not be raised")
def test_handled_exception_does_not_re_raises_error():
    @handled_exception((KeyError, ValueError), re_raise=[ValueError])
    def to_be_decorated():
        raise KeyError
    with pytest.raises(KeyError):
        to_be_decorated()


def test_handled_exception_re_raises_correct_error():
    @handled_exception((KeyError, ValueError), re_raise=[ValueError])
    def to_be_decorated():
        raise ValueError
    with pytest.raises(ValueError):
        to_be_decorated()


def test_handled_exception_return_none():
    @handled_exception(KeyError, return_none=True)
    def to_be_decorated():
        raise KeyError

    def here_is_the_test():
        d = to_be_decorated()
        return d

    result = here_is_the_test()
    assert result is None

