from unittest.mock import Mock

from job_notifications.notifications import Notifications
from job_notifications.mail_services import MailGunService


import pytest

"""
exceptions stack
notify
    -subject generation
    -body generation
    -exceptions stack
simple email
add_log

"""


@pytest.fixture()
def notification_class():
    mock_service = Mock()
    notifications = Notifications("Test Job", mock_service)
    notifications._exception_stack = []
    return notifications


def test_exception_stack_empty(notification_class):
    notifications = notification_class
    assert len(notifications.exception_stack()) == 0


def test_add_exception_to_stack(notification_class):
    notifications = notification_class
    handled_exception = Mock()
    notifications.add_to_exception_stack(handled_exception)
    assert len(notifications.exception_stack()) == 1


@pytest.mark.skip("notification_class fixture doesn't get torn down; look into tearing down class attr")
def test_add_exception_to_stack_another_object(notification_class):
    notifications = notification_class
    mock_service = Mock()
    handled_exception = Mock()
    notifications_two = Notifications("Test Job 2", mock_service)
    notifications_two.add_to_exception_stack(handled_exception)
    assert len(notifications.exception_stack()) == 1


# body generation
def test_body_generation_error(notification_class):
    notifications = notification_class
    error_message = "Whoops! There was an error!"
    result = notifications._generate_notification_body(error_message)
    assert result == 'Test Job encountered an error: \n Whoops! There was an error!'


def test_body_generation_warnings(notification_class):
    notifications = notification_class
    handled_exception = Mock()
    notifications.add_to_exception_stack(handled_exception)
    result = notifications._generate_notification_body(None)
    assert result == 'Test Job completed with 1 exception(s) handled - see log(s) for details.'


def test_body_generation_success_with_logs(notification_class):
    mock_logs = Mock()
    notifications = notification_class
    notifications.add_log(mock_logs)
    result = notifications._generate_notification_body(None)
    assert result == 'Test Job completed successfully. See attached log(s) for details.'


def test_body_generation_success_no_logs(notification_class):
    notifications = notification_class
    result = notifications._generate_notification_body(None)
    assert result == 'Test Job completed successfully.'

# subject generation


def test_subject_failed(notification_class):
    notifications = notification_class
    error_message = "Whoops! There was an error!"
    result = notifications._generate_notification_subject(error_message)
    assert result == 'Test Job - Failed'


def test_subject_warnings(notification_class):
    notifications = notification_class
    handled_exception = Mock()
    notifications.add_to_exception_stack(handled_exception)
    result = notifications._generate_notification_subject(None)
    assert result == 'Test Job - Succeeded with Warnings'


def test_subject_success(notification_class):
    notifications = notification_class
    result = notifications._generate_notification_subject(None)
    assert result == 'Test Job - Success'


def test_notify():
    # Todo: Note that this is more of an integration test since it's
    #  involving data moving from the Notification object to the MaliGunService object
    mail_service = MailGunService("to@test.com", 'from@test.com', key=None, url=None)
    mail_service.send_notification = Mock()
    notifications = Notifications("Test Job", mail_service)
    notifications._generate_notification_subject = Mock().return_value('Test Subject')
    notifications._generate_notification_body = Mock().return_value('Test Body')
    notifications._create_notifications_exceptions_log = Mock().return_value('Cat')
    notifications.notify()
    print(mail_service.send_notification.call_count)
