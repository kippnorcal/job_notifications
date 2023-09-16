from time import sleep

from job_notifications import timer
import pytest


@pytest.fixture
def function_for_testing_timer():
    @timer("Test Timer")
    def func_test():
        sleep(10)
    return func_test


def test_timer(function_for_testing_timer):
    f = function_for_testing_timer()
