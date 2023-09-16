
class MailServiceNotFound(Exception):
    """
    Raised when a service called in create_notifications cannot be found in SERVICE_REGISTRY
    """
    # Todo: Is it possible to create a custom error message here that lists the services
    pass


class MissingRequests(Exception):
    """
    MailGun requires the requests package. Any repo that uses MailGun also needs to install requests.
    """
    pass
