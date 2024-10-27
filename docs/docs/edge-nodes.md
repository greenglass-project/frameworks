---
layout: default
title: Edge Nodes
description:  The concept and implementation of Edge Nodes
page_nav:
    prev:
        content: Building Blocks
        url: '/docs/building-blocks'
    next:
        content: Host Applications
        url: '/docs/host-applications'
---

## Introduction





## Supported Hardware

The Edge-Node software requires the MicroPython runtime with Greenglass extensions written in C. Ultimately it should be possible to support any platform on which MicroPyhon runs, however initially only two will be supported:

- Raspberry Pi Pico
- Espressif ESP32

Both are very low cost and widely used microcontroller platforms. There are many commerical products based around these, and there is a lot of MicroPython interface software available for a wide range of I/O use cases. Commerical products can be reflashed with Greenglass firmware, or custom hadrware can be created using off-the shelf controller boards and flashed with the Greenglass software.

### Rasberry Pi Pico

![pico](/docs/images/pico.png)

The [Raspberry Pi Pico ](https://www.raspberrypi.com/products/raspberry-pi-pico/) is the smallest board in the Raspberry Pi range of computer boards. It is a controller board with a range of I/O options including Digital I/O, Analogue in, SPI, I2C and serial. Uniquely, the Pico also has a number of PIO processors. These are tiny programmable processors that are independent of the  main processor and capablle of handling 4 state machines.  Each state machine can control one I/O pin. These PIO controllers and their state machines can implement a variety of protocols without using the board's main processor. They are programmable from MicroPython. 

The rp2040 has 2  and the rp2350 has 3.

- rp2040 W  - ARM Dual core 240MHz. WiFi and Bluetooth 5.0 
- rp2350 W - not yet available 

The Pi Pico controller board is priced from $4.

### Espressif ESP32

![](/docs/images/esp32.png)

The ESP32 series of microcontrollers is manufactured by  [Espressif](https://www.espressif.com).  Like the Pi Pico they support a range of I/O options including Digital I/O, Analogue in, SPI, I2C and serial. Unlike the Pi Pico, ESP32 devices do not have separate PIO Controllers.

The ESP32 range includes many different boards, but currently the following 5 boards are supported by MicroPython and Greenglass.

- esp32 - ARM Dual core 240MHz. WiFi and Bluetooth 4.2
- esp32c3 - Risc-V Single core 160MHz. WiFi and Bluetooth 5.0
- esp32c6 -  Risc-V Single core 160MHz. WiFi 6   Bluetooth 5.3 and Thread
- esp32s2 - ARM Single core 240MHz. WiFi only
- esp32s3 - ARM Dual core 240MHz. WiFi and Bluetooth 5.0

ESP32 boards are also priced from $4.



## Eclipse Sparkplug Node

### Sparkplug API

The Sparkplug API is a MicroPython extension written in C and based on the  [Eclipse Tahu](https://github.com/eclipse/tahu) Spakplug C implemenration. This uses NanoPB - a Protocol Buffers library optimised for targets with constrained memory, like microcontrollers.

This exposes a very simple Python API that allows Sparkplug Payloads to be created from a set of Metrics, and then serialized for transmission; and incoming payloads to be decoded and their constituent Metrics to be read.

It contains 3 classes

- PayloadIn

- PayloadOut

- Metric

  

#### PayloadIn

PayloadIn is a micro-python wrapper for a C org_eclipse_tahu_protobuf_Payload` object.
It is constructed from the raw `bytebuffer` received from MQ/TT., and exposes the following attributes:

- seq 
- timestamp
- uuid
- metric_count

The metrics are accessible by calling `metric(n)` which will return the nth metric. (or a `ValueException` if it is out of range).

Example:
```python
>>> payload_in = PayloadIn(buffer) 
>>> print(payload_in.seq)
>>> print(payload_in.timestamp)
>>> print(payload_in.uuid)
>>> print(payload_in.metric_count)
>>> metric_0 = payload_in.metric(0)
```


#### PayloadOut

PayloadOut is a micro-python wrapper for a  C `org_eclipse_tahu_protobuf_Payload` object that can be constructed and sent to MQ/TT.

It is constructed from the following parameters.
- seq 
- timestamp
- uuid

Metrics can be added to the payload using the `add_metric(Metric)` function.

The payload can be encoded into a `bytebuffer` which can be sent to MQ/TT,  using the `to_bytes()` function.

Example:
```python
>>> payload _out = PayloadOut(0,"uuid", 1775435677)
>>> payload_out.add_metric(metric1)
>>> byte_buffer = payload_out.to_bytes()
```

#### Metric

A MicroPython wrapper for a  C `org_eclipse_tahu_protobuf_Payload_Metric` object. It is used by both `PayloadIn` and `PayloadOut`.

A Metric has the following attributes:
- name
- type
- value
- timestamp

The attributes must be supplied when a Metric is constructed

`metric = Metric(name, type, value, timestamp)`

and they are available as read-only attributes

Examples :

Incoming :
```python
>>> payload_in = PayloadIn(buffer)
>>> 
>>> metric_0 = payload_in.metric(0)
>>> print(metric_0.name)
>>> print(metric_0.type)
>>> print(metric_0.value)
>>> print(metric_0.timestamp)
```

Outgoing :
```python
>>> payload _out = PayloadOut(0,"uuid", 1775435677)
>>>
>>> metric = Metric("/sensors/tempature", Metric.METRIC_DATA_TYPE_DOUBLE, 27.3)
>>> 
>>> payload_out.add_metric(metric1)

```



