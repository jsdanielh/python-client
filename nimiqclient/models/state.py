from typing import TypeVar, Generic

__all__ = ["BlockchainState", "StateData"]


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

    @classmethod
    def deserialize(cls, data):
        params = set(inspect.signature(cls).parameters)
        return cls(**{key: value for key, value in data.items() if key in params}


T = TypeVar('T')


class StateData(Generic[T]):
    """
    Data returned by the RPC server that is valid for specific blockchain state
    and depends on the state the blockchain is at.

    :param metadata: State this data was obtained for/in.
    :type metadata: BlockchainState
    :param data: Data obtained.
    :type data: Generic[T]
    """

    def __init__(self, metadata: BlockchainState, data: T):
        self.metadata = metadata
        self.data = data

    @classmethod
    def deserialize(cls, data):
        params = set(inspect.signature(cls).parameters)
        return cls(**{key: value for key, value in data.items() if key in params}
