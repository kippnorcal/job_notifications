import os
from typing import Union, List

from job_notifications.utils.decorators import HandledException
from job_notifications.mail_services import MailServiceBaseClass



class Notifications:

    _exception_stack: List[HandledException] = []

    def __init__(self, job_name, mail_service: MailServiceBaseClass,
                 logs: Union[None, str, list] = None):
        self._job_name = job_name
        self._mail_service = mail_service
        self._logs = list(logs) if isinstance(logs, str) else logs

    def add_log(self, log: str) -> None:
        if self._logs is None:
            self._logs = [log]
        else:
            self._logs.append(log)

    def add_to_exception_stack(self, e: HandledException) -> None:
        self._exception_stack.append(e)

    def exception_stack(self) -> list:
        return self._exception_stack

    @property
    def exception_stack_empty(self):
        return len(self._exception_stack) == 0

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
                     subject: Union[None, str] = None,
                     body: Union[None, str] = None,
                     attachments: Union[None, str] = None) -> None:
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
        if self._exception_stack:
            self._logs.append(self._create_notifications_exceptions_log())

    def _create_notifications_exceptions_log(self) -> str:
        log_file = os.getenv("EXCEPTIONS_LOG_FILE") or '/exceptions.log'
        with open(log_file, 'w') as exceptions_log:
            for exception in self._exception_stack:
                exceptions_log.write(exception.to_log())
        return log_file

