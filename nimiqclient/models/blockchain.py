__all__ = ["BlockchainState"]


class BlockchainState:
    """
    Blockchain state returned by the server.
    This state allows to relate data with the state of the blockchain for
    which the data was fetched.

    :param blockNumber: Block number for which the data was fetched for.
    :type blockNumber: int
    :param hash: Block hash for which the data was fetched for.
    :type hash: str
    """

    def __init__(self, blockNumber: int, blockHash: str):
        self.blockNumber = blockNumber
        self.blockHash = blockHash
