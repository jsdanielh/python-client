__all__ = ["InternalErrorException", "RemoteErrorException"]


class InternalErrorException(Exception):
    """
    Internal error during a JSON RPC request.
    """

    pass


class RemoteErrorException(Exception):
    """
    Exception on the remote server.
    """

    def __init__(self, message, code):
        super(RemoteErrorException, self).__init__(
            "{0} ({1})".format(message, code))
