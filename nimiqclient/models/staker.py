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
    :param delegation: Optional address of the delegated validator
    :type delegation: str, optional
    :param inactiveRelease: Optional inactive release of the staker.
    :type inactiveRelease: int, optional
    """

    def __init__(self, address, balance, inactiveBalance, delegation=None,
                 inactiveRelease=None):
        self.address = address
        self.balance = balance
        self.delegation = delegation
        self.inactiveBalance = inactiveBalance
        self.inactiveRelease = inactiveRelease
