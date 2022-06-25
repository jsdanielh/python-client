from .models.account import *
from .models.block import *
from .models.inherent import *
from .models.mempool import *
from .models.node import *
from .models.peer import *
from .models.staker import *
from .models.transaction import *
from .models.validator import *

import json
import websocket
import requests
from requests.auth import HTTPBasicAuth

__all__ = ["NimiqClient", "InternalErrorException", "RemoteErrorException"]


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

    :param scheme: Protocol scheme, "http" or "https" or "ws".
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
        if scheme not in ["ws", "http", "https"]:
            raise InternalErrorException("Invalid scheme: {}".format(scheme))

        self.websocket = scheme == "ws"
        self.auth = HTTPBasicAuth(user, password)

        if self.websocket:
            self.url += "/ws"
            self.session = websocket.create_connection(self.url)
        else:
            self.session = requests.Session()

    def _call(self, method, *args):
        """
        Used in all JSONRPC requests to fetch the data.

        :param method: JSONRPC method.
        :type method: str
        :param params: Parameters used by the request.
        :type params: list
        :return: If successful, returns the model representation of the
            result, None otherwise.
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
        call_object = json.dumps(call_object)

        # make request
        req_error = None
        try:
            if self.websocket:
                self.session.send(
                    call_object
                )
                resp_object = json.loads(self.session.recv())
            else:
                resp_object = self.session.post(
                    self.url, data=call_object, auth=self.auth
                ).json()

        except Exception as e:
            req_error = e
        # raise if there was any error
        if req_error is not None:
            raise InternalErrorException(req_error)
        error = resp_object.get("error")
        if error is not None:
            raise RemoteErrorException(
                error.get("message"), error.get("code"))

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
        :rtype: list of (str)
        """
        result = self._call("listAccounts")
        return result if result is not None else []

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

        :return: Consensus state. "established" is the value for a good state,
            other values indicate bad.
        :rtype: bool
        """
        return self._call("isConsensusEstablished")

    def create_account(self, passphrase=None):
        """
        Creates a new account and stores its private key in the client store.

        :param passphrase: Private Key passphrase to add to the account.
        :type passphrase: str
        :return: Information on the wallet that was created using the command.
        :rtype: WalletAccount
        """
        return WalletAccount(**self._call("createAccount", passphrase))

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
        :return: Details about the account. Returns the default empty basic
            account for non-existing accounts.
        :rtype: Account or VestingContract or HTLC
        """
        return self._get_account(self._call("getAccountByAddress", address))

    def get_active_validators(self):
        """
        Returns a dictionary with the set of the current active validators.

        :return: The current set of active validators using a dictionary with
            the validator address as key (str) and the balance as value (int).
        :rtype: dict

        """
        return self._call("getActiveValidators")

    def get_balance(self, address):
        """
        Returns the balance of the account of given address.

        :param address: Address to check for balance.
        :type address: str
        :return: The current balance at the specified address (in smallest
            unit).
        :rtype: int
        """
        return self._call("getBalance", address)

    def get_block_by_hash(self, hash, include_transactions=None):
        """
        Returns information about a block by hash.

        :param hash: Hash of the block to gather information on.
        :type hash: str
        :param include_transactions: If True it returns the full transaction
            objects, if False only the hashes of the transactions.
        :type include_transactions: bool, optional
        :return: A block object or None when no block was found.
        :rtype: Block or None
        """
        result = None
        result = self._call("getBlockByHash", hash, include_transactions)
        return self._get_block(result) if result is not None else None

    def get_block_by_number(self, height, include_transactions=None):
        """
        Returns information about a block by block number.

        :param height: The height of the block to gather information on.
        :type height: int
        :param include_transactions: If True it returns the full transaction
            objects, if False only the hashes of the transactions.
        :type include_transactions: bool, optional
        :return: A block object or None when no block was found.
        :rtype: Block or None
        """
        result = None
        result = self._call("getBlockByNumber", height,
                            include_transactions)
        return Block(**result) if result is not None else None

    def get_block_transaction_count_by_hash(self, hash):
        """
        Returns the number of transactions in a block from a block matching
        the given block hash.

        :param hash: Hash of the block.
        :type hash: str
        :return: Number of transactions in the block found, or None, when no
            block was found.
        :rtype: int or None
        """
        return self._call("getBlockTransactionCountByHash", hash)

    def get_block_transaction_count_by_number(self, height):
        """
        Returns the number of transactions in a block matching the given block
        number.

        :param height: Height of the block.
        :type height: int
        :return: Number of transactions in the block found, or None, when no
            block was found.
        :rtype: int or None
        """
        return self._call("getBlockTransactionCountByNumber", height)

    def get_current_slashed_slots(self):
        """
        Returns the current slashed slots.

        :return: Current slashed slots.
        :rtype: SlashedSlots
        """
        return SlashedSlots(**self.call("getCurrentSlashedSlots"))

    def get_inherents_by_batch_number(self, batch_number):
        """
        Returns information about inherents by batch number.

        :param batch_number: Batch number for which the inherents are going to
            be gathered.
        :type batch_number: int
        :return: A list of inherent objects.
        :rtype: List of (Inherent)
        """
        result = self._call(
            "getInherentsByBatchNumber", batch_number)
        if result is not None:
            return [Inherent(**inherent) for inherent in result]
        else:
            return []

    def get_inherents_by_block_number(self, height):
        """
        Returns information about inherents by block number.

        :param height: Height of the block containing the inherents.
        :type height: int
        :return: A list of inherent objects.
        :rtype: List of (Inherent)
        """
        result = self._call(
            "getInherentsByBlockNumber", height)
        if result is not None:
            return [Inherent(**inherent) for inherent in result]
        else:
            return []

    def get_parked_validators(self):
        """
        Returns the set of current parked validators.

        :return: Set of current parked validators.
        :rtype: ParkedValidators
        """
        return ParkedValidators(**self.call("getParkedValidators"))

    def get_previous_slashed_slots(self):
        """
        Returns the previous slashed slots.

        :return: Previous slashed slots.
        :rtype: SlashedSlots
        """
        return SlashedSlots(**self.call("getPreviousSlashedSlots"))

    def get_raw_transaction_info(self, transaction):
        """
        Deserializes hex-encoded transaction and returns a transaction object.

        :param transaction: The hex encoded signed transaction.
        :type transaction: str
        :return: The transaction object.
        :rtype: Transaction
        """
        return Transaction(**self._call("getRawTransactionInfo", transaction))

    def get_staker_by_address(self, address):
        """
        Gets a staker using its address

        :param address: Address of the staker.
        :type address: str
        :return: The staker object.
        :rtype: Staker
        """
        return Staker(**self._call("getStakerByAddress", address))

    def get_transactions_by_address(self, address,
                                    number_of_transactions=None):
        """
        Returns the latest transactions successfully performed by or for an
        address. Note that this information might change when blocks are
        reverted on the local state due to forks.

        :param address: Address of which transactions should be gathered.
        :type address: str
        :param number_of_transactions: Maximum number of transactions that
            shall be returned.
        :type number_of_transactions: int, optional
        :return: List of transactions linked to the requested address.
        :rtype: list of (Transaction)
        """
        result = None
        result = self._call(
            "getTransactionsByAddress", address, number_of_transactions
        )
        return [Transaction(**tx) for tx in result]

    def get_transaction_hashes_by_address(self, address,
                                          number_of_transactions=None):
        """
        Returns the hashes of the latest transactions successfully performed
        by or for an address. Note that this information might change when
        blocks are reverted on the local state due to forks.

        :param address: Address of which transactions should be gathered.
        :type address: str
        :param number_of_transactions: Maximum number of transactions that
            shall be returned.
        :type number_of_transactions: int, optional
        :return: List of hashes of transactions linked to the requested
            address.
        :rtype: list of (str)
        """
        result = None
        result = self._call(
            "getTransactionHashesByAddress", address,
            number_of_transactions)
        return result

    def get_transactions_by_batch_number(self, batch_number):
        """
        Returns information about transactions by batch number.

        :param batch_number: Batch number for which the transactions are going
            to be gathered.
        :type batch_number: int
        :return: A list of transaction objects.
        :rtype: List of (Transaction)
        """
        result = self._call(
            "getTransactionsByBatchNumber", batch_number)
        if result is not None:
            return [Transaction(**tx) for tx in result]
        else:
            return []

    def get_transactions_by_block_number(self, height):
        """
        Returns information about transactions by block number.

        :param height: Height of the block containing the transactions.
        :type height: int
        :return: A list of transaction objects.
        :rtype: List of (Transaction)
        """
        result = self._call(
            "getTransactionsByBlockNumber", height)
        if result is not None:
            return [Transaction(**tx) for tx in result]
        else:
            return []

    def get_transaction_by_hash(self, hash):
        """
        Returns the information about a transaction requested by transaction
        hash.

        :param hash: Hash of a transaction.
        :type hash: str
        :return: A transaction object or None when no transaction was found.
        :rtype: Transaction or None
        """
        result = self._call("getTransactionByHash", hash)
        return Transaction(**result) if result is not None else None

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
        :param include_stakers: Set to true to include stakers in the
            Validator object to be returned.
        :type include_stakers: bool, optional
        :return: Validator for the corresponding address
        :rtype: Validator
        """
        result = None
        result = self._call(
            "getValidatorByAddress", address, include_stakers
        )
        return Validator(**result) if result is not None else None

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

    def importRawKey(self, private_key, passphrase=None):
        """
        Imports a raw key into the wallet.

        :param private_key: Private key to be imported.
        :type address: str
        :param passphrase: Optional passphrase to add to the private key.
        :type passphrase: str
        :return: Address of the imported raw key.
        :rtype: str
        """
        return self._call("importRawKey", private_key, passphrase)

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

    def lock_account(self, address):
        """
        Locks an account in the wallet

        :param address: Address of the account to be locked.
        :type address: sre
        """
        self._call("lockAccount", address)

    def mempool(self):
        """
        Returns information on the current mempool situation. This will
        provide an overview of the number of transactions sorted into buckets
        based on their fee per byte (in smallest unit).

        :return: Mempool information.
        :rtype: MempoolInfo
        """
        result = self._call("mempool")
        return MempoolInfo(**result)

    def mempool_content(self, include_transactions=None):
        """
        Returns transactions that are currently in the mempool.

        :param include_transactions: If True includes full transactions, if
            False includes only transaction hashes.
        :type include_transactions: bool, optional
        :return: List of transactions(either represented by the transaction
            hash or a transaction object).
        :rtype: list of(Transaction or str)
        """
        result = None
        result = self._call("mempoolContent", include_transactions)
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
        :rtype: list of(Peer)
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
        Sends a signed message call transaction or a contract creation, if the
        data field contains code.

        :param transaction: The hex encoded signed transaction
        :type transaction: str
        :return: The Hex-encoded transaction hash.
        :rtype: str
        """
        return self._call("sendRawTransaction", transaction)

    def send_basic_transaction(self, address, recipient, value, fee,
                               validityStartHeight):
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
        :param validityStartHeight: The validity start height for the
            transaction.
        :type validityStartHeight: int
        :return: The Hex-encoded transaction hash.
        :rtype: str
        """
        return self._call("sendBasicTransaction", address, recipient, value,
                          fee, validityStartHeight)

    def unlock_account(self, address, passphrase=None, duration=None):
        """
        Unlocks a wallet account

        :param address: The account address.
        :type address: str
        :param passphrase: Optional passphrase if the accounts requires it.
        :type passphrase: str
        :param duration: Optional duration in which the account is unlocked.
        :type duration: int
        """
        self._call("unlockAccount", address, passphrase, duration)
