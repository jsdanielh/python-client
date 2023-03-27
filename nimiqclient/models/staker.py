__all__ = ["Staker"]


class Staker:
    """
    Staker returned by the server

    :param address: Address of the staker.
    :type address: str
    :param balance: Balance of the staker.
    :type balance: int
    :param delegation: Optional address of the delegated validator
    :type delegation: str, optional
    """

    def __init__(self, address, balance, delegation=None):
        self.address = address
        self.balance = balance
        self.delegation = delegation
