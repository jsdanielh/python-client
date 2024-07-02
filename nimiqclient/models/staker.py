__all__ = ["Staker"]


class Staker:
    """
    Staker returned by the server

    :param address: Address of the staker.
    :type address: str
    :param balance: Balance of the staker.
    :type balance: int
    :param inactiveBalance: Inactive balance of the staker.
    :type inactiveBalance: int
    :param retiredBalance: Retired balance of the staker.
    :type retiredBalance: int
    :param delegation: Optional address of the delegated validator
    :type delegation: str, optional
    :param inactiveFrom: Optional value indicating since which block this
        staker has been inactive.
    :type inactiveFrom: int, optional
    """

    def __init__(self, address, balance, inactiveBalance, retiredBalance,
                 delegation=None, inactiveFrom=None):
        self.address = address
        self.balance = balance
        self.inactiveBalance = inactiveBalance
        self.delegation = delegation
        self.inactiveFrom = inactiveFrom
        self.retiredBalance = retiredBalance

    @classmethod
    def deserialize(cls, data):
        params = set(inspect.signature(cls).parameters)
        return cls(**{key: value for key, value in data.items() if key in params}
