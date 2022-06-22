__all__ = ["NimiqClient", "InternalErrorException", "RemoteErrorException"]

from .models.account import *
from .models.block import *
from .models.mempool import *
from .models.node import *
from .models.peer import *
from .models.transaction import *
from .models.validator import *

import requests
from requests.auth import HTTPBasicAuth
from enum import Enum


class InternalErrorException(Exception):
    """
    Internal error during a JSON RPC request.
    """

    pass


class RemoteErrorException(Exception):
    """
    Exception on the remote server.
    """

    def __init__(self, message, code):
        super(RemoteErrorException, self).__init__(
            "{0} ({1})".format(message, code))


class NimiqClient:
    """
    API client for the Nimiq JSON RPC server.

    :param scheme: Protocol squeme, "http" or "https".
    :type scheme: str, optional
    :param user: Authorized user.
    :type user: str, optional
    :param password: Password for the authorized user.
    :type password: str, optional
    :param host: Host IP address.
    :type host: str, optional
    :param port: Host port.
    :type port: int, optional
    """

    def __init__(
        self, scheme="http", user="", password="", host="127.0.0.1", port=8648
    ):
        self.id = 0
        self.url = "{0}://{1}:{2}".format(scheme, host, port)
        self.auth = HTTPBasicAuth(user, password)
        self.session = requests.Session()

    def _call(self, method, *args):
        """
        Used in all JSONRPC requests to fetch the data.

        :param method: JSONRPC method.
        :type method: str
        :param params: Parameters used by the request.
        :type params: list
        :return: If successful, returns the model representation of the result, None otherwise.
        :rtype: dict
        """

        # increase the JSONRPC client request id
        self.id += 1

        # make JSON object to send to the server
        call_object = {
            "jsonrpc": "2.0",
            "method": method,
            "params": list(args),
            "id": self.id,
        }

        print("{}".format(call_object))

        # make request
        req_error = None
        try:
            resp_object = self.session.post(
                self.url, json=call_object, auth=self.auth
            ).json()

        except Exception as e:
            req_error = e

        # raise if there was any error
        if req_error is not None:
            raise InternalErrorException(req_error)

        error = resp_object.get("error")
        if error is not None:
            raise RemoteErrorException(error.get("message"), error.get("code"))

        return resp_object.get("result")

    def _get_account(self, data):
        """
        Get the specific account type from the dictionary data.

        :param data: The dictionary containing the data.
        :type data: dict
        :return: Account object.
        :rtype: Account or VestingContract or HTLC
        """
        type = data.get("type")
        if type == AccountType.HTLC:
            return HTLC(**data)
        elif type == AccountType.VESTING:
            return VestingContract(**data)
        else:
            return Account(**data)

    def _get_block(self, data):
        """
        Get the specific block type from the dictionary data.

        :param data: The dictionary containing the data.
        :type data: dict
        :return: Block object.
        :rtype: Block or MicroBlock or MacroBlock
        """
        type = data.get("type")
        print("Type {}, data: {}".format(type, data))
        if type == BlockType.MicroBlock:
            return MicroBlock(**data)
        elif type == BlockType.MacroBlock:
            return MacroBlock(**data)
        else:
            return Block(**data)

    def accounts(self):
        """
        Returns a list of addresses owned by client.

        :return: List of Accounts owned by the client.
        :rtype: list of (Account or VestingContract or HTLC)
        """
        return [self._get_account(account) for account in self._call("listAccounts")]

    def batch_number(self):
        """
        Returns the batch number.

        :return: The current batch number the client is on.
        :rtype: int
        """
        return self._call("getBatchNumber")

    def block_number(self):
        """
        Returns the height of most recent block.

        :return: The current block height the client is on.
        :rtype: int
        """
        return self._call("getBlockNumber")

    def consensus(self):
        """
        Returns information on the current consensus state.

        :return: Consensus state. "established" is the value for a good state, other values indicate bad.
        :rtype: bool
        """
        return self._call("isConsensusEstablished")

    def create_account(self, address, public_key, private_key):
        """
        Creates a new account and stores its private key in the client store.

        :param address: Address of the account to create.
        :type address: str
        :param public_key: Public key of the account to create.
        :type address: str
        :param private_key: Private key of the account to create.
        :type address: str
        :return: Information on the wallet that was created using the command.
        :rtype: Wallet
        """
        return Wallet(**self._call("createAccount", address, public_key, private_key))

    def create_raw_transaction(self, transaction):
        """
        Creates and signs a transaction without sending it. The transaction can then be send via sendRawTransaction() without accidentally replaying it.

        :param transaction: The transaction object.
        :type transaction: OutgoingTransaction
        :return: Hex-encoded transaction.
        :rtype: str
        """
        return self._call("createRawTransaction", transaction)

    def epoch_number(self):
        """
        Returns the epoch number.

        :return: The current epoch number the client is on.
        :rtype: int
        """
        return self._call("getEpochNumber")

    def get_account_by_address(self, address):
        """
        Returns details for the account of given address.

        :param address: Address to get account details.
        :type address: str
        :return: Details about the account. Returns the default empty basic account for non-existing accounts.
        :rtype: Account or VestingContract or HTLC
        """
        return self._get_account(self._call("getAccountByAddress", address))

    def get_balance(self, address):
        """
        Returns the balance of the account of given address.

        :param address: Address to check for balance.
        :type address: str
        :return: The current balance at the specified address (in smalest unit).
        :rtype: int
        """
        return self._call("getBalance", address)

    def get_block_by_hash(self, hash, include_transactions=None):
        """
        Returns information about a block by hash.

        :param hash: Hash of the block to gather information on.
        :type hash: str
        :param include_transactions: If True it returns the full transaction objects, if False only the hashes of the transactions.
        :type include_transactions: bool, optional
        :return: A block object or None when no block was found.
        :rtype: Block or None
        """
        result = None
        if include_transactions is not None:
            result = self._call("getBlockByHash", hash, include_transactions)
        else:
            result = self._call("getBlockByHash", hash)
        print("Data {}".format(result))
        return self._get_block(result) if result is not None else None

    def get_block_by_number(self, height, include_transactions=None):
        """
        Returns information about a block by block number.

        :param height: The height of the block to gather information on.
        :type height: int
        :param include_transactions: If True it returns the full transaction objects, if False only the hashes of the transactions.
        :type include_transactions: bool, optional
        :return: A block object or None when no block was found.
        :rtype: Block or None
        """
        result = None
        if include_transactions is not None:
            result = self._call("getBlockByNumber", height,
                                include_transactions)
        else:
            result = self._call("getBlockByNumber", height)
        return Block(**result) if result is not None else None

    def get_block_transaction_count_by_hash(self, hash):
        """
        Returns the number of transactions in a block from a block matching the given block hash.

        :param hash: Hash of the block.
        :type hash: str
        :return: Number of transactions in the block found, or None, when no block was found.
        :rtype: int or None
        """
        return self._call("getBlockTransactionCountByHash", hash)

    def get_block_transaction_count_by_number(self, height):
        """
        Returns the number of transactions in a block matching the given block number.

        :param height: Height of the block.
        :type height: int
        :return: Number of transactions in the block found, or None, when no block was found.
        :rtype: int or None
        """
        return self._call("getBlockTransactionCountByNumber", height)

    def get_transaction_by_block_hash_and_index(self, hash, index):
        """
        Returns information about a transaction by block hash and transaction index position.

        :param hash: Hash of the block containing the transaction.
        :type hash: str
        :param index: Index of the transaction in the block.
        :type index: int
        :return: A transaction object or None when no transaction was found.
        :rtype: Transaction or None
        """
        result = self._call("getTransactionByBlockHashAndIndex", hash, index)
        if result is not None:
            return Transaction(**result)
        else:
            return None

    def get_transaction_by_block_number_and_index(self, height, index):
        """
        Returns information about a transaction by block number and transaction index position.

        :param height: Height of the block containing the transaction.
        :type height: int
        :param index: Index of the transaction in the block.
        :type index: int
        :return: A transaction object or None when no transaction was found.
        :rtype: Transaction or None
        """
        result = self._call(
            "getTransactionByBlockNumberAndIndex", height, index)
        if result is not None:
            return Transaction(**result)
        else:
            return None

    def get_transaction_by_hash(self, hash):
        """
        Returns the information about a transaction requested by transaction hash.

        :param hash: Hash of a transaction.
        :type hash: str
        :return: A transaction object or None when no transaction was found.
        :rtype: Transaction or None
        """
        result = self._call("getTransactionByHash", hash)
        if result is not None:
            return Transaction(**result)
        else:
            return None

    def get_transaction_receipt(self, hash):
        """
        Returns the receipt of a transaction by transaction hash.

        :param hash: Hash of a transaction.
        :type hash: str
        :return: A transaction receipt object, or None when no receipt was found.
        :rtype: TransactionReceipt or None
        """
        result = self._call("getTransactionReceipt", hash)
        if result is not None:
            return TransactionReceipt(**result)
        else:
            return None

    def get_transactions_by_address(self, address, number_of_transactions=None):
        """
        Returns the latest transactions successfully performed by or for an address.
        Note that this information might change when blocks are rewinded on the local state due to forks.

        :param address: Address of which transactions should be gathered.
        :type address: str
        :param number_of_transactions: Number of transactions that shall be returned.
        :type number_of_transactions: int, optional
        :return: List of transactions linked to the requested address.
        :rtype: list of (Transaction)
        """
        result = None
        if number_of_transactions is not None:
            result = self._call(
                "getTransactionsByAddress", address, number_of_transactions
            )
        else:
            result = self._call("getTransactionsByAddress", address)
        return [Transaction(**tx) for tx in result]

    def get_validator_address(self):
        """
        Returns the address of the current validator.

        :return: Address of the current validator.
        :rtype: str or None
        """
        return self._call("getAddress")

    def get_validator_by_address(self, address, include_stakers=None):
        """
        Returns a validator given its address

        :param address: Address for which a validator should be gathered.
        :type address: str
        :param include_stakers: Set to true to include stakers in the Validator object to be returned.
        :type include_stakers: bool, optional
        :return: Validator for the corresponding address
        :rtype: Validator
        """
        result = None
        if include_stakers is not None:
            result = self._call(
                "getValidatorByAddress", address, include_stakers
            )
        else:
            result = self._call("getValidatorByAddress", address)
        print(result)
        return Validator(**result)

    def get_validator_signing_key(self):
        """
        Returns the signing key of the current validator.

        :return: Signing key of the current validator.
        :rtype: str or None
        """
        return self._call("getSigningKey")

    def get_validator_voting_key(self):
        """
        Returns the voting key of the current validator.

        :return: Voting key of the current validator.
        :rtype: str or None
        """
        return self._call("getVotingKey")

    def is_account_imported(self, address):
        """
        Returns wether an account has been imported into the wallet.

        :param address: Address of the account that is going to be checked.
        :type address: str
        :return: Bool indicating wether the account has been imported.
        :rtype: bool
        """
        return self._call("isAccountImported", address)

    def is_account_unlocked(self, address):
        """
        Returns wether an account has been unlocked in the wallet.

        :param address: Address of the account that is going to be checked.
        :type address: str
        :return: Bool indicating wether the account has been unlocked.
        :rtype: bool
        """
        return self._call("isAccountUnlocked", address)

    def mempool(self):
        """
        Returns information on the current mempool situation. This will provide an overview of the number of transactions sorted into buckets based on their fee per byte (in smallest unit).

        :return: Mempool information.
        :rtype: MempoolInfo
        """
        result = self._call("mempool")
        return MempoolInfo(**result)

    def mempool_content(self, include_transactions=None):
        """
        Returns transactions that are currently in the mempool.

        :param include_transactions: If True includes full transactions, if False includes only transaction hashes.
        :type include_transactions: bool, optional
        :return: List of transactions (either represented by the transaction hash or a transaction object).
        :rtype: list of (Transaction or str)
        """
        result = None
        if include_transactions is not None:
            result = self._call("mempoolContent", include_transactions)
        else:
            result = self._call("mempoolContent")
        return [tx if type(tx) is str else Transaction(**tx) for tx in result]

    def min_fee_per_byte(self):
        """
        Returns the minimum fee per byte.

        :return: The new minimum fee per byte.
        :rtype: int
        """
        return self._call("getMinFeePerByte")

    def peer_count(self):
        """

        Returns number of peers currently connected to the client.

        :return: Number of connected peers.
        :rtype: int
        """
        return self._call("getPeerCount")

    def peer_id(self):
        """
        Returns the peer ID of the running client.

        :return: Peer ID of the running client.
        :rtype: string
        """
        return self._call("getPeerId")

    def peer_list(self):
        """
        Returns list of peers known to the client.

        :return: The list of peers.
        :rtype: list of (Peer)
        """
        return [Peer(**peer) for peer in self._call("getPeerList")]

    def peer_state(self, address):
        """
        Returns the state of the peer.

        :param address: The address of the peer.
        :type address: str
        :return: The current state of the peer.
        :rtype: Peer
        """
        return Peer(**self._call("peerState", address))

    def set_peer_state(self, address, command=None):
        """
        Returns the state of the peer.

        :param address: The address of the peer.
        :type address: str
        :param command: The command to send.
        :type command: PeerStateCommand
        :return: The new state of the peer.
        :rtype: Peer
        """
        return Peer(**self._call("peerState", address, command))

    def send_raw_transaction(self, transaction):
        """
        Sends a signed message call transaction or a contract creation, if the data field contains code.

        :param transaction: The hex encoded signed transaction
        :type transaction: str
        :return: The Hex-encoded transaction hash.
        :rtype: str
        """
        return self._call("sendRawTransaction", transaction)

    def send_basic_transaction(self, address, recipient, value, fee, validityStartHeight):
        """
        Creates and send a new basic transaction

        :param address: The sender address.
        :type address: str
        :param recipient: The recipient address.
        :type recipient: str
        :param value: The value of the transaction.
        :type value: int
        :param fee: The fee of the transaction.
        :type fee: int
        :param validityStartHeight: The validity start height for the transaction.
        :type validityStartHeight: int
        :return: The Hex-encoded transaction hash.
        :rtype: str
        """
        return self._call("sendBasicTransaction", address, recipient, value, fee, validityStartHeight)

    def get_raw_transaction_info(self, transaction):
        """
        Deserializes hex-encoded transaction and returns a transaction object.

        :param transaction: The hex encoded signed transaction.
        :type transaction: str
        :return: The transaction object.
        :rtype: Transaction
        """
        return Transaction(**self._call("getRawTransactionInfo", transaction))
