from .transaction import Transaction


__all__ = ["Block", "BlockType", "ForkProof", "MicroBlock", "MacroBlock",
           "Slot", "SlashedSlots"]


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
    :type batch: int
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
    :param network: Network ID of the block
    :type network: int
    :param timestamp: Timestamp of the block.
    :type timestamp: int
    :param seed: Seeds for the block.
    :type seed: BlockSeed
    :param stateHash: Hash of the state of the block.
    :type stateHash: str
    :param historyHash: Hash of the history of the block.
    :type historyHash: str
    """

    def __init__(self, number, batch, type, bodyHash, epoch, extraData, hash,
                 parentHash, size, version, network, timestamp, seed,
                 stateHash, historyHash):
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
        self.network = network
        self.timestamp = timestamp
        self.seed = seed
        self.stateHash = stateHash
        self.historyHash = historyHash

    @classmethod
    def deserialize(cls, data):
        params = set(inspect.signature(cls).parameters)
        return cls(**{key: value for key, value in data.items() if key in params}

    @staticmethod
    def get_block(data):
        """
        Get the specific block type from the dictionary data.

        :param data: The dictionary containing the data.
        :type data: dict
        :return: Block object.
        :rtype: Block or MicroBlock or MacroBlock
        """
        type = data.get("type")
        if type == BlockType.MicroBlock:
            return MicroBlock.deserialize(data)
        elif type == BlockType.MacroBlock:
            return MacroBlock.deserialize(data)
        else:
            return Block.deserialize(data)


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
    :param network: Network ID of the block
    :type network: int
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
    :param equivocationProofs: Equivocation proofs of the block
    :type equivocationProofs: List of EquivocationProof
    :param transactions: List of transactions. Either represented by the
        transaction hash or a Transaction object.
    :type transactions: list of (Transaction or str)
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
        network,
        timestamp,
        producer,
        stateHash,
        historyHash,
        seed,
        forkProofs=None,
        justification=None,
        equivocationProofs=None,
        transactions=[],
    ):
        super(MicroBlock, self).__init__(number, batch, type, bodyHash, epoch,
                                         extraData, hash, parentHash, size,
                                         version, network, timestamp, seed,
                                         stateHash, historyHash)
        self.producer = producer
        self.forkProofs = forkProofs
        self.justification = justification
        self.equivocationProofs = equivocationProofs
        for index, transaction in enumerate(transactions):
            tt = type(transaction)
            if tt is not str and tt is not Transaction:
                if tt is dict:
                    transactions[index] = Transaction.deserialize(transaction)
                else:
                    from ..nimiq_client import InternalErrorException

                    raise InternalErrorException(
                        "Couldn't parse Transaction {0}".format(transaction)
                    )
        self.transactions = transactions

    @classmethod
    def deserialize(cls, data):
        params = set(inspect.signature(cls).parameters)
        return cls(**{key: value for key, value in data.items() if key in params}

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
    :param network: Network ID of the block
    :type network: int
    :param timestamp: Timestamp of the block.
    :type timestamp: int
    :param seed: Seeds for the block.
    :type seed: BlockSeed
    :param stateHash: Hash of the state of the block.
    :type stateHash: str
    :param historyHash: Hash of the history of the block.
    :type historyHash: str
    :param isElectionBlock: Indicates whether the block is an election macro
        block.
    :type isElectionBlock: bool
    :param parentElectionHash: Parent election hash of the macro block.
    :type parentElectionHash: str
    :param interlink: The block interlink.
    :type interlink: str
    :param slots: Slots for the block
    :type slots: list
    :param lostRewardSet: Set of lost rewards of the block.
    :type lostRewardSet: list
    :param disabledRewardSet: Set of disabled rewards of the block.
    :type disabledRewardSet: list
    :param justification: Justification of the block
    :type justification: BlockJustification
    :param transactions: List of transactions. Either represented by the
        transaction hash or a Transaction object.
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
        network,
        timestamp,
        seed,
        stateHash,
        historyHash,
        isElectionBlock,
        parentElectionHash,
        interlink,
        slots=None,
        lostRewardSet=None,
        disabledSet=None,
        justification=None,
        transactions=[],
    ):
        super(MacroBlock, self).__init__(number, batch, type, bodyHash, epoch,
                                         extraData, hash, parentHash, size,
                                         version, network, timestamp, seed,
                                         stateHash, historyHash)
        self.isElectionBlock = isElectionBlock
        self.interlink = interlink
        self.parentElectionHash = parentElectionHash
        self.slots = slots
        self.lostRewardSet = lostRewardSet
        self.disabledSet = disabledSet
        self.justification = justification
        for index, transaction in enumerate(transactions):
            tt = type(transaction)
            if tt is not str and tt is not Transaction:
                if tt is dict:
                    transactions[index] = Transaction.deserialize(transaction)
                else:
                    from ..nimiq_client import InternalErrorException

                    raise InternalErrorException(
                        "Couldn't parse Transaction {0}".format(transaction)
                    )
        self.transactions = transactions

    @classmethod
    def deserialize(cls, data):
        params = set(inspect.signature(cls).parameters)
        return cls(**{key: value for key, value in data.items() if key in params}



class Slot:
    """
    Slot returned from the server

    :param slotNumber: Slot number.
    :type slotNumber: int
    :param validator: Address of the validator this slot belongs to.
    :type validator: str
    :param publicKey: Public key of the validator this slot belongs to.
    :type publicKey: str
    """

    def __init__(self, slotNumber, validator, publicKey):
        self.slotNumber = slotNumber
        self.validator_address = validator
        self.validator_pk = publicKey

    @classmethod
    def deserialize(cls, data):
        params = set(inspect.signature(cls).parameters)
        return cls(**{key: value for key, value in data.items() if key in params}



class SlashedSlots:
    """
    Slashed slots returned from the server

    :param blockNumber: Block number for the slashed slots.
    :type blockNumber: int
    :param lostRewards: Bitset indicating lost rewards for the slashed slots.
    :type lostRewards: dict
    :param disabled: Bitset indicating disabled slots.
    :type disabled: dict
    """

    def __init__(self, blockNumber, lostRewards, disabled):
        self.blockNumber = blockNumber
        self.lostRewards = lostRewards
        self.disabled = disabled

    @classmethod
    def deserialize(cls, data):
        params = set(inspect.signature(cls).parameters)
        return cls(**{key: value for key, value in data.items() if key in params}



class ForkProof:
    """
    Fork proof returned by the server

    :param blockNumber: Block number for the fork proof.
    :type blockNumber: int
    :param viewNumber: View number for the fork proof.
    :type viewNumber: int
    :param hashes: List of hashes of the fork proof. The length of the list is
        always 2.
    :type hashes: List of (str)
    """

    def __init__(self, blockNumber, viewNumber, hashes):
        self.blockNumber = blockNumber
        self.viewNumber = viewNumber
        self.hashes = hashes

    @classmethod
    def deserialize(cls, data):
        params = set(inspect.signature(cls).parameters)
        return cls(**{key: value for key, value in data.items() if key in params}
