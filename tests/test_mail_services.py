from job_notifications import mail_services


def test_add():
    n = 8
    out = mail_services.add(n)
    assert out == 16
