from .callback import Callback
from .models.account import *
from .models.block import *
from .models.state import *
from .models.block_log import *
from .models.inherent import *
from .models.mempool import *
from .models.node import *
from .models.peer import *
from .models.staker import *
from .models.state import StateData
from .models.state import BlockchainState
from .models.transaction import *
from .models.validator import *
from .websocket_rpc import NimiqRPCMethods, NimiqSerializer
from .error_exception import InternalErrorException, RemoteErrorException

from typing import Any, Awaitable, Callable, Dict, List
from fastapi_websocket_rpc import WebSocketRpcClient
import json
import requests
from requests.auth import HTTPBasicAuth

__all__ = ["NimiqClient", "InternalErrorException", "RemoteErrorException"]


class NimiqClient:

    WS_RESPONSE_TIMEOUT = 5
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
        self.callbacks = {}
        self.subscriptions = {}
        self.url = "{0}://{1}:{2}".format(scheme, host, port)
        if scheme not in ["ws", "wss", "http", "https"]:
            raise InternalErrorException("Invalid scheme: {}".format(scheme))

        self.websocket = scheme == "ws" or scheme == "wss"
        self.auth = HTTPBasicAuth(user, password)

        if self.websocket:
            self.url += "/" + scheme
            self.session = WebSocketRpcClient(
                self.url,
                NimiqRPCMethods(self),
                serializing_socket_cls=NimiqSerializer,
                default_response_timeout=self.WS_RESPONSE_TIMEOUT,
                ping_interval=None)
            # Disable ping messages since the Nimiq server doesn't support it
            self.session.MAX_CONNECTION_ATTEMPTS = 0
        else:
            self.session = requests.Session()

    async def __aenter__(self):
        if self.websocket:
            self.session = await self.session.__aenter__()
        return self

    async def __aexit__(self, *args, **kwargs):
        if self.websocket:
            await self.session.__aexit__(*args, **kwargs)

    async def _call(self, method, *args):
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

        if self.websocket:
            result = await self.session.call(
                method,
                {i: k for i, k in enumerate(args)},
                timeout=self.WS_RESPONSE_TIMEOUT)
            return result.result

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

    async def _call_and_subscribe(self, callback, kwargs, decoder, method,
                                  *args):
        if self.websocket:
            callback_obj = Callback(callback, kwargs, decoder)
            self.callbacks[method] = callback_obj
            subscription = await self._call(method, *args)
            self.subscriptions[method] = subscription
        else:
            raise InternalErrorException(
                "Protocol {} doesn't support RPC subscription".format(
                    self.scheme))

    async def accounts(self):
        """
        Returns a list of addresses owned by client.

        :return: List of Accounts owned by the client.
        :rtype: list of (str)
        """
        result = await self._call("listAccounts")
        return result['data'] if result is not None else []

    async def batch_number(self):
        """
        Returns the batch number.

        :return: The current batch number the client is on.
        :rtype: int
        """
        return (await self._call("getBatchNumber"))['data']

    async def block_number(self):
        """
        Returns the height of most( recent block.)['data']

        :return: The current block height the client is on.
        :rtype: int
        """
        return (await self._call("getBlockNumber"))['data']

    async def consensus(self):
        """
        Returns information on the current consensus state.

        :return: Consensus state. "established" is the value for a good state,
            other values indicate bad.
        :rtype: bool
        """
        return (await self._call("isConsensusEstablished"))['data']

    async def create_account(self, passphrase=None):
        """
        Creates a new account and stores its private key in the client store.

        :param passphrase: Private Key passphrase to add to the account.
        :type passphrase: str
        :return: Information on the wallet that was created using the command.
        :rtype: WalletAccount
        """
        result = await self._call("createAccount", passphrase)
        return WalletAccount(result['data'])

    async def epoch_number(self):
        """
        Returns the epoch number.

        :return: The current epoch number the client is on.
        :rtype: int
        """
        return (await self._call("getEpochNumber"))['data']

    async def get_account_by_address(self, address):
        """
        Returns details for the account of given address.

        :param address: Address to get account details.
        :type address: str
        :return: Details about the account. Returns the default empty basic
            account for non-existing accounts.
        :rtype: StateData[Account or VestingContract or HTLC]
        """
        result = await self._call("getAccountByAddress", address)
        account = Account.get_account(result['data'])
        state = BlockchainState(**result['metadata'])
        return StateData[Account](state, account)

    async def get_accounts(self):
        """
        Returns details for all of the the accounts in the accounts tree.

        :return: Details for all of the the accounts in the accounts tree.
        :rtype: StateData[list of (Account or VestingContract or HTLC)]
        """
        result = await self._call("getAccounts")
        accounts = [Account.get_account(account) for account in result['data']]
        state = BlockchainState(**result['metadata'])
        return StateData[list[Account]](state, accounts)

    async def get_active_validators(self):
        """
        Returns a dictionary with the set of the current active validators.

        :return: The current set of active validators using a dictionary with
            the validator address as key (str) and the balance as value (int).
        :rtype: StateData[List of (Validator)]

        """
        result = await self._call("getActiveValidators")
        validators = [Validator(**validator) for validator in result['data']]
        state = BlockchainState(**result['metadata'])
        return StateData[List[Validator]](state, validators)

    async def get_block_by_hash(self, hash, include_transactions=None):
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
        result = await self._call("getBlockByHash", hash, include_transactions)
        return Block.get_block(result['data']) if result is not None else None

    async def get_block_by_number(self, height, include_transactions=None):
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
        result = await self._call("getBlockByNumber", height,
                                  include_transactions)
        return Block(**result['data']) if result is not None else None

    async def get_block_transaction_count_by_hash(self, hash):
        """
        Returns the number of transactions in a block from a block matching
        the given block hash.

        :param hash: Hash of the block.
        :type hash: str
        :return: Number of transactions in the block found, or None, when no
            block was found.
        :rtype: int or None
        """
        result = await self._call("getBlockTransactionCountByHash", hash)
        return result['data']

    async def get_block_transaction_count_by_number(self, height):
        """
        Returns the number of transactions in a block matching the given block
        number.

        :param height: Height of the block.
        :type height: int
        :return: Number of transactions in the block found, or None, when no
            block was found.
        :rtype: int or None
        """
        result = await self._call("getBlockTransactionCountByNumber", height)
        return result['data']

    def get_callbacks(self):
        """
        Returns a dictionary containing all callbacks that the client can call
        when an RPC request is received.

        :return: Dictionary containing all RPC subscription IDs.
        :rtype: dict
        """
        return self.callbacks

    async def get_current_slashed_slots(self):
        """
        Returns the current slashed slots.

        :return: Current slashed slots.
        :rtype: StateData[SlashedSlots]
        """
        result = await self._call("getCurrentSlashedSlots")
        slashed_slots = SlashedSlots(**result['data'])
        state = BlockchainState(**result['metadata'])
        return StateData[SlashedSlots](state, slashed_slots)

    async def get_inherents_by_batch_number(self, batch_number):
        """
        Returns information about inherents by batch number.

        :param batch_number: Batch number for which the inherents are going to
            be gathered.
        :type batch_number: int
        :return: A list of inherent objects.
        :rtype: List of (Inherent)
        """
        result = await self._call(
            "getInherentsByBatchNumber", batch_number)
        if result is not None:
            return [Inherent(**inherent) for inherent in result['data']]
        else:
            return []

    async def get_inherents_by_block_number(self, height):
        """
        Returns information about inherents by block number.

        :param height: Height of the block containing the inherents.
        :type height: int
        :return: A list of inherent objects.
        :rtype: List of (Inherent)
        """
        result = await self._call(
            "getInherentsByBlockNumber", height)
        if result is not None:
            return [Inherent(**inherent) for inherent in result['data']]
        else:
            return []

    async def get_latest_block(self, include_body=None):
        """
        Returns information the latest block.

        :return: The latest block in the chain.
        :rtype: Block
        """
        result = await self._call("getLatestBlock", include_body)
        return Block.get_block(result['data'])

    async def get_parked_validators(self):
        """
        Returns the set of current parked validators.

        :return: Set of current parked validators.
        :rtype: ParkedValidators
        """
        result = await self._call("getParkedValidators")
        parked_validators = ParkedValidators(**result['data'])
        state = BlockchainState(**result['metadata'])
        return StateData[ParkedValidators](state, parked_validators)

    async def get_previous_slashed_slots(self):
        """
        Returns the previous slashed slots.

        :return: Previous slashed slots.
        :rtype: StateData[SlashedSlots]
        """
        result = await self._call("getPreviousSlashedSlots")
        slashed_slots = SlashedSlots(**result['data'])
        state = BlockchainState(**result['metasata'])
        return StateData[SlashedSlots](state, slashed_slots)

    async def get_slot_at(self, block_number, offset=None):
        """
        Returns the slot at a specific block number

        :param block_number: Block number for which the slot is queried.
        :type block_number: int
        :param offset: Optional block number offset.
        :type int, optional
        :return: The slot at the specified block number.
        :rtype: StateData[Slot]
        """
        result = await self._call("getSlotAt", block_number, offset)
        slot = Slot(**result['data'])
        state = BlockchainState(**result['metadata'])
        return StateData[Slot](state, slot)

    def get_subscriptions(self):
        """
        Returns a dictionary containing all RPC subscription IDs the client
        has subscribed to.

        :return: Dictionary containing all RPC subscription IDs.
        :rtype: dict
        """
        return self.subscriptions

    async def get_raw_transaction_info(self, transaction):
        """
        Deserializes hex-encoded transaction and returns a transaction object.

        :param transaction: The hex encoded signed transaction.
        :type transaction: str
        :return: The transaction object.
        :rtype: Transaction
        """
        result = await self._call("getRawTransactionInfo", transaction)
        return Transaction(**result['data'])

    async def get_staker_by_address(self, address):
        """
        Gets a staker using its address

        :param address: Address of the staker.
        :type address: str
        :return: The staker object.
        :rtype: StateData[Staker]
        """
        result = await self._call("getStakerByAddress", address)
        staker = Staker(**result['data'])
        state = BlockchainState(**result['metadata'])
        return StateData[Staker](state, staker)

    async def get_stakers_by_validator_address(self, address):
        """
        Gets the stakers for a validator given its address

        :param address: Address of the validator.
        :type address: str
        :return: The staker object.
        :rtype: StateData[list of (Staker)]
        """
        result = await self._call("getStakersByValidatorAddress", address)
        stakers = [Staker(**staker) for staker in result['data']]
        state = BlockchainState(**result['metadata'])
        return StateData[Staker](state, stakers)

    async def get_transactions_by_address(self, address,
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
        result = await self._call(
            "getTransactionsByAddress", address, number_of_transactions
        )
        return [Transaction(**tx) for tx in result['data']]

    async def get_transaction_hashes_by_address(self, address,
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
        result = await self._call(
            "getTransactionHashesByAddress", address,
            number_of_transactions)
        return result['data']

    async def get_transactions_by_batch_number(self, batch_number):
        """
        Returns information about transactions by batch number.

        :param batch_number: Batch number for which the transactions are going
            to be gathered.
        :type batch_number: int
        :return: A list of transaction objects.
        :rtype: List of (Transaction)
        """
        result = await self._call(
            "getTransactionsByBatchNumber", batch_number)
        if result is not None:
            return [Transaction(**tx) for tx in result['data']]
        else:
            return []

    async def get_transactions_by_block_number(self, height):
        """
        Returns information about transactions by block number.

        :param height: Height of the block containing the transactions.
        :type height: int
        :return: A list of transaction objects.
        :rtype: List of (Transaction)
        """
        result = await self._call(
            "getTransactionsByBlockNumber", height)
        if result is not None:
            return [Transaction(**tx) for tx in result['data']]
        else:
            return []

    async def get_transaction_by_hash(self, hash):
        """
        Returns the information about a transaction requested by transaction
        hash.

        :param hash: Hash of a transaction.
        :type hash: str
        :return: A transaction object or None when no transaction was found.
        :rtype: Transaction or None
        """
        result = await self._call("getTransactionByHash", hash)
        return Transaction(**result['data']) if result is not None else None

    async def get_validator_address(self):
        """
        Returns the address of the current validator.

        :return: Address of the current validator.
        :rtype: str or None
        """
        return (await self._call("getAddress"))['data']

    async def get_validator_by_address(self, address):
        """
        Returns a validator given its address

        :param address: Address for which a validator should be gathered.
        :type address: str
        :param include_stakers: Set to true to include stakers in the
            Validator object to be returned.
        :return: Validator for the corresponding address
        :rtype: StateData[Validator]
        """
        result = None
        result = await self._call(
            "getValidatorByAddress", address)
        if result is None:
            return None

        validator = Validator(**result['data'])
        state = BlockchainState(**result['metadata'])
        return StateData[Validator](state, validator)

    async def get_validators(self):
        """
        Returns a all validators in the staking contract

        :return: Validator for the corresponding address
        :rtype: StateData[List of (Validator)]
        """
        result = await self._call("getValidators")

        validators = [Validator(**validator) for validator in result['data']]
        state = BlockchainState(**result['metadata'])
        return StateData[list[Validator]](state, validators)

    async def get_validator_signing_key(self):
        """
        Returns the signing key of the current validator.

        :return: Signing key of the current validator.
        :rtype: str or None
        """
        return (await self._call("getSigningKey"))['data']

    async def get_validator_voting_key(self):
        """
        Returns the voting key of the current validator.

        :return: Voting key of the current validator.
        :rtype: str or None
        """
        return (await self._call("getVotingKey"))['data']

    async def importRawKey(self, private_key, passphrase=None):
        """
        Imports a raw key into the wallet.

        :param private_key: Private key to be imported.
        :type private_key: str
        :param passphrase: Optional passphrase to add to the private key.
        :type passphrase: str
        :return: Address of the imported raw key.
        :rtype: str
        """
        result = await self._call("importRawKey", private_key, passphrase)
        return result['data']

    async def is_account_imported(self, address):
        """
        Returns wether an account has been imported into the wallet.

        :param address: Address of the account that is going to be checked.
        :type address: str
        :return: Bool indicating wether the account has been imported.
        :rtype: bool
        """
        return (await self._call("isAccountImported", address))['data']

    async def is_account_unlocked(self, address):
        """
        Returns wether an account has been unlocked in the wallet.

        :param address: Address of the account that is going to be checked.
        :type address: str
        :return: Bool indicating wether the account has been unlocked.
        :rtype: bool
        """
        return (await self._call("isAccountUnlocked", address))['data']

    async def lock_account(self, address):
        """
        Locks an account in the wallet

        :param address: Address of the account to be locked.
        :type address: sre
        """
        await self._call("lockAccount", address)

    async def mempool(self):
        """
        Returns information on the current mempool situation. This will
        provide an overview of the number of transactions sorted into buckets
        based on their fee per byte (in smallest unit).

        :return: Mempool information.
        :rtype: MempoolInfo
        """
        result = await self._call("mempool")
        return MempoolInfo(**result['data'])

    async def mempool_content(self, include_transactions=None):
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
        result = await self._call("mempoolContent", include_transactions)
        return [tx if type(tx) is str else Transaction(**tx)
                for tx in result['data']]

    async def min_fee_per_byte(self):
        """
        Returns the minimum fee per byte.

        :return: The new minimum fee per byte.
        :rtype: int
        """
        return (await self._call("getMinFeePerByte"))['data']

    async def peer_count(self):
        """

        Returns number of peers currently connected to the client.

        :return: Number of connected peers.
        :rtype: int
        """
        return (await self._call("getPeerCount"))['data']

    async def peer_id(self):
        """
        Returns the peer ID of the running client.

        :return: Peer ID of the running client.
        :rtype: string
        """
        return (await self._call("getPeerId"))['data']

    async def peer_list(self):
        """
        Returns list of peers known to the client.

        :return: The list of peers.
        :rtype: list of(Peer)
        """
        result = await self._call("getPeerList")
        return [Peer(**peer) for peer in result['data']]

    async def peer_state(self, address):
        """
        Returns the state of the peer.

        :param address: The address of the peer.
        :type address: str
        :return: The current state of the peer.
        :rtype: Peer
        """
        result = await self._call("peerState", address)
        return Peer(**result['data'])

    async def set_peer_state(self, address, command=None):
        """
        Returns the state of the peer.

        :param address: The address of the peer.
        :type address: str
        :param command: The command to send.
        :type command: PeerStateCommand
        :return: The new state of the peer.
        :rtype: Peer
        """
        result = await self._call("peerState", address, command)
        return Peer(**result['data'])

    async def send_raw_transaction(self, transaction):
        """
        Sends a signed message call transaction or a contract creation, if the
        data field contains code.

        :param transaction: The hex encoded signed transaction
        :type transaction: str
        :return: The Hex-encoded transaction hash.
        :rtype: str
        """
        return (await self._call("sendRawTransaction", transaction))['data']

    async def send_basic_transaction(self, address, recipient, value, fee,
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
            transaction. Could be a string containing a block number
            (e.g."1000") or an offset (e.g. "+10").
        :type validityStartHeight: str
        :return: The Hex-encoded transaction hash.
        :rtype: str
        """
        result = await self._call(
            "sendBasicTransaction", address, recipient, value, fee,
            validityStartHeight)
        return result['data']

    async def send_stake_transaction(self, address, staker, value, fee,
                                     validityStartHeight):
        """
        Creates and sends a stake transaction to add stake to an existing
        staker

        :param address: The sender address.
        :type address: str
        :param staker: The staker address.
        :type staker: str
        :param value: The value of the transaction.
        :type value: int
        :param fee: The fee of the transaction.
        :type fee: int
        :param validityStartHeight: The validity start height for the
            transaction. Could be a string containing a block number
            (e.g."1000") or an offset (e.g. "+10").
        :type validityStartHeight: str
        :return: The Hex-encoded transaction hash.
        :rtype: str
        """
        result = await self._call(
            "sendStakeTransaction", address, staker, value, fee,
            validityStartHeight)
        return result['data']

    async def send_set_active_stake_transaction(self, address, staker,
                                                new_active_balance, fee,
                                                validityStartHeight):
        """
        Creates and sends a set active stake transaction to set a new value
        for the active stake

        :param address: The sender address.
        :type address: str
        :param staker: The staker address.
        :type staker: str
        :param new_active_balance: The new value for the active stake
        :type new_active_balance: int
        :param fee: The fee of the transaction.
        :type fee: int
        :param validityStartHeight: The validity start height for the
            transaction. Could be a string containing a block number
            (e.g."1000") or an offset (e.g. "+10").
        :type validityStartHeight: str
        :return: The Hex-encoded transaction hash.
        :rtype: str
        """
        result = await self._call(
            "sendSetActiveStakeTransaction", address, staker,
            new_active_balance, fee, validityStartHeight)
        return result['data']

    async def create_retire_stake_transaction(self, address, staker,
                                              retire_stake, fee,
                                              validityStartHeight):
        """
        Creates (but do not send) a retire stake transaction

        :param address: The sender address.
        :type address: str
        :param staker: The staker address.
        :type staker: str
        :param retire_stake: The stake to be retired
        :type retire_stake: int
        :param fee: The fee of the transaction.
        :type fee: int
        :param validityStartHeight: The validity start height for the
            transaction. Could be a string containing a block number
            (e.g."1000") or an offset (e.g. "+10").
        :type validityStartHeight: str
        :return: The Hex-encoded transaction hash.
        :rtype: str
        """
        result = await self._call(
            "createRetireStakeTransaction", address, staker, retire_stake, fee,
            validityStartHeight)
        return result['data']

    async def create_remove_stake_transaction(self, address, recipient,
                                              value, fee, validityStartHeight):
        """
        Creates (but do not send) a remove stake transaction

        :param address: The sender address.
        :type address: str
        :param recipient: The recipient of the funds.
        :type recipient: str
        :param value: The value.
        :type value: int
        :param fee: The fee of the transaction.
        :type fee: int
        :param validityStartHeight: The validity start height for the
            transaction. Could be a string containing a block number
            (e.g."1000") or an offset (e.g. "+10").
        :type validityStartHeight: str
        :return: The Hex-encoded transaction hash.
        :rtype: str
        """
        result = await self._call(
            "createRemoveStakeTransaction", address, recipient, value, fee,
            validityStartHeight)
        return result['data']

    async def subscribe_for_head_block(
            self,
            callback: Callable[[Any, Block, Dict], Awaitable[None]],
            include_transactions=None,
            **kwargs):
        """
        Subscribes to blocks produced by the server and calls a callback on
        each of the block.

        :param callback: Callback to be called on each block.
        :type callback: Callable[[NimiqClient, Block, Dict], Awaitable[None]]
        :param kwargs: Callback extra arguments that will be passed when the
            callback is called
        :type kwargs: dict
        """
        def get_block_from_result(data: Dict):
            return Block.get_block(data['data'])
        await self._call_and_subscribe(callback,
                                       kwargs,
                                       get_block_from_result,
                                       "subscribeForHeadBlock",
                                       include_transactions)

    async def subscribe_for_head_block_hash(
            self,
            callback: Callable[[Any, str, Dict], Awaitable[None]],
            **kwargs):
        """
        Subscribes to blocks produced by the server and calls a callback on
        each of the hash of the block.

        :param callback: Callback to be called on each block.
        :type callback: Callable[[NimiqClient, str, Dict], Awaitable[None]]
        :param kwargs: Callback extra arguments that will be passed when the
            callback is called
        :type kwargs: dict
        """
        def get_hash_from_result(data: Dict):
            return data['data']
        await self._call_and_subscribe(callback, kwargs, get_hash_from_result,
                                       "subscribeForHeadBlockHash")

    async def subscribe_for_logs_by_addresses_and_types(
            self,
            addresses,
            log_types,
            callback: Callable[[Any, StateData, Dict], Awaitable[None]],
            **kwargs):
        """
        Subscribes to block logs by type and addresses produced by the server
        and calls a callback on each each of the logs.

        :param addresses: List of addresses to subscribe to.
        :type addresses: List of (str)
        :param log_types: List of log types to subscribe to.
        :type log_types: List of (str)
        :param callback: Callback to be called on each block log.
        :type callback: Callable[[NimiqClient, BlockLog, Dict],
            Awaitable[None]]
        :param kwargs: Callback extra arguments that will be passed when the
            callback is called
        :type kwargs: dict
        """
        def get_block_logs_from_result(data: Dict):
            block_log = BlockLog.get_block_log(data['data'])
            state = BlockchainState(**data['metadata'])
            return StateData[BlockLog](state, block_log)
        await self._call_and_subscribe(callback,
                                       kwargs,
                                       get_block_logs_from_result,
                                       "subscribeForLogsByAddressesAndTypes",
                                       addresses,
                                       log_types)

    async def subscribe_for_validator_election_by_address(
            self,
            address,
            callback: Callable[[Any, Validator, Dict], Awaitable[None]],
            **kwargs):
        """
        Subscribes to validator election events and calls a callback on each
        each of the validators received.

        :param address: Validator address to subscribe for.
        :type address: str
        :param callback: Callback to be called on each validator.
        :type callback: Callable[[Any, Validator, Dict], Awaitable[None]]
        :param kwargs: Callback extra arguments that will be passed when the
            callback is called
        :type kwargs: dict
        """
        def get_validator_from_result(data: Dict):
            validator = Validator(data['data'])
            state = BlockchainState(**data['metadata'])
            return StateData[Validator](state, validator)
        await self._call_and_subscribe(
            callback,
            kwargs,
            get_validator_from_result,
            "subscribeForValidatorElectionByAddress",
            address)

    async def unlock_account(self, address, passphrase=None, duration=None):
        """
        Unlocks a wallet account

        :param address: The account address.
        :type address: str
        :param passphrase: Optional passphrase if the accounts requires it.
        :type passphrase: str
        :param duration: Optional duration in which the account is unlocked.
        :type duration: int
        """
        await self._call("unlockAccount", address, passphrase, duration)
