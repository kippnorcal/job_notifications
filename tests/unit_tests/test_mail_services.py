import os

from job_notifications.mail_services import MailGunService

from unittest.mock import patch, mock_open, Mock

import pytest


def test_eval_status():
    return MailGunService(
        job_name='Test',
        to_address='test@test.com',
        from_address='testbot@testbot.com',
        url='http://none.org',
        key='8675309'
    )


def test_notification_subject():
    pass


def test_body():
    pass


@pytest.fixture
def mail_gun_setup_init_kwargs():
    service = MailGunService(
        job_name='Test',
        to_address='test@test.com',
        from_address='testbot@testbot.com',
        url='http://none.org',
        key='8675309'
    )
    return service


def test_mail_gun_init_kwargs(mail_gun_setup_init_kwargs):
    service = mail_gun_setup_init_kwargs
    assert service.url == 'http://none.org'
    assert service.key == '8675309'


@pytest.fixture
def mail_gun_setup_init_env(monkeypatch):
    monkeypatch.setenv("MG_URL", 'http://none.org')
    monkeypatch.setenv("MG_KEY", '8675309')
    service = MailGunService(
        job_name='Test',
        to_address='test@test.com',
        from_address='testbot@testbot.com',
    )
    return service


def test_mail_gun_init_env(mail_gun_setup_init_env):
    service = mail_gun_setup_init_env
    assert service.url == 'http://none.org'
    assert service.key == '8675309'


@patch('builtins.open', new_callable=mock_open, read_data='1')
def test_mail_gun_attachments(x):
    os_mock = Mock()
    os.path.exists = os_mock.return_value(True)
    service = MailGunService(
        job_name='Test',
        to_address='test@test.com',
        from_address='testbot@testbot.com',
        url='http://none.org',
        key='8675309'
    )
    test = service._attachments(['app.log'])
    assert test == [('attachment', ('app.log', '1'))]


@patch('builtins.open', new_callable=mock_open, read_data='1')
def test_mail_gun_attachments_multiple(x):
    os_mock = Mock()
    os.path.exists = os_mock.return_value(True)
    service = MailGunService(
        job_name='Test',
        to_address='test@test.com',
        from_address='testbot@testbot.com',
        url='http://none.org',
        key='8675309'
    )
    test = service._attachments(['app.log', 'test/some.log', 'foo/bar/test.log'])
    assert test == [
        ('attachment', ('app.log', '1')),
        ('attachment', ('some.log', '1')),
        ('attachment', ('test.log', '1'))
    ]
