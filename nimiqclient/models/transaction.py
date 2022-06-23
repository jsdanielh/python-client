from .account import AccountType
import json

__all__ = ["Transaction"]


class Transaction:
    """
    Transaction returned by the server.

    :param hash: Hex-encoded hash of the transaction.
    :type hash: str
    :param blockHash: Hex-encoded hash of the block containing the
        transaction.
    :type blockHash: str, optional
    :param blockNumber: Height of the block containing the transaction.
    :type blockNumber: int, optional
    :param timestamp: UNIX timestamp of the block containing the transaction.
    :type timestamp: int, optional
    :param confirmations: Number of confirmations of the block containing the
        transaction.
    :type confirmations: int, optional
    :param transactionIndex: Index of the transaction in the block.
    :type transactionIndex: int, optional
    :param from_: Hex-encoded address of the sending account.
    :type from_: str
    :param fromAddress: Nimiq user friendly address (NQ-address) of the
        sending account.
    :type fromAddress: str
    :param to: Hex-encoded address of the recipient account.
    :type to: str
    :param toAddress: Nimiq user friendly address (NQ-address) of the
        recipient account.
    :type toAddress: str
    :param value: Integer of the value (in smallest unit) sent with this
        transaction.
    :type value: int
    :param fee: Integer of the fee (in smallest unit) for this transaction.
    :type fee: int
    :param data: Hex-encoded contract parameters or a message.
    :type data: str, optional
    :param flags: Bit-encoded transaction flags.
    :type flags: int
    :param valid: Is valid transaction.
    :type valid: bool, optional
    :param inMempool: Transaction is in mempool.
    :type inMempool: bool, optional
    """

    def __init__(
        self,
        hash,
        from_,
        fromAddress,
        to,
        toAddress,
        value,
        fee,
        flags,
        blockHash=None,
        blockNumber=None,
        timestamp=None,
        confirmations=0,
        transactionIndex=None,
        data=None,
        valid=None,
        inMempool=None,
    ):
        self.hash = hash
        self.blockHash = blockHash
        self.blockNumber = blockNumber
        self.timestamp = timestamp
        self.confirmations = confirmations
        self.transactionIndex = transactionIndex
        self.from_ = from_
        self.fromAddress = fromAddress
        self.to = to
        self.toAddress = toAddress
        self.value = value
        self.fee = fee
        self.data = data
        self.flags = flags
        self.valid = valid
        self.inMempool = inMempool
