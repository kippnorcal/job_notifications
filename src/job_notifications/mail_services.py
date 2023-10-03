from abc import ABC
from abc import abstractmethod
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import smtplib
import ssl
from typing import Union, List, Tuple

from job_notifications.utils.exceptions import MailServiceNotFound, MissingRequests


class MailServiceBaseClass(ABC):
    """
    Base class that provides an interface for mail services to implement.
    """

    def __init__(self, to_address: Union[None, str] = None, from_address: Union[None, str] = None, *args, **kwargs):
        self.to_address = os.getenv("TO_ADDRESS") or to_address
        self.from_address = os.getenv("FROM_ADDRESS") or from_address

    def send_notification(self, message: str, subject: str,
                          attachments: Union[None, List[str]] = None, *args, **kwargs) -> None:
        """Send email success/error notifications using Mailgun API."""
        if self.to_address or self.from_address or subject or message is not None:
            self.email(self.to_address, self.from_address, subject, message, attachments=attachments)
        else:
            raise Exception("Unable to send notification. To Address, From Address, Subject, or Message is None")

    @abstractmethod
    def email(self,
              to_address: str,
              from_address: str,
              subject: str,
              body: str,
              cc: Union[None, str] = None,
              bcc: Union[None, str] = None,
              attachments: Union[None, List[str]] = None) -> None:
        """
        Sends an adhoc email.
        """
        raise Exception("Function must be implemented by sub class")


class MailGunService(MailServiceBaseClass):
    """
    Class for sending emails through the MailGun API
    """

    def __init__(self, to_address: Union[None, str] = None, from_address: Union[None, str] = None, *args, **kwargs):
        super().__init__(to_address, from_address)
        self.url = os.getenv("MG_API_URL") or kwargs.get("MG_API_URL") or kwargs.get("url")
        self.domain = os.getenv("MG_DOMAIN") or kwargs.get("MG_DOMAIN") or kwargs.get("domain")
        self.key = os.getenv("MG_API_KEY") or kwargs.get("MG_API_KEY") or kwargs.get("key")

    def email(self,
              to_address: str,
              from_address: str,
              subject: str,
              body: str,
              cc: Union[None, str] = None,
              bcc: Union[None, str] = None,
              attachments: Union[None, List[str]] = None) -> None:

        try:
            import requests
        except ModuleNotFoundError:
            raise MissingRequests("Check that the requests package is installed; Needed for using MailGun")

        if attachments is not None:
            attachments = self._attachments(attachments)  # type: ignore

        requests.post(
            f"{self.url}{self.domain}/messages",
            auth=("api", self.key),
            files=attachments,
            data={
                "from": from_address,
                "to": to_address,
                "subject": subject,
                "text": body,
                "cc": cc,
                "bcc": bcc,
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
    """
    Class for sending emails through Google's SMTP server
    """

    def __init__(self, to_address: Union[None, str] = None, from_address: Union[None, str] = None, *args, **kwargs):
        super().__init__(to_address, from_address)
        self.user = os.getenv("GMAIL_USER") or kwargs.get("GMAIL_USER") or kwargs.get("user")
        self.pwd = os.getenv("GMAIL_PASS") or kwargs.get("GMAIL_PASS") or kwargs.get("pass")

    def email(self,
              to_address: str,
              from_address: str,
              subject: str,
              body: str,
              cc: Union[None, str] = None,
              bcc: Union[None, str] = None,
              attachments: Union[None, List[str]] = None) -> None:

        context = ssl.create_default_context()
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context)
        with server as s:
            email_contents = MIMEMultipart()
            email_contents["Subject"] = subject
            email_contents["From"] = self.user
            email_contents["To"] = to_address
            email_contents["CC"] = cc
            email_contents["BCC"] = bcc
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
    """
    Finds service in SERVICE_REGISTRY and returns a subclass instance of MailServiceBaseClass
    """
    try:
        service_obj = SERVICE_REGISTRY[service.upper()]
        return service_obj(*args, **kwargs)
    except KeyError:
        raise MailServiceNotFound(f"Unable to fetch mail service. {service} is an unknown service")


"""The below registry is used to lookup the mail service that is called through the create_notifications entrypoint"""
SERVICE_REGISTRY = {
    "MAILGUN": MailGunService,
    "GMAIL": GmailSMTPService
}
