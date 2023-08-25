from abc import ABC
from abc import abstractmethod
import os
from typing import Union, List

import requests

SERVICE_LOOKUP = {
    "MAILGUN": 'MailGunService',
    "GMAIL": 'GmailSMTPService'
}


class MailServiceBaseClass(ABC):
    """
    Interface for different mail services to implement.
    """

    def __init__(self, to_address: Union[None, str] = None, from_address: Union[None, str] = None, *args, **kwargs):
        self.to_address = to_address or os.getenv("TO_ADDRESS")
        self.from_address = from_address or os.getenv("FROM_ADDRESS")
        self.requests = requests

    def send_notification(self, message: str, subject: str,
                          attachments: Union[None, list] = None, *args, **kwargs):
        """Send email success/error notifications using Mailgun API."""
        self.email(self.to_address, self.from_address, subject, message, attachments=attachments)

    @abstractmethod
    def email(self,
              to_address: str,
              from_address: str,
              subject: Union[None, str] = None,
              body: Union[None, str] = None,
              attachments: Union[None, str] = None) -> None:
        """
        Sends an adhoc email.
        """
        raise Exception("Function must be implemented by sub class")


class MailGunService(MailServiceBaseClass):
    """

    """

    def __init__(self, to_address, from_address, *args, **kwargs):
        super().__init__(to_address, from_address)
        self.url = os.getenv("MG_URL") or kwargs.get("MG_URL") or kwargs.get("url")
        self.key = os.getenv("MG_KEY") or kwargs.get("MG_KEY") or kwargs.get("key")

    def email(self,
              to_address: str,
              from_address: str,
              subject: Union[None, str] = None,
              body: Union[None, str] = None,
              attachments: Union[None, str] = None) -> None:

        if attachments:
            attachments = self._attachments(attachments)

        self.requests.post(
            self.url,
            auth=("api", self.key),
            files=attachments,
            data={
                "from": from_address,
                "to": to_address,
                "subject": subject,
                "text": body,
            },
        )

    @staticmethod
    def _attachments(attachments: Union[str, list]) -> List[tuple]:
        attachments = [attachments] if isinstance(attachments, str) else attachments
        attachment_container = []
        for attachment in attachments:
            if os.path.exists(attachment):
                attachment_name = os.path.basename(attachment)
                with open(attachment, "rb") as file:
                    attachment_file = file.read()
                attachment_container.append(("attachment", (attachment_name, attachment_file)))
        return attachment_container


class GmailSMTPService(MailServiceBaseClass):

    def __init__(self, job_name, to_address, from_address, *args, **kwargs):
        super().__init__(job_name, to_address, from_address)
        self.user = os.getenv("GMAIL_USER") or kwargs["GMAIL_USER"] or kwargs["user"]
        self.pwd = os.getenv("GMAIL_PASS") or kwargs["GMAIL_PASS"] or kwargs["user"]

    def email(self):
        with self.server as s:
            s.login(self.user, self.password)
            msg = self._message()
            s.sendmail(self.user, self.to_address, msg)

    def _attachment(self):
        filename = "app.log"
        if os.path.exists(filename):
            with open(filename, "r") as attachment:
                log = MIMEText(attachment.read())
            log.add_header("Content-Disposition", f"attachment; filename= {filename}")
            msg.attach(log)


def create_mail_service(service: str,  *args, **kwargs) -> MailServiceBaseClass:
    try:
        service_obj = SERVICE_LOOKUP[service.upper()]
        return service_obj(args, kwargs)
    except KeyError:
        raise Exception("Unable to find service")
