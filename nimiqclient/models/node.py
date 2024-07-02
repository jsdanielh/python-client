from enum import Enum
from typing import TypeVar, Generic

__all__ = ["SyncStatus", "LogLevel"]


class SyncStatus:
    """
    Syncing status returned by the server.

    :param startingBlock: The block at which the import started (will only be
        reset, after the sync reached his head).
    :type startingBlock: int
    :param currentBlock: The current block, same as blockNumber.
    :type currentBlock: int
    :param highestBlock: The estimated highest block.
    :type highestBlock: int
    """

    def __init__(self, startingBlock, currentBlock, highestBlock):
        self.startingBlock = startingBlock
        self.currentBlock = currentBlock
        self.highestBlock = highestBlock

    @classmethod
    def deserialize(cls, data):
        params = set(inspect.signature(cls).parameters)
        return cls(**{key: value for key, value in data.items() if key in params}


class LogLevel(str, Enum):
    """
    Used to set the log level in the JSONRPC server.
    """

    TRACE = "trace"
    """Trace level log."""
    VERBOSE = "verbose"
    """Verbose level log."""
    DEBUG = "debug"
    """Debugging level log."""
    INFO = "info"
    """Info level log."""
    WARN = "warn"
    """Warning level log."""
    ERROR = "error"
    """Error level log."""
    ASSERT = "assert"
    """Assertions level log."""

    def __str__(self):
        return self.value
