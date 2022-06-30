from .blockchain import BlockchainState

__all__ = ["Staker"]


class Staker:
    """
    Staker returned by the server

    :param address: Address of the staker.
    :type address: str
    :param balance: Balance of the staker.
    :type balance: int
    :param blockNumber: Block number from which this staker was fetch for.
    :type blockNumber: int
    :param blockHash: Block hash from which this staker was fetch for.
    :type blockHash: str
    """

    def __init__(self, address, balance, blockNumber, blockHash):
        self.address = address
        self.balance = balance
        self.blockchainState = BlockchainState(blockNumber, blockHash)
