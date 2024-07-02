from .log import Log

__all__ = ["TransactionLog"]


class TransactionLog:
    """
    Transaction log returned by the server.

    :param hash: Transaction hash associated with the transaction log.
    :type hash: str
    :param logs: List of logs associated with the transaction log.
    :type logs: List of (Log)
    """

    def __init__(self, hash, logs):
        self.type = type
        self.hash = hash
        log_objs = []
        for log in logs:
            tt = type(log)
            if tt is not str and tt is not Log:
                if tt is dict:
                    log_objs.append(Log.get_log(log))
                else:
                    from ..nimiq_client import InternalErrorException

                    raise InternalErrorException(
                        "Couldn't parse Transaction {0}".format(log)
                    )
        self.logs = log_objs

    @classmethod
    def deserialize(cls, data):
        params = set(inspect.signature(cls).parameters)
        return cls(**{key: value for key, value in data.items() if key in params}
