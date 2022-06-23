__all__ = ["Inherent"]


class Inherent:
    """
    Inherent returned by the server

    :param type: Type of the inherent.
    :type type: int
    :param blockNumber: Block number of the inherent.
    :type blockNumber: int
    :param timestamp: Timestamp of the inherent.
    :type timestamp: int
    :param target: Target address of the inherent.
    :type target: str
    :param value: Value or amount of the inherent.
    :type value: str
    :param data: Data of the inherent.
    :type data: str
    :param hash: Hash of the inherent.
    :type hash: str
    """

    def __init__(self, type, blockNumber, timestamp, target, value, data,
                 hash):
        self.type = type
        self.blockNumber = blockNumber
        self.timestamp = timestamp
        self.target = target
        self.value = value
        self.data = data
        self.hash = hash
