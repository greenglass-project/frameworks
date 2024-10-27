from typing import Callable
from asyncio import Future, iscoroutinefunction


class Value:
    def __init__(self, value,  timestamp = int(time()*1000)) :
        self.value = value
        self.timestamp = timestamp

    def __eq__(self, other):
        self.timestamp = other.timestamp
        self.value = other.value

class MetricVariable :

    def __init__(self, metric_name : str):
        self.subscribers = set()
        self.netric_name = metric_name
        self.current_value : [Value, None] = None

    def unsubscribe(self, observer):
        del self.subscribers[observer]

    async def subscribe_async(self, observer) :
        self.subscribers.append(observer)
        if self.current_value is not None:
            keyed_value = Value(self.current_value)
            await observer.observer.asend(keyed_value)


    async def set_value(self, value):
        self.current_value = value
        for subscriber in self.subscribers:
            await subscriber.observer.asend(value)


class ObjectVariable :

    def __init__(self, object_id : int, object_instance : int, resource_id : int):
        self.subscribers = set()
        self.object_id = object_id
        self.object_instance = object_instance
        self.resource_id = resource_id
        self.current_value : [Value, None] = None

    def unsubscribe(self, observer):
        del self.subscribers[observer]

    async def subscribe_async(self, observer) :
        self.subscribers.append(observer)
        if self.current_value is not None:
            keyed_value = Value(self.current_value)
            await observer.observer.asend(keyed_value)


    async def set_value(self, value):
        self.current_value = value
        for subscriber in self.subscribers:
            await subscriber.observer.asend(value)


class AsyncObserver:
    """An anonymous AsyncObserver.

    Creates as sink where the implementation is provided by three
    optional and anonymous functions, asend, athrow and aclose. Used for
    listening to a source.
    """

    def __init__(self, asend, athrow, aclose) :
        super().__init__()
        self._asend = asend
        assert iscoroutinefunction(self._asend)

        self._athrow = athrow
        assert iscoroutinefunction(self._athrow)

        self._aclose = aclose
        assert iscoroutinefunction(self._aclose)

    async def asend(self, value: Value) -> None:
        await self._asend(value)

    async def athrow(self, error: Exception) -> None:
        await self._athrow(error)

    async def aclose(self) -> None:
        await self._aclose()
