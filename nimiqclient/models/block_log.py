from .log import Log
from .transaction_log import TransactionLog

__all__ = ["AppliedBlockLog", "BlockLog", "BlockLogType", "RevertedBlockLog"]


class BlockLogType:
    """
    Type of a Nimiq block log.
    """

    APPLIED = 'applied-block'
    """Applied block log."""
    REVERTED = 'reverted-block'
    """Reverted block log."""


class BlockLog:
    """
    Block log returned by the server.

    :param type: The block log type associated with the block log.
    :type type: BlockLogType
    :param inherents: Inherent logs associated with the block log.
    :type inherents: List of (str)
    :param transactions: Transaction logs associated with the block log.
    :type transactions: Lost of (str)
    """

    def __init__(self, type_, inherents, transactions):
        self.type = type_

        # Build the Log objects for inherentLogs
        log_objs = []
        for log in inherents:
            tt = type(log)
            if tt is not str and tt is not Log:
                if tt is dict:
                    log_objs.append(Log.get_log(log))
                else:
                    from ..nimiq_client import InternalErrorException

                    raise InternalErrorException(
                        "Couldn't parse Transaction {0}".format(log)
                    )
        self.inherentLogs = log_objs

        # Build the TransactionLog objects for inherentLogs
        tx_log_objs = []
        for log in transactions:
            tt = type(log)
            if tt is not str and tt is not TransactionLog:
                if tt is dict:
                    tx_log_objs.append(TransactionLog(**log))
                else:
                    from ..nimiq_client import InternalErrorException

                    raise InternalErrorException(
                        "Couldn't parse Transaction {0}".format(log)
                    )
        self.txLogs = tx_log_objs

    @staticmethod
    def get_block_log(data):
        """
        Get the specific block log type from the dictionary data.

        :param data: The dictionary containing the data.
        :type data: dict
        :return: BlockLog object.
        :rtype: BlockLog or AppliedBlockLog or RevertedBlockLog
        """
        type = data.get("type")
        if type == BlockLogType.APPLIED:
            return AppliedBlockLog(**data)
        elif type == BlockLogType.REVERTED:
            return RevertedBlockLog(**data)
        else:
            return BlockLog(**data)


class AppliedBlockLog(BlockLog):
    """
    Applied block log returned by the server.

    :param type: The block log type associated with the block log.
    :type type: BlockLogType
    :param inherents: Inherent logs associated with the block log.
    :type inherents: List of (str)
    :param timestamp: Timestamp associated with the block log.
    :type timestamp: str
    :param transactions: Transaction logs associated with the block log.
    :type transactions: Lost of (str)
    """

    def __init__(self, type, inherents, timestamp, transactions):
        super(AppliedBlockLog, self).__init__(
            type, inherents, transactions)
        self.timestamp = timestamp


class RevertedBlockLog(BlockLog):
    """
    Reverted block log returned by the server.

    :param type: The block log type associated with the block log.
    :type type: BlockLogType
    :param inherents: Inherent logs associated with the block log.
    :type inherents: List of (str)
    :param timestamp: Timestamp associated with the block log.
    :type timestamp: str
    :param transactions: Transaction logs associated with the block log.
    :type transactions: Lost of (str)
    """

    def __init__(self, type, inherents, transactions):
        super(RevertedBlockLog, self).__init__(
            type, inherents, transactions)
