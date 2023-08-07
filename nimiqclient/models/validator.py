__all__ = ["ParkedValidators", "Validator"]


class Validator:
    """
    Validator returned by the server

    :param address: Address of the validator.
    :type address: str
    :param signingKey: Signing key of the validator.
    :type signingKey: str
    :param votingKey: Voting key of the validator.
    :type votingKey: str
    :param rewardAddress: Reward address of the validator.
    :type rewardAddress: str
    :param balance: Balance of the validator.
    :type balance: int
    :param numStakers: Number of stakers for this validator.
    :type numStakers: int
    :param retired: Flag that indicates the retired condition.
    :type retired: bool
    :param inactivityFlag: Optional inactivity flag.
    :type inactivityFlag: bool, optional
    :param signalData: Signal data for the validator.
    :type signalData: str, optional
    :param jailRelease: Optional value when the validator will be released from
        failing.
    :type jailRelease: int, optional
    """

    def __init__(self, address, signingKey, votingKey, rewardAddress, balance,
                 numStakers, retired, inactivityFlag=None,
                 signalData=None, jailRelease=None):
        self.address = address
        self.signingKey = signingKey
        self.votingKey = votingKey
        self.rewardAddress = rewardAddress
        self.balance = balance
        self.numStakers = numStakers
        self.inactivityFlag = inactivityFlag
        self.signalData = signalData
        self.retired = retired
        self.jailRelease = jailRelease


class ParkedValidators:
    """
    Parked validators returned by the server

    :param blockNumber: Block number in which the validators were parked.
    :type blockNumber: int
    :param validators: List of parked validators
    :type validators: List of (Validator)
    """

    def __init__(self, blockNumber, validators):
        self.blockNumber = blockNumber
        self.validators = [Validator(**validator) for validator in validators]
