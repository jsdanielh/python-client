__all__ = ["Staker"]


class Staker:
    """
    Staker returned by the server

    :param address: Address of the staker.
    :type address: str
    :param balance: Balance of the staker.
    :type balance: int
    """

    def __init__(self, address, balance):
        self.address = address
        self.balance = balance
