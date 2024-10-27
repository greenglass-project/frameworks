---
layout: default
title: Data Types
description:  Variables are a ReactiveX Observable implementation for passing values

page_nav:
    prev:
        content: Previous page
        url: '#'
    next:
        content: Next page
        url: '#'
---

# Variable Descriptor (VarDescr)

Used to identify a Variable in terms of its process_id and variable_id.

It implements `__eq__()` and `__hash__()` so it can  be used as the key in a Python `dict` object.

```python
descr = VarDescr( process_id,variable_id )

p = descr.process_id
v = descr.variable_id

lookup = {}
lookup[descr] = ....
```

| Parameter   | Description         | Type   |
| ----------- | ------------------- | ------ |
| process_id  | Process identifier  | String |
| variable_id | Variable identifier | String |



# Metric Descriptor (MetricDescr)

Used to identify a Metric in terms of its node_name and metric_name. and its data type. 

It implements `__eq__()` and `__hash__()` so it can  be used as the key in a Python `dict` object.

```python
descr = MetricDescr( node_name, metric_name, data_type )

n = descr.node_name
m = descr.metric_name
d = descr.data_type

lookup = {}
lookup[descr] = ....
```

| Parameter   | Description                      | Type           |
| ----------- | -------------------------------- | -------------- |
| node_name   | The node's name                  | String         |
| metric_name | The metric's same                | String         |
| data_type   | The metric's Sparkplug data type | MetricDataType |



# Node Descriptor  (NodeDescr)

Assignment of a node_id to a node_name

```python
descr = NodeDescr( node_name, node_id )

n_name = descr.node_name
n_id = described.node_id
```

| Parameter | Description                  | Type   |
| --------- | ---------------------------- | ------ |
| node_name | The node's symbolic name     | String |
| node_id   | The node's actual identifier | String |



# Value

Value in the underlying data class used in Variables.  It simply comprises a Python simple type plus a timestamp indicating when the value was created.

When creating a variable the timestamp is is optional, and if it is not supplied the current timestamp is used 

```python
v1 = Value(simple_type)
v2 = Value(simple_type, timestamp = timestamp)

v = v1.value
t = v2.timestamp
```



| Parameter | Description              | Type                                  |
| --------- | ------------------------ | ------------------------------------- |
| timestamp | Milliseconds since epoch | int                                   |
| value     | The value                | Simple type: int, float, boolean, str |

