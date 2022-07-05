import asyncio
import json
from fastapi_websocket_rpc import RpcMethodsBase
from fastapi_websocket_rpc.simplewebsocket import (JsonSerializingWebSocket,
                                                   SimpleWebSocket)
from fastapi_websocket_rpc.schemas import RpcResponse, RpcMessage, RpcRequest
from fastapi_websocket_rpc.rpc_methods import NoResponse

from .error_exception import RemoteErrorException

__all__ = ["NimiqRPCMethods", "NimiqSerializer"]


class NimiqSerializer(JsonSerializingWebSocket):
    """
    Nimiq Serializer for `RpcMessage`s of fastapi_websocket_rpc.

    :param websocket: Web socket as created by the RPC client.
    :type websocket: SimpleWebSocket
    """

    def __init__(self, websocket: SimpleWebSocket):
        self._websocket = websocket

    def _serialize(self, msg):
        """
        Serializes a message.

        :param msg: Message to serialize.
        :type msg: RpcMessage
        :return: Serialized message in JSON format.
        :rtype: str
        """
        if msg.request is not None:
            call_object = {
                "jsonrpc": "2.0",
                "method": msg.request.method,
                "params": list(msg.request.arguments.values()),
                "id": msg.request.call_id,
            }
            return json.dumps(call_object)
        else:
            return None

    def _deserialize(self, buffer):
        """
        Deserializes a JSON buffer.

        :param buffer: Message to serialize.
        :type buffer: str
        :return: Deserialized message in RpcMessage format.
        :rtype: RpcMessage
        """
        msg = json.loads(buffer)

        error = msg.get("error")
        if error is not None:
            raise RemoteErrorException(
                error.get("message") + ":" + error.get("data"),
                error.get("code"))

        if 'result' in msg:
            response = RpcResponse(result=msg['result'], call_id=msg['id'])
            return RpcMessage(response=response)
        elif 'method' in msg:
            request = RpcRequest(method=msg['method'], arguments=msg['params'])
            return RpcMessage(request=request)
        else:
            response = NoResponse
            return NoResponse

    async def send(self, msg):
        """
        Sends a message.

        :param msg: Message to serialize.
        :type msg: RpcMessage
        """
        await self._websocket.send(self._serialize(msg))

    async def recv(self):
        """
        Receives a message.

        :return: Deserialized message in RpcMessage format.
        :rtype: RpcMessage
        """
        msg = await self._websocket.recv()

        return self._deserialize(msg)

    async def close(self, code: int = 1000):
        """
        Closes the underlying websocket.

        :param code: Code to use for closing the websocket.
        :type code: int
        """
        await self._websocket.close(code)


class NimiqRPCMethods(RpcMethodsBase):
    """
    Defines RPC methods that the server can request.

    :param client: Nimiq API client.
    :type client: NimiqClient
    """

    def __init__(self, client):
        super().__init__()
        self.client = client

    """
    Nimiq Websocket RPC method for subscribing for new blocks

    :param subscription: Subscription ID as provided by the server.
    :type subscription: int
    :param result: Block hash as provided by the server.
    :type result: str
    """
    async def headSubscribe(self, subscription, result):
        callbacks = self.client.get_callbacks()
        subscriptions = self.client.get_subscriptions()
        if 'headSubscribe' in callbacks and 'headSubscribe' in subscriptions:
            if subscriptions['headSubscribe'] == subscription:
                asyncio.ensure_future(
                    callbacks['headSubscribe'](self.client, result))
        return NoResponse
