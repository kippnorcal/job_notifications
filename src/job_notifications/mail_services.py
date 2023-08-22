from abc import ABC
from abc import abstractmethod


class MailServiceBaseClass(ABC):
    """
    Interface for different mail services to implement.
    """

    @abstractmethod
    def send_notification(self):
        """
        Sends job notification upon completion
        """
        raise Exception("Function must be implemented by sub class")

    @abstractmethod
    def email(self):
        """
        Sends an adhoc email.
        """
        raise Exception("Function must be implemented by sub class")


class MailGunService(MailServiceBaseClass):
    """

    """

    def __init__(self):
        pass

    def send_notification(self):
        pass


class SMTPService(MailServiceBaseClass):

    def __init__(self):
        pass

    def send_notification(self):
        pass
