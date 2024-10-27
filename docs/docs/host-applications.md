---


layout: default
title: Host Application
description:  The concept and implementation of Host Applications
page_nav:
    prev:
        content: Edge Nodes
        url: '/docs/edge-nodes'
    next:
        content: Control Concepts
        url: '/docs/control-concepts'
---

## Introduction

The Host Application provides the control and monitoring functionality of the system. It listens to the values from the sensors mananaged by the Edge Nodes, applies control algorithms to generate outputs and  sends them  to actuators managed by the Edge Nodes.

Since evey use-case will be different the Greenglass Does not provide a complete application. Rather is provides the **Host Application Framwork** that provides core functionality for configuration and creating control algorithms. In this way only the use-case specific functionality has to be developed.

A Host application can be split into 3 parts:

- Protocol handler(s)
- **The System Model**
- Control processes



![host](/docs/images/host.png)

## The Host Application Framework (HAF)

### Asynchronous Programming

The Host Application Framework uses Asynchronous Programming. Techniques.  This makes the application fully event driven and very efficient, and  allows the application to be very modular by splitting it into a set of cooperating tasks. 

The asynchronous programming capability is provided by 2 Python libraries :

- [Asyncio ](https://docs.python.org/3/library/asyncio.html) - "a library to write **concurrent** code using the **async/await** syntax. asyncio is used as a foundation for multiple Python asynchronous frameworks that provide high-performance network and web-servers, database connection libraries, distributed task queues, etc."
-  [Aioreactive](https://github.com/dbrattli/aioreactive/tree/master/aioreactive)  - " [ReactiveX](https://reactivex.io) for asyncio. It's an asynchronous and reactive Python library for asyncio using async and await."

ReactiveX is "an API for asynchronous programming with observable streams". They HAF uses Reactive Streams to pass data between tasks.  These streams implement the Variables of a Process Control model (see xxxxxx).

Variables are ReactiveX observables which publish their underlying value whenever it changes, One or more observers can subscribe to the variable and receive notifications when it changes value.

![variable](/docs/images/variable.png)

### The System Model

#### Introduction

The System Model defines the structure of the system in terms of the Variables and provides a mechanism for different parts of the system to access them. It does tis by  allowing variables to be referenced using different key information for example : process-id and variable-id for control process, and node-name and metric-name for sparkplug metrics. This allows each part of the system to operate in its own domain  with the Congtrol Model binding everything together.

This diagram shows how a control process can be linked to Sparkplug metrics via a set of variables.

![basic-model](/docs/images/basic-model.png)

The System model is used in two phases:

- Constructing the configuration.
- Running the configured system.

#### Variable Mapping

Access to variables is provided using multiple keys:

**Variable** Key - the primary key

```python
key = VariableKey(process_id,variable_id)
```

**Metric** Key - for Sparkplug metrics

```python
key = MetricKey(node_name, metric_name, data_type)
```

**Object Key** - for LwM2M Objects

```
key = ObjectKey(object_id, object_instance, resource_id)
```

A variable always has a variable-key, optionally there can be a metric-key, or an object-key allowing the varable to be accessed from the Sparkplug or LwM2M protocol handlers.

![mapping](/docs/images/mapping.png)

#### Configuring Variables

The System Model API to configure variables is:

`new_variable()` - Create a new variable with its primary key.

```python
model.new_variable(variable_key)
```

`link_variable_to_metric()`  - Link a variable to a metric using their keys. This is for output variables/metrics

```python
model.link_variable_to_metric(variable_key, metric_key)
```

`link_metric_to_variable()` - Link a metric to a variable using their keys. This is for input variables/metrics

```python
variable = model.variable_for_metric(metric_key)
```

`link_variable_to_object()` - Link a variable to an object using their keys. This is for output variables/objects

```python
model.link_variable_to_object(variable_key, object_key)
```

`link_object_to_variable()` - Link a objectto a variable using their keys. This is for input variables/objects

```python
model.link_object_to_variable(object_key, variable_key)
```



#### Creating a System Model

The  base class for all system models is `SystemModel`. This contains 2 abstract methods `configure()` and `run()` as follows:

```python
class SystemModel(ABC) :
	  @abstractmethod
    def configure(self):
        pass

    @abstractmethod
    def run(self):
        pass
```

As its name suggests `configure()` is used to set up the variable structure:

Consider this simple example, a system that controls the temperature of something. It's input is the temperature, and the output turns a heater on and off.

![example](/docs/images/example.png)

The `configure()` function of the `SystemModel` for this would look lsomething like this:

```python
CONTROL_TEMPERATURE_VAR = VariableKey("CONTROL", "TEMPERATURE")
CONTROL_HEATER_VAR = VariableKey("CONTROL", "HEATER")

TEMPERATURE_METRIC = MetricKey("CONTROLLER", "/Controller/Temperature", MetricDataType.Double)
HEATER_METRIC = MetricKey("CONTROLLER", "/Controller/Heater", MetricDataType.Boolean)

class MySystemModel(SystemModel) :
	
    def configure(self):
        # Create the input variable and link it to the metric
        self.new_variable( variable = CONTROL_TEMPERATURE_VAR )
        self.link_metric_to_variable( 
            metric = TEMPERATURE_METRIC, 
            variable = CONTROL_TEMPERATURE_VAR
        )

    		# Create the output variable and link it to the metric
        self.new_variable( variable = CONTROL_HEATER_VAR )
        self.link_variable_to_metric(
            variable = CONTROL_HEATER_VAR, 
            metric = HEATER_METRIC 
        )
        
    def run(self):
      # Run the tasks
				
```

### Control Processes

A Contol Process listens on one or more variable and, when the values change, runs some control algorithm that generates one or more output values  that are used modify the state of the system under control.

The algorithm can be very simple e.g. an output value is a  simple function  of an input variable, or complex e.g the process uses fuzzy logic to generate multiple outputs from multiple 

The  base class for all control processes is `ControlProcess`. This has access to the system model to get acccess to its variables.

The class has one abstract function `run()`  which connects to the variables and runs the control algorithm. 

This function should be run as a task and never exit.

```python
class ControlProcess(ABC):
    """Base class for Process implementations """

    def __init__(self, model):
        self.name = self.__class__.__name__
        self.model = model

    @abstractmethod
    async def run(self) -> None:
        """Run the process"""
        pass
```



The control  process for the above example would be something like this:

```python
from simple_pid import PID

class Control(ControlProcess) :
  
    p = 1
    i = 0.1
    d = 0.06
    set_point = 25.0
    
    def __init__(self, model):
        super().__init__(model)
        self.pid = PID(p, i, d, setpoint = set_point)
     
    # Run the pid and publish the result
    async def event(value) :
        await self.model.variable(CONTROL_HEATER_VAR).set_value(self.pid(v))
    
    # Listen to the temperature value
    async def run(self) -> None:
        await self.model.variable(CONTROL_TEMPERATURE_VAR).subscribe_async(
           AsyncAnonymousObserver(event)
        )

```
