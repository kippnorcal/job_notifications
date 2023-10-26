import os
from typing import Union, List

from job_notifications.utils.handled_exception import HandledException
from job_notifications.mail_services import MailServiceBaseClass


class NotificationBase:

    """
    This base class exists as a helper to the @handled_exception decorator. The decorator
    uses the add_to_exception_stack method to insert exceptions that it catches into the exception stack.
    The other methods related to the exception stack were included to group them together in one place.
    """

    _exception_stack: List[HandledException] = []

    def add_to_exception_stack(self, e: HandledException) -> None:
        self._exception_stack.append(e)

    def exception_stack(self) -> List[HandledException]:
        return self._exception_stack

    @property
    def exception_stack_empty(self):
        return len(self._exception_stack) == 0


class Notifications(NotificationBase):

    def __init__(self, job_name, mail_service: MailServiceBaseClass):
        self._job_name = job_name
        self._mail_service = mail_service
        self._logs = []

    def add_log(self, log: str) -> None:
        self._logs.append(log)

    def extend_job_name(self, name: str) -> None:
        self._job_name = self._job_name + " " + name

    def notify(self, error_message: Union[None, str] = None):
        """
        Sends out notification of job completion and the status.
        """

        subject = self._generate_notification_subject(error_message)
        message = self._generate_notification_body(error_message)
        self._eval_notifications_exceptions_log()
        self._mail_service.send_notification(message, subject, attachments=self._logs)

    def simple_email(self,
                     to_address: str,
                     from_address: str,
                     subject: str,
                     body: str,
                     cc: Union[None, str] = None,
                     bcc: Union[None, str] = None,
                     attachments: Union[None, List[str]] = None) -> None:
        self._mail_service.email(to_address, from_address, subject, body, cc, bcc, attachments)

    def _generate_notification_subject(self, error_message):
        if error_message:
            return f'{self._job_name} - Failed'
        elif not self.exception_stack_empty:
            return f'{self._job_name} - Succeeded with Warnings'
        else:
            return f'{self._job_name} - Success'

    def _generate_notification_body(self, error_message: Union[None, str]) -> str:

        if error_message:
            return f"{self._job_name} encountered an error: \n {error_message}"
        elif not self.exception_stack_empty:
            return f"{self._job_name} completed with {len(self._exception_stack)} " \
                   f"exception(s) handled - see log(s) for details."
        elif self._logs:
            return f"{self._job_name} completed successfully. See attached log(s) for details."
        else:
            return f"{self._job_name} completed successfully."

    def _eval_notifications_exceptions_log(self) -> None:
        if not self.exception_stack_empty:
            self._logs.append(self._create_notifications_exceptions_log())

    def _create_notifications_exceptions_log(self) -> str:
        log_file = os.getenv("EXCEPTIONS_LOG_FILE") or '/exceptions.log'
        with open(log_file, 'a') as exceptions_log:
            for exception in self._exception_stack:
                exceptions_log.write(f'{exception.to_log()}\n')
        return log_file
