from abc import ABC
from abc import abstractmethod
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import smtplib
import ssl
from typing import Union, List, Tuple

import requests  # type: ignore

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
                          attachments: Union[None, List[str]] = None, *args, **kwargs) -> None:
        """Send email success/error notifications using Mailgun API."""
        self.email(self.to_address, self.from_address, subject, message, attachments=attachments)  # type: ignore

    @abstractmethod
    def email(self,
              to_address: str,
              from_address: str,
              subject: str,
              body: str,
              attachments: Union[None, List[str]] = None) -> None:
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
              subject: str,
              body: str,
              attachments: Union[None, List[str]] = None) -> None:

        if attachments is not None:
            attachments = self._attachments(attachments)  # type: ignore

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
    def _attachments(attachments: List[str]) -> List[Tuple[str, Tuple[str, bytes]]]:
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

    def email(self,
              to_address: str,
              from_address: str,
              subject: str,
              body: str,
              attachments: Union[None, List[str]] = None) -> None:

        context = ssl.create_default_context()
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context)
        with server as s:
            email_contents = MIMEMultipart()
            email_contents["Subject"] = subject
            email_contents["From"] = self.user
            email_contents["To"] = to_address
            email_contents.attach(MIMEText(body, "plain"))
            if attachments is not None:
                self._attachments(email_contents, attachments)
            s.login(self.user, self.pwd)
            s.sendmail(self.user, to_address, email_contents.as_string())

    @staticmethod
    def _attachments(message: MIMEMultipart, attachments: List[str]) -> None:
        """Attaches logs to email by converting log files to MIMEText object and attaching to MIMEMultipart object"""
        for attachment in attachments:
            if os.path.exists(attachment):
                attachment_name = os.path.basename(attachment)
                with open(attachment, "r") as file:
                    log = MIMEText(file.read())
                log.add_header("Content-Disposition", f"attachment; filename= {attachment_name}")
                message.attach(log)


def create_mail_service(service: str,  *args, **kwargs) -> MailServiceBaseClass:
    try:
        service_obj = SERVICE_LOOKUP[service.upper()]
        return service_obj(args, kwargs)  # type: ignore
    except KeyError:
        raise Exception("Unable to find service")
