---
layout: default
title: Variables
description:  Variables are ReactiveX Observable implementation for passing values
page_nav:
    prev:
        content: Previous page
        url: '#'
    next:
        content: Next page
        url: '#'
---

# Observables

The Greenglass Host Framework adopts an asynchronous programming paradigm, which uses 

-  [asyncio](https://docs.python.org/3/library/asyncio.html) - to provide concurrent task handling
- [aoireactive](https://github.com/dbrattli/aioreactive) - to provide asynchronous observable streams accorting to the [ReactiveX API ](https://reactivex.io) .

> **Observable** 
>
> In ReactiveX an observer subscribes to an Observable. Then that observer reacts to whatever item or sequence of items the Observable emits. This pattern facilitates concurrent operations because it does not need to block while waiting for the Observable to emit objects, but instead it creates a sentry in the form of an observer that stands ready to react appropriately at whatever future time the Observable does so.
>
> https://reactivex.io/documentation/observable.html 

The principal event mechanism used  by the framework is the **Variable**  - a ReactiveX Observable implementation with the following characteristics :

- It is "hot" - this means it will start emitting events as soon as it is started, irrespective of whether it has any observers.
- It supports multiple observers
- It is stateful. It retains its latest value, which can be read without observing the Variable. This value is also published when an obsever subscribes to the variable.

# The Variable API

The Variable has a very simple API:

```python
class Variable(AsyncObservable[Value], ABC) :

    def __init__(self, process_id, variable_id):
   
    async def subscribe_async(self, observer) -> ObservableValueSubscription:
    
    async def set_value(self, value):

```

Variables are identified by their owning process and a variable identifier scoped by the process:

```
variable = Variable(process_id, variable_id)
```

An Observer can subscribe to the variable as follows;

```
variable.subscribe_async(observer)
```

The observer can be an object from a class that implements the AsyncObserver interface, or in the simplest case an AsyncAnonymousObserver - like this

```python
async def handler(value : Value):
  print("Value received\n")

variable.subscribe_async(AsyncAnonymousObserver(handler))
```

To set the variable's value :

```python
variable.set_value(value)
```

All subscribed observers will receive the value.

