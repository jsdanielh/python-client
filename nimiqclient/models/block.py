__all__ = ["Block", "BlockType",
           "MicroBlock", "MacroBlock"]

from .transaction import Transaction


class BlockType:
    """
    Type of a Nimiq account.
    """

    MicroBlock = "micro"
    """Micro block"""
    MacroBlock = "macro"
    """Macro block"""


class Block:
    """
    Block returned by the server.

    :param number: Height of the block.
    :type number: int
    :param batch: Batch number of the block.
    :type number: int
    :param type: The block type associated with the block.
    :type type: BlockType
    :param bodyHash: Hash of the block body.
    :type bodyHash: str
    :param epoch: Epoch number of the block.
    :type epoch: int
    :param extraData: Extra data of the block.
    :type extraData: str
    :param hash: Hash of the block.
    :type hash: str
    :param parentHash: Hash of the parent of the block.
    :type parentHash: str
    :param size: Size of the block
    :type size: int
    :param version: Version of the block
    :type version: int
    :param view: View number of the block.
    :type view: int
    :param timestamp: Timestamp of the block.
    :type timestamp: int
    :param seed: Seeds for the block.
    :type seed: BlockSeed
    :param stateHash: Hash of the state of the block.
    :type stateHash: str
    :param historyHash: Hash of the history of the block.
    :type historyHash: str
    """

    def __init__(self, number, batch, type, bodyHash, epoch, extraData, hash, parentHash, size, version, view, timestamp, seed, stateHash, historyHash):
        self.number = number
        self.batch = batch
        self.type = type
        self.bodyHash = bodyHash
        self.epoch = epoch
        self.extraData = extraData
        self.hash = hash
        self.parentHash = parentHash
        self.size = size
        self.version = version
        self.view = view
        self.timestamp = timestamp
        self.seed = seed
        self.stateHash = stateHash
        self.historyHash = historyHash


class MicroBlock(Block):
    """
    Block returned by the server.

    :param number: Height of the block.
    :type number: int
    :param batch: Batch number of the block.
    :type batch: int
    :param type: The BlockType associated with the block.
    :type type: BlockType
    :param bodyHash: Hash of the body of the block.
    :type bodyHash: str
    :param epoch: Epoch number of the block.
    :type epoch: int
    :param extraData: Extra data of the block.
    :type extraData: str
    :param hash: Hash of the block.
    :type hash: str
    :param parentHash: Hash of the parent of the block.
    :type parentHash: str
    :param size: Size of the block
    :type size: int
    :param version: Version of the block
    :type version: int
    :param view: View number of the block.
    :type view: int
    :param timestamp: Timestamp of the block.
    :type timestamp: int
    :param producer: Producer of the block.
    :type producer: BlockProducer
    :param seed: Seeds for the block.
    :type seed: BlockSeed
    :param stateHash: Hash of the state of the block.
    :type stateHash: str
    :param historyHash: Hash of the history of the block.
    :type historyHash: str
    :param forkProof: Fork proof of the block.
    :type forkProof: dict
    :param justification: Justification of the block
    :type justification: BlockJustification
    :param transactions: List of transactions. Either represented by the transaction hash or a Transaction object.
    :type transactions: list of(Transaction or str)
    """

    def __init__(
        self,
        number,
        batch,
        type,
        bodyHash,
        epoch,
        extraData,
        hash,
        parentHash,
        size,
        version,
        view,
        timestamp,
        producer,
        stateHash,
        historyHash,
        seed,
        forkProofs=None,
        justification=None,
        transactions=[],
    ):
        super(MicroBlock, self).__init__(number, batch, type,
                                         bodyHash, epoch, extraData, hash, parentHash, size, version, view, timestamp, seed, stateHash, historyHash)
        self.producer = producer
        self.forkProofs = forkProofs
        self.justification = justification
        for index, transaction in enumerate(transactions):
            tt = type(transaction)
            if tt is not str and tt is not Transaction:
                if tt is dict:
                    transactions[index] = Transaction(**transaction)
                else:
                    from ..nimiq_client import InternalErrorException

                    raise InternalErrorException(
                        "Couldn't parse Transaction {0}".format(transaction)
                    )
        self.transactions = transactions


class MacroBlock(Block):
    """
    Block returned by the server.

    :param number: Height of the block.
    :type number: int
    :param batch: Batch number of the block.
    :type batch: int
    :param type: The BlockType associated with the block.
    :type type: BlockType
    :param bodyHash: Hash of the body of the block.
    :type bodyHash: str
    :param epoch: Epoch number of the block.
    :type epoch: int
    :param extraData: Extra data of the block.
    :type extraData: str
    :param hash: Hash of the block.
    :type hash: str
    :param parentHash: Hash of the parent of the block.
    :type parentHash: str
    :param size: Size of the block
    :type size: int
    :param version: Version of the block
    :type version: int
    :param view: View number of the block.
    :type view: int
    :param timestamp: Timestamp of the block.
    :type timestamp: int
    :param seed: Seeds for the block.
    :type seed: BlockSeed
    :param stateHash: Hash of the state of the block.
    :type stateHash: str
    :param historyHash: Hash of the history of the block.
    :type historyHash: str
    :param isElectionBlock: Indicates whether the block is an election macro block.
    :type isElectionBlock: bool
    :param parentElectionHash: Parent election hash of the macro block.
    :type parentElectionHash: str
    :param slots: Slots for the block
    :type slots: list
    :param lostRewardSet: Set of lost rewards of the block.
    :type lostRewardSet: list
    :param disabledRewardSet: Set of disabled rewards of the block.
    :type disabledRewardSet: list
    :param justification: Justification of the block
    :type justification: BlockJustification
    :param transactions: List of transactions. Either represented by the transaction hash or a Transaction object.
    :type transactions: list of(Transaction or str)
    """

    def __init__(
        self,
        number,
        batch,
        type,
        bodyHash,
        epoch,
        extraData,
        hash,
        parentHash,
        size,
        version,
        view,
        timestamp,
        seed,
        stateHash,
        historyHash,
        isElectionBlock,
        parentElectionHash,
        slots=None,
        lostRewardSet=None,
        disabledSet=None,
        justification=None,
        transactions=[],
    ):
        super(MacroBlock, self).__init__(number, batch, type,
                                         bodyHash, epoch, extraData, hash, parentHash, size, version, view, timestamp, seed, stateHash, historyHash)
        self.isElectionBlock = isElectionBlock
        self.parentElectionHash = parentElectionHash
        self.slots = slots
        self.lostRewardSet = lostRewardSet
        self.disabledSet = disabledSet
        self.justification = justification
        for index, transaction in enumerate(transactions):
            tt = type(transaction)
            if tt is not str and tt is not Transaction:
                if tt is dict:
                    transactions[index] = Transaction(**transaction)
                else:
                    from ..nimiq_client import InternalErrorException

                    raise InternalErrorException(
                        "Couldn't parse Transaction {0}".format(transaction)
                    )
        self.transactions = transactions
