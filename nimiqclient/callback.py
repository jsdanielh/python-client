from typing import Any, Awaitable, Callable, Dict, Generic, Optional, TypeVar

__all__ = ["Callback"]

T = TypeVar("T")


class Callback(Generic[T]):
    """
    Callback to be used by the NimiqClient when calling a method that
    subscribes to specific events

    :param callback_function: Callback function to be called by the client
        when the subscribed event happens.
    :type Callable[[Any, T], Awaitable[None]]
    :param result_decoder: Function to be called when the result of an RPC
        call must be decoded before passing it to the callback
    :type Optional[Callable[[dict], T]]
    :param kwargs: Function arguments to be sent to the callback when called.
    :type kwargs: dict
    """

    def __init__(self,
                 callback_function: Callable[[Any, T, Dict], Awaitable[None]],
                 kwargs: Dict,
                 result_decoder=Optional[Callable[[Dict], T]]):
        self.callback = callback_function
        self.result_decoder = result_decoder
        self.kwargs = kwargs

    async def call(self, client: Any, result: Dict):
        """
        Calls a callback with the appropriate arguments

        :param client: Nimiq client to be passed to the callback.
        :type client: NimiqClient
        :param result: Result of the RPC call done by the NimiqClient
        :type result: int or str or dict
        """
        if self.result_decoder is not None:
            result = self.result_decoder(result)
        await self.callback(client, result, self.kwargs)
