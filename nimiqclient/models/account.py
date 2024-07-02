__all__ = ["AccountType", "Account", "HTLC",
           "VestingContract", "WalletAccount"]

__metaclass__ = type


class AccountType:
    """
    Type of a Nimiq account.
    """

    BASIC = 'basic'
    """Normal Nimiq account."""
    VESTING = 'vesting'
    """Vesting contract."""
    HTLC = 'htlc'
    """Hashed Timelock Contract."""
    STAKING = 'staking'
    """Staking Contract."""


class Account:
    """
    Normal Nimiq account object returned by the server.

    :param address: User friendly address (NQ-address).
    :type address: str
    :param balance: Balance of the account (in smallest unit).
    :type balance: int
    :param type: The account type associated with the account.
    :type type: AccountType
    """

    def __init__(self, address, balance, type):
        self.address = address
        self.balance = balance
        self.type = type

    @classmethod
    def deserialize(cls, data):
        params = set(inspect.signature(cls).parameters)
        return cls(**{key: value for key, value in data.items() if key in params}

    @staticmethod
    def get_account(data):
        """
        Get the specific account type from the dictionary data.

        :param data: The dictionary containing the data.
        :type data: dict
        :return: Account object.
        :rtype: Account or VestingContract or HTLC
        """
        type = data.get("type")
        if type == AccountType.HTLC:
            return HTLC.deserialize(data)
        elif type == AccountType.VESTING:
            return VestingContract.deserialize(data)
        elif type == AccountType.STAKING:
            return StakingContract.deserialize(data)
        else:
            return Account.deserialize(data)


class VestingContract(Account):
    """
    Vesting contract object returned by the server.

    :param address: User friendly address (NQ-address).
    :type address: str
    :param balance: Balance of the account (in smallest unit).
    :type balance: int
    :param type: The account type associated with the account.
    :type type: AccountType
    :param owner: User friendly address (NQ-address) of the owner of the
        vesting contract.
    :type owner: str
    :param vestingStart: The block that the vesting contracted commenced.
    :type vestingStart: int
    :param vestingStepBlocks: The number of blocks after which some part of
        the vested funds is released.
    :type vestingStepBlocks: int
    :param vestingStepAmount: The amount (in smallest unit) released every
        vestingStepBlocks blocks.
    :type vestingStepAmount: int
    :param vestingTotalAmount: The total amount (in smallest unit) that was
        provided at the contract creation.
    :type vestingTotalAmount: int
    """

    def __init__(
        self,
        address,
        balance,
        type,
        owner,
        vestingStart,
        vestingStepBlocks,
        vestingStepAmount,
        vestingTotalAmount,
    ):
        super(VestingContract, self).__init__(address, balance, type)
        self.owner = owner
        self.vestingStart = vestingStart
        self.vestingStepBlocks = vestingStepBlocks
        self.vestingStepAmount = vestingStepAmount
        self.vestingTotalAmount = vestingTotalAmount

    @classmethod
    def deserialize(cls, data):
        params = set(inspect.signature(cls).parameters)
        return cls(**{key: value for key, value in data.items() if key in params}


class HTLC(Account):
    """
    Hashed Timelock Contract object returned by the server.

    :param address: User friendly address (NQ-address).
    :type address: str
    :param balance: Balance of the account (in smallest unit).
    :type balance: int
    :param type: The account type associated with the account.
    :type type: AccountType
    :param sender: User friendly address (NQ-address) of the sender of the
        HTLC.
    :type sender: str
    :param recipient: User friendly address (NQ-address) of the recipient of
        the HTLC.
    :type recipient: str
    :param hashRoot: Hex-encoded 32 byte hash root.
    :type hashRoot: str
    :param hashCount: Number of hashes this HTLC is split into.
    :type hashCount: int
    :param timeout: Block after which the contract can only be used by the
        original sender to recover funds.
    :type timeout: int
    :param totalAmount: The total amount (in smallest unit) that was provided
        at the contract creation.
    :type totalAmount: int
    """

    def __init__(
        self,
        address,
        balance,
        type,
        sender,
        recipient,
        hashRoot,
        hashCount,
        timeout,
        totalAmount,
    ):
        super(HTLC, self).__init__(address, balance, type)
        self.sender = sender
        self.recipient = recipient
        self.hashRoot = hashRoot
        self.hashCount = hashCount
        self.timeout = timeout
        self.totalAmount = totalAmount

    @classmethod
    def deserialize(cls, data):
        params = set(inspect.signature(cls).parameters)
        return cls(**{key: value for key, value in data.items() if key in params}


class StakingContract(Account):
    """
    Staking Contract object returned by the server.

    :param address: User friendly address (NQ-address).
    :type address: str
    :param balance: Balance of the account (in smallest unit).
    :type balance: int
    :param type: The account type associated with the account.
    :type type: AccountType
    """

    def __init__(
        self,
        address,
        balance,
        type,
    ):
        super(StakingContract, self).__init__(address, balance, type)

    @classmethod
    def deserialize(cls, data):
        params = set(inspect.signature(cls).parameters)
        return cls(**{key: value for key, value in data.items() if key in params}


class WalletAccount:
    """
    Account wallet returned by the server.

    :param address: User friendly address (NQ-address).
    :type address: str
    :param publicKey: Hex-encoded 32 byte Ed25519 public key.
    :type publicKey: str
    :param privateKey: Hex-encoded 32 byte Ed25519 private key.
    :type privateKey: str, optional
    """

    def __init__(self, address, publicKey, privateKey):
        self.id = id
        self.address = address
        self.publicKey = publicKey
        self.privateKey = privateKey

    @classmethod
    def deserialize(cls, data):
        params = set(inspect.signature(cls).parameters)
        return cls(**{key: value for key, value in data.items() if key in params}
