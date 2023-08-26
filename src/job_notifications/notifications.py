import os
from typing import Union, List

from job_notifications.utils.handled_exception import HandledException
from job_notifications.mail_services import MailServiceBaseClass


class NotificationBase:

    """
    This base class exists as a helper to the @handled_exception decorator. The decorator
    uses the add_to_exception_stack method to insert exceptions that it catches into the exception stack.
    The other exception stack methods were included because it felt appropriate to group them together.
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

    def __init__(self, job_name, mail_service: MailServiceBaseClass,
                 logs: Union[None, List[str]] = None):
        self._job_name = job_name
        self._mail_service = mail_service
        self._logs = logs if logs is not None else []

    def add_log(self, log: str) -> None:
        self._logs.append(log)

    def notify(self, error_message: Union[None, str] = None):
        """
        Sends out notification of job completion and the status.
        :return:
        """

        subject = self._generate_notification_subject(error_message)
        message = self._generate_notification_body(error_message)
        self._create_notifications_exceptions_log()
        self._mail_service.send_notification(message, subject, attachments=self._logs)

    def simple_email(self,
                     to_address: str,
                     from_address: str,
                     subject: str,
                     body: str,
                     attachments: Union[None, List[str]] = None) -> None:
        """

        :return:
        """
        self._mail_service.email(to_address, from_address, subject, body, attachments)

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
                   f"exceptions handled - see logs for details."
        elif self._logs:
            return f"{self._job_name} completed successfully. See attached logs for details."
        else:
            return f"{self._job_name} completed successfully."

    def _eval_notifications_exceptions_log(self) -> None:
        if not self.exception_stack_empty:
            self._logs.append(self._create_notifications_exceptions_log())

    def _create_notifications_exceptions_log(self) -> str:
        log_file = os.getenv("EXCEPTIONS_LOG_FILE") or '/exceptions.log'
        with open(log_file, 'w') as exceptions_log:
            for exception in self._exception_stack:
                exceptions_log.write(exception.to_log())
        return log_file
