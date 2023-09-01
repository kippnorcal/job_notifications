import os

from job_notifications.mail_services import GmailSMTPService, MailGunService, create_mail_service
from job_notifications.utils.exceptions import MailServiceNotFound

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


def test_mail_service_creation_with_args_mailgun():
    creation_args = {
        "from_address": "test@from.address",
        "to_address": "test@to.address",
        "MG_URL": "http://some.url",
        "MG_DOMAIN": "foo.bar/v1",
        "MG_KEY": '123key'
    }
    result = create_mail_service('MailGun', **creation_args)
    assert isinstance(result, MailGunService)
    assert result.to_address == "test@to.address"
    assert result.from_address == "test@from.address"
    assert result.url == 'http://some.url'
    assert result.key == "123key"
    assert result.domain == "foo.bar/v1"


def test_mail_service_creation_with_env_vars_mailgun(monkeypatch):
    monkeypatch.setenv("TO_ADDRESS", "test@to.address")
    monkeypatch.setenv("FROM_ADDRESS", "test@from.address")
    monkeypatch.setenv("MG_URL", "http://some.url")
    monkeypatch.setenv("MG_DOMAIN", "foo.bar/v1")
    monkeypatch.setenv("MG_KEY", "123key")

    result = create_mail_service('MailGun')
    assert isinstance(result, MailGunService)
    assert result.to_address == "test@to.address"
    assert result.from_address == "test@from.address"
    assert result.url == 'http://some.url'
    assert result.key == "123key"
    assert result.domain == "foo.bar/v1"


def test_mail_service_creation_with_general_args_mailgun():
    creation_args = {
        "from_address": "test@from.address",
        "to_address": "test@to.address",
        "url": "http://some.url",
        "domain": "foo.bar/v1",
        "key": '123key'
    }
    result = create_mail_service('MailGun', **creation_args)
    assert isinstance(result, MailGunService)
    assert result.to_address == "test@to.address"
    assert result.from_address == "test@from.address"
    assert result.url == 'http://some.url'
    assert result.key == "123key"
    assert result.domain == "foo.bar/v1"


def test_mail_service_creation_with_args_gmail():
    creation_args = {
        "from_address": "test@from.address",
        "to_address": "test@to.address",
        "GMAIL_USER": "test@from.address",
        "GMAIL_PASS": '123key'
    }
    result = create_mail_service('gmail', **creation_args)
    assert isinstance(result, GmailSMTPService)
    assert result.to_address == "test@to.address"
    assert result.from_address == "test@from.address"
    assert result.user == "test@from.address"
    assert result.pwd == "123key"


def test_mail_service_creation_with_env_vars_gmail(monkeypatch):
    monkeypatch.setenv("TO_ADDRESS", "test@to.address")
    monkeypatch.setenv("FROM_ADDRESS", "test@from.address")
    monkeypatch.setenv("GMAIL_USER", "test@from.address")
    monkeypatch.setenv("GMAIL_PASS", "123key")

    result = create_mail_service('gmail')
    assert isinstance(result, GmailSMTPService)
    assert result.to_address == "test@to.address"
    assert result.from_address == "test@from.address"
    assert result.user == "test@from.address"
    assert result.pwd == "123key"


def test_mail_service_creation_with_general_args_gmail():
    creation_args = {
        "from_address": "test@from.address",
        "to_address": "test@to.address",
        "user": "test@from.address",
        "pass": '123key'
    }
    result = create_mail_service('gmail', **creation_args)
    assert isinstance(result, GmailSMTPService)
    assert result.to_address == "test@to.address"
    assert result.from_address == "test@from.address"
    assert result.user == "test@from.address"
    assert result.pwd == "123key"


def test_mail_service_creation_raise_exception():
    with pytest.raises(MailServiceNotFound):
        create_mail_service("FooBar")
