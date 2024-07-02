__all__ = ["CreateStakerLog", "CreateValidatorLog", "DeleteValidatorLog",
           "HTLCCreateLog", "HTLCEarlyResolveLog", "HTLCRegularTransferLog",
           "HTLCTimeoutResolveLog", "InactivateValidatorLog", "Log",
           "LogType", "ParkLog", "PayFeeLog", "PayoutRewardLog",
           "ReactivateValidatorLog", "RevertContractLog", "SlashLog",
           "StakeLog", "TransferLog", "UnparkValidatorLog", "UnstakeLog",
           "UpdateStakerLog", "UpdateValidatorLog", "VestingCreateLog"]


class LogType:
    """
    Type of a Nimiq log.
    """
    PAY_FEE = 'pay-fee'
    """Pay fee log."""
    TRANSFER = 'transfer'
    """Transfer log."""
    HTLC_CREATE = 'htlc-create'
    """HTLC create log."""
    HTLC_TIMEOUT_RESOLVE = "htlc-timeout-resolve"
    """HTLC timeout resolve log."""
    HTLC_REGULAR_TRANSFER = "htlc-regular-transfer"
    """HTLC regular transfer log."""
    HTLC_EARLY_RESOLVE = "htlc-early-resolve"
    """HTLC regular early log."""
    VESTING_CREATE = "vesting-create"
    """Vesting create log."""
    CREATE_VALIDATOR = "create-validator"
    """Create validator log."""
    UPDATE_VALIDATOR = "update-validator"
    """Update validator log."""
    INACTIVATE_VALIDATOR = "inactivate-validator"
    """Inactivate validator log."""
    REACTIVATE_VALIDATOR = "reactivate-validator"
    """Reactivate validator log."""
    UNPARK_VALIDATOR = "unpark-validator"
    """Unpark validator log."""
    CREATE_STAKER = "create-staker"
    """Create staker log."""
    STAKE = "stake"
    """Stake log."""
    UPDATE_STAKER = "update-staker"
    """Update staker log."""
    DELETE_VALIDATOR = "delete-validator"
    """Delete validator log."""
    UNSTAKE = "unstake"
    """Unstake log."""
    PAYOUT_REWARD = "payout-reward"
    """Payout reward log."""
    PARK = "park"
    """Park log."""
    SLASH = "slash"
    """Slash log."""
    REVERT_CONTRACT = "revert-contract"
    """Revert contract log."""


class Log:
    """
    Log returned by the server.

    :param type: The log type associated with the log.
    :type type: LogType
    """

    def __init__(self, type):
        self.type = type

    @classmethod
    def deserialize(cls, data):
        params = set(inspect.signature(cls).parameters)
        return cls(**{key: value for key, value in data.items() if key in params}

    @staticmethod
    def get_log(data):
        """
        Get the specific log type from the dictionary data.

        :param data: The dictionary containing the data.
        :type data: dict
        :return: Log object.
        :rtype: Log or a subtype of Log.
        """
        # First we need to remove reserved words
        if 'from' in data:
            data['from_'] = data.pop('from')

        # Then do the decoding
        type = data.get("type")
        if type == LogType.PAY_FEE:
            return PayFeeLog.deserialize(data)
        elif type == LogType.TRANSFER:
            return TransferLog.deserialize(data)
        elif type == LogType.HTLC_CREATE:
            return HTLCCreateLog.deserialize(data)
        elif type == LogType.HTLC_TIMEOUT_RESOLVE:
            return HTLCTimeoutResolveLog.deserialize(data)
        elif type == LogType.HTLC_REGULAR_TRANSFER:
            return HTLCRegularTransferLog.deserialize(data)
        elif type == LogType.HTLC_EARLY_RESOLVE:
            return HTLCEarlyResolveLog.deserialize(data)
        elif type == LogType.VESTING_CREATE:
            return VestingCreateLog.deserialize(data)
        elif type == LogType.CREATE_VALIDATOR:
            return CreateValidatorLog.deserialize(data)
        elif type == LogType.UPDATE_VALIDATOR:
            return UpdateValidatorLog.deserialize(data)
        elif type == LogType.INACTIVATE_VALIDATOR:
            return InactivateValidatorLog.deserialize(data)
        elif type == LogType.REACTIVATE_VALIDATOR:
            return ReactivateValidatorLog.deserialize(data)
        elif type == LogType.UNPARK_VALIDATOR:
            return UnparkValidatorLog.deserialize(data)
        elif type == LogType.CREATE_STAKER:
            return CreateStakerLog.deserialize(data)
        elif type == LogType.STAKE:
            return StakeLog.deserialize(data)
        elif type == LogType.UPDATE_STAKER:
            return UpdateStakerLog.deserialize(data)
        elif type == LogType.DELETE_VALIDATOR:
            return DeleteValidatorLog.deserialize(data)
        elif type == LogType.UNSTAKE:
            return UnstakeLog.deserialize(data)
        elif type == LogType.PAYOUT_REWARD:
            return PayoutRewardLog.deserialize(data)
        elif type == LogType.PARK:
            return ParkLog.deserialize(data)
        elif type == LogType.SLASH:
            return SlashLog.deserialize(data)
        elif type == LogType.REVERT_CONTRACT:
            return RevertContractLog.deserialize(data)
        else:
            return Log.deserialize(data)


class PayFeeLog(Log):
    """
    Fee payment log returned by the server.

    :param type: The log type associated with the log.
    :type type: LogType
    :param from_: Sender of the fee associated with the log.
    :type from_: str
    :param fee: Fee associated with the log.
    :type fee: int
    """

    def __init__(self, type, from_, fee):
        super(PayFeeLog, self).__init__(type)
        self.sender = from_
        self.fee = fee

    @classmethod
    def deserialize(cls, data):
        params = set(inspect.signature(cls).parameters)
        return cls(**{key: value for key, value in data.items() if key in params}


class TransferLog(Log):
    """
    Transfer log returned by the server.

    :param type: The log type associated with the log.
    :type type: LogType
    :param from_: Sender of the transaction associated with the log.
    :type from_: str
    :param to: Recipient of the transaction associated with the log.
    :type to: str
    :param amount: Amount of the transaction associated with the log.
    :type amount: int
    """

    def __init__(self, type, from_, to, amount):
        super(TransferLog, self).__init__(type)
        self.sender = from_
        self.recipient = to
        self.amount = amount

    @classmethod
    def deserialize(cls, data):
        params = set(inspect.signature(cls).parameters)
        return cls(**{key: value for key, value in data.items() if key in params}


class HTLCCreateLog(Log):
    """
    HTLC creation log returned by the server.

    :param type: The log type associated with the log.
    :type type: LogType
    :param contractAddress: Contract address of the HTLC associated with the
        log.
    :type contractAddress: str
    :param sender: Sender of the HTLC associated with the log.
    :type sender: str
    :param recipient: Recipient of the HTLC associated with the log.
    :type recipient: str
    :param hashAlgorithm: Hash algorithm of the HTLC associated with the log.
    :type hashAlgorithm: str
    :param hashRoot: Hash root of the HTLC associated with the log.
    :type hashRoot: str
    :param hashCount: Hash count of the HTLC associated with the log.
    :type hashCount: int
    :param timeout: Timeout of the HTLC associated with the log.
    :type timeout: int
    :param totalAmount: Total amount of the HTLC associated with the log.
    :type totalAmount: int
    """

    def __init__(self, type, contractAddress, sender, recipient,
                 hashAlgorithm, hashRoot, hashCount, timeout, totalAmount):
        super(TransferLog, self).__init__(type)
        self.contractAddress = contractAddress
        self.sender = sender
        self.recipient = recipient
        self.hashAlgorithm = hashAlgorithm
        self.hashRoot = hashRoot
        self.hashCount = hashCount
        self.timeout = timeout
        self.totalAmount = totalAmount

    @classmethod
    def deserialize(cls, data):
        params = set(inspect.signature(cls).parameters)
        return cls(**{key: value for key, value in data.items() if key in params}


class HTLCTimeoutResolveLog(Log):
    """
    HTLC timeout resolve log returned by the server.

    :param type: The log type associated with the log.
    :type type: LogType
    :param contractAddress: Contract address of the HTLC associated with the
        log.
    :type contractAddress: str
    """

    def __init__(self, type, contractAddress):
        super(HTLCTimeoutResolveLog, self).__init__(type)
        self.contractAddress = contractAddress

    @classmethod
    def deserialize(cls, data):
        params = set(inspect.signature(cls).parameters)
        return cls(**{key: value for key, value in data.items() if key in params}


class HTLCRegularTransferLog(Log):
    """
    HTLC regular transfer log returned by the server.

    :param type: The log type associated with the log.
    :type type: LogType
    :param contractAddress: Contract address of the HTLC associated with the
        log.
    :type contractAddress: str
    :param preImage: Pre-image of the HTLC associated with the log.
    :type preImage: str
    :param hashDepth: Hash depth of the HTLC associated with the log.
    :type hashDepth: int
    """

    def __init__(self, type, contractAddress, preImage, hashDepth):
        super(HTLCRegularTransferLog, self).__init__(type)
        self.contractAddress = contractAddress
        self.preImage = preImage
        self.hashDepth = hashDepth

    @classmethod
    def deserialize(cls, data):
        params = set(inspect.signature(cls).parameters)
        return cls(**{key: value for key, value in data.items() if key in params}


class HTLCEarlyResolveLog(Log):
    """
    HTLC early resolve log returned by the server.

    :param type: The log type associated with the log.
    :type type: LogType
    :param contractAddress: Contract address of the HTLC associated with the
        log.
    :type contractAddress: str
    """

    def __init__(self, type, contractAddress):
        super(HTLCEarlyResolveLog, self).__init__(type)
        self.contractAddress = contractAddress

    @classmethod
    def deserialize(cls, data):
        params = set(inspect.signature(cls).parameters)
        return cls(**{key: value for key, value in data.items() if key in params}


class VestingCreateLog(Log):
    """
    Vesting creation log returned by the server.

    :param type: The log type associated with the log.
    :type type: LogType
    :param contractOwner: Contract owner of the Vesting associated with the
        log.
    :type contractOwner: str
    :param owner: Owner of the Vesting associated with the log.
    :type owner: str
    :param startTime: Start time of the Vesting associated with the log.
    :type startTime: int
    :param timeStep: Time step of the Vesting associated with the log.
    :type timeStep: int
    :param stepAmount: Step amount of the Vesting associated with the log.
    :type stepAmount: int
    :param totalAmount: Total amount of the Vesting associated with the log.
    :type totalAmount: int
    """

    def __init__(self, type, contractOwner, owner, startTime, timeStep,
                 stepAmount, totalAmount):
        super(VestingCreateLog, self).__init__(type)
        self.contractOwner = contractOwner
        self.owner = owner
        self.startTime = startTime
        self.timeStep = timeStep
        self.stepAmount = stepAmount
        self.totalAmount = totalAmount

    @classmethod
    def deserialize(cls, data):
        params = set(inspect.signature(cls).parameters)
        return cls(**{key: value for key, value in data.items() if key in params}


class CreateValidatorLog(Log):
    """
    Validator creation log returned by the server.

    :param type: The log type associated with the log.
    :type type: LogType
    :param validatorAddress: Address of the validator associated with the log.
    :type validatorAddress: str
    :param rewardAddress: Reward address of the validator associated with the
        log.
    :type rewardAddress: str
    """

    def __init__(self, type, validatorAddress, rewardAddress):
        super(CreateValidatorLog, self).__init__(type)
        self.validatorAddress = validatorAddress
        self.rewardAddress = rewardAddress

    @classmethod
    def deserialize(cls, data):
        params = set(inspect.signature(cls).parameters)
        return cls(**{key: value for key, value in data.items() if key in params}


class UpdateValidatorLog(Log):
    """
    Validator update log returned by the server.

    :param type: The log type associated with the log.
    :type type: LogType
    :param validatorAddress: Address of the validator associated with the log.
    :type validatorAddress: str
    :param oldRewardAddress: Old reward address of the validator associated
        with the log.
    :type oldRewardAddress: str
    :param newRewardAddress: New reward address of the validator associated
        with the log.
    :type newRewardAddress: str
    """

    def __init__(self, type, validatorAddress, oldRewardAddress,
                 newRewardAddress):
        super(UpdateValidatorLog, self).__init__(type)
        self.validatorAddress = validatorAddress
        self.oldRewardAddress = oldRewardAddress
        self.newRewardAddress = newRewardAddress

    @classmethod
    def deserialize(cls, data):
        params = set(inspect.signature(cls).parameters)
        return cls(**{key: value for key, value in data.items() if key in params}


class InactivateValidatorLog(Log):
    """
    Validator inactivation log returned by the server.

    :param type: The log type associated with the log.
    :type type: LogType
    :param validatorAddress: Address of the validator associated with the log.
    :type validatorAddress: str
    """

    def __init__(self, type, validatorAddress):
        super(InactivateValidatorLog, self).__init__(type)
        self.validatorAddress = validatorAddress

    @classmethod
    def deserialize(cls, data):
        params = set(inspect.signature(cls).parameters)
        return cls(**{key: value for key, value in data.items() if key in params}


class ReactivateValidatorLog(Log):
    """
    Validator reactivation log returned by the server.

    :param type: The log type associated with the log.
    :type type: LogType
    :param validatorAddress: Address of the validator associated with the log.
    :type validatorAddress: str
    """

    def __init__(self, type, validatorAddress):
        super(ReactivateValidatorLog, self).__init__(type)
        self.validatorAddress = validatorAddress

    @classmethod
    def deserialize(cls, data):
        params = set(inspect.signature(cls).parameters)
        return cls(**{key: value for key, value in data.items() if key in params}


class UnparkValidatorLog(Log):
    """
    Validator unparking log returned by the server.

    :param type: The log type associated with the log.
    :type type: LogType
    :param validatorAddress: Address of the validator associated with the log.
    :type validatorAddress: str
    """

    def __init__(self, type, validatorAddress):
        super(UnparkValidatorLog, self).__init__(type)
        self.validatorAddress = validatorAddress

    @classmethod
    def deserialize(cls, data):
        params = set(inspect.signature(cls).parameters)
        return cls(**{key: value for key, value in data.items() if key in params}


class CreateStakerLog(Log):
    """
    Staker creation log returned by the server.

    :param type: The log type associated with the log.
    :type type: LogType
    :param stakerAddress: Address of the staker associated with the log.
    :type stakerAddress: str
    :param validatorAddress: Validator address of the staker associated with
        the log.
    :type validatorAddress: str
    :param value: Stake value associated with the log.
    :type value: int
    """

    def __init__(self, type, stakerAddress, validatorAddress, value):
        super(CreateStakerLog, self).__init__(type)
        self.stakerAddress = stakerAddress
        self.validatorAddress = validatorAddress
        self.value = value

    @classmethod
    def deserialize(cls, data):
        params = set(inspect.signature(cls).parameters)
        return cls(**{key: value for key, value in data.items() if key in params}


class StakeLog(Log):
    """
    Stake log returned by the server.

    :param type: The log type associated with the log.
    :type type: LogType
    :param stakerAddress: Address of the staker associated with the log.
    :type stakerAddress: str
    :param value: Stake value associated with the log.
    :type value: int
    :param validatorAddress: Optional validator address of the staker
        associated with the log.
    :type validatorAddress: str
    """

    def __init__(self, type, stakerAddress, value, validatorAddress=None):
        super(StakeLog, self).__init__(type)
        self.stakerAddress = stakerAddress
        self.validatorAddress = validatorAddress
        self.value = value

    @classmethod
    def deserialize(cls, data):
        params = set(inspect.signature(cls).parameters)
        return cls(**{key: value for key, value in data.items() if key in params}


class UpdateStakerLog(Log):
    """
    Staker update log returned by the server.

    :param type: The log type associated with the log.
    :type type: LogType
    :param stakerAddress: Address of the staker associated with the log.
    :type stakerAddress: str
    :param oldValidatorAddress: Optional old validator address of the staker
        associated with the log.
    :type oldValidatorAddress: str
    :param newValidatorAddress: Optional new validator address of the staker
        associated with the log.
    :type newValidatorAddress: str
    """

    def __init__(self, type, stakerAddress, oldValidatorAddress=None,
                 newValidatorAddress=None):
        super(UpdateStakerLog, self).__init__(type)
        self.stakerAddress = stakerAddress
        self.oldValidatorAddress = oldValidatorAddress
        self.newValidatorAddress = newValidatorAddress

    @classmethod
    def deserialize(cls, data):
        params = set(inspect.signature(cls).parameters)
        return cls(**{key: value for key, value in data.items() if key in params}


class DeleteValidatorLog(Log):
    """
    Validator deletion log returned by the server.

    :param type: The log type associated with the log.
    :type type: LogType
    :param validatorAddress: Address of the validator associated with the log.
    :type validatorAddress: str
    :param rewardAddress: Reward address of the validator associated with the
        log.
    :type rewardAddress: str
    """

    def __init__(self, type, validatorAddress, rewardAddress):
        super(DeleteValidatorLog, self).__init__(type)
        self.validatorAddress = validatorAddress
        self.rewardAddress = rewardAddress

    @classmethod
    def deserialize(cls, data):
        params = set(inspect.signature(cls).parameters)
        return cls(**{key: value for key, value in data.items() if key in params}


class UnstakeLog(Log):
    """
    Unstake log returned by the server.

    :param type: The log type associated with the log.
    :type type: LogType
    :param stakerAddress: Address of the staker associated with the log.
    :type stakerAddress: str
    :param value: Stake value associated with the log.
    :type value: int
    :param validatorAddress: Optional validator address of the staker
        associated with the log.
    :type validatorAddress: str
    """

    def __init__(self, type, stakerAddress, value, validatorAddress=None):
        super(UnstakeLog, self).__init__(type)
        self.stakerAddress = stakerAddress
        self.validatorAddress = validatorAddress
        self.value = value

    @classmethod
    def deserialize(cls, data):
        params = set(inspect.signature(cls).parameters)
        return cls(**{key: value for key, value in data.items() if key in params}


class PayoutRewardLog(Log):
    """
    Payout reward log returned by the server.

    :param type: The log type associated with the log.
    :type type: LogType
    :param to: Recipient of the payout reward associated with the log.
    :type to: str
    :param value: Value of the transaction associated with the log.
    :type value: int
    """

    def __init__(self, type, to, value):
        super(PayoutRewardLog, self).__init__(type)
        self.recipient = to
        self.value = value

    @classmethod
    def deserialize(cls, data):
        params = set(inspect.signature(cls).parameters)
        return cls(**{key: value for key, value in data.items() if key in params}


class ParkLog(Log):
    """
    Validator parking log returned by the server.

    :param type: The log type associated with the log.
    :type type: LogType
    :param validatorAddress: Address of the validator associated with the log.
    :type validatorAddress: str
    :param eventBlock: Event block associated with the log.
    :type eventBlock: int
    """

    def __init__(self, type, validatorAddress, eventBlock):
        super(ParkLog, self).__init__(type)
        self.validatorAddress = validatorAddress
        self.eventBlock = eventBlock

    @classmethod
    def deserialize(cls, data):
        params = set(inspect.signature(cls).parameters)
        return cls(**{key: value for key, value in data.items() if key in params}


class SlashLog(Log):
    """
    Validator slashing log returned by the server.

    :param type: The log type associated with the log.
    :type type: LogType
    :param validatorAddress: Address of the validator associated with the log.
    :type validatorAddress: str
    :param eventBlock: Event block associated with the log.
    :type eventBlock: int
    :param slot: Slot associated with the log.
    :type slot: int
    :param newlyDisabled: Flag indicating if the validator has been newly
        disabled or not.
    :type newlyDisabled: bool
    """

    def __init__(self, type, validatorAddress, eventBlock, slot,
                 newlyDisabled):
        super(SlashLog, self).__init__(type)
        self.validatorAddress = validatorAddress
        self.eventBlock = eventBlock
        self.slot = slot
        self.newlyDisabled = newlyDisabled

    @classmethod
    def deserialize(cls, data):
        params = set(inspect.signature(cls).parameters)
        return cls(**{key: value for key, value in data.items() if key in params}


class RevertContractLog(Log):
    """
    Contract reversion log returned by the server.

    :param type: The log type associated with the log.
    :type type: LogType
    :param contractAddress: Address of the contract associated with the log.
    :type contractAddress: str
    """

    def __init__(self, type, contractAddress):
        super(RevertContractLog, self).__init__(type)
        self.contractAddress = contractAddress

    @classmethod
    def deserialize(cls, data):
        params = set(inspect.signature(cls).parameters)
        return cls(**{key: value for key, value in data.items() if key in params}
