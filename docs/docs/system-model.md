

# System Model

The Ststem Model sits at the heart of a Greenglass host implementation. It contains the description of how the parts of the system are wired together, whilst allowing each component of the system to know only about their own local context e.g.

- Control Processes know only about variables.
- The Sparkplug component knows only about nodes and metrics.
- The LwM2M component knows only about objects.

The model contains both simple static configuration like host names, and a set of Python dictionaries with a corresponding API  that allow different components to "find" variables using their local contexts.

```
self.variables : dict [ VarDescr, Variable ] = {}
self.variables_to_metrics : dict [ VarDescr, MetricDescr ] = {}
self.metrics_to_variables : dict [ MetricDescr, VarDescr ] = {}
self.output_metrics : set [ MetricDescr] = set()
self.node_input_metrics : dict [ str, set[MetricDescr] ] = {}
self.node_output_metrics : dict [ str, set[MetricDescr] ] = {}
self.metric_types  : dict [ (str, str), MetricDataType] = {}
self.processes = set()
self.node_id_map = NodeIdMap()
self.broker_url = None
self.host_id = None
self.group_id = None
self.micro_services_port = None
```

## Configuration

The System model contains the following static configuration:

| **Name**            | **Description**                    | **Default**  |
| ------------------- | ---------------------------------- | ------------ |
| broker_url          | MQ/TT broker url ('hostname:port') | "localhost"  |
| host_id             | Sparkplug host-id                  | "greenglass" |
| group_id            | Sparkplug group-id                 | "greenglass" |
| micro_services_port | REST Micro-services port number    | 8080         |









Variables

```python
def new_variable(self, variable : VarDescr):
```

