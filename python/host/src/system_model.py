# ******************************************************************************
#  Copyright 2024 Greenglass Project
#
#  Use of this source code is governed by an MIT-style
#  license that can be found in the LICENSE file or at
#  https://opensource.org/licenses/MIT.
#
# *****************************************************************************/
from abc import ABC, abstractmethod

from tahu.sparkplug_b import MetricDataType
from aioreactive import AsyncObservable
from expression.system import AsyncDisposable
from time import time
from bidict import bidict

class VarDescr :
    def __init__(self, process_id,variable_id):
        self.process_id = process_id
        self.variable_id = variable_id

    def __eq__(self, other):
        return self.process_id == other.process_id and self.variable_id == other.variable_id

    def __hash__(self):
        return hash((self.process_id, self.variable_id))

class MetricDescr:
    def __init__(self, node_name, metric_name, data_type):
        self.node_name = node_name
        self.metric_name = metric_name
        self.data_type = data_type

    def __eq__(self, other):
        return ( self.node_name == other.node_name and
                self.metric_name == other.metric_name
                and self.data_type == other.data_type )

    def __hash__(self):
        return hash((self.node_name, self.metric_name, self.data_type))

class NodeDescr :
    def __init__(self, node_name, node_id) :
        self.node_name = node_name
        self.node_id = node_id

class NodeIdMap :
    def __init__(self) :
        self.node_map = bidict()

    def add_node(self, node_descr) :
        self.node_map[node_descr.node_name] = node_descr.node_id

    def get_id_for_name(self, node_name) :
        return self.node_map[node_name]

    def get_name_for_id(self, node_id) :
        return self.node_map.inverse[node_id]

    def node_ids(self):
        return self.node_map.inverse.keys()

class Value:
    def __init__(self, value,  timestamp =int(time())) :
        self.timestamp = timestamp
        self.value = value

#---------------------------------------------------------------------
# ObservableValueSubscription
# ---------------------------------------------------------------------
class  ObservableValueSubscription(AsyncDisposable, ABC) :

    def __init__(self, observable_value, observer):
        super().__init__()
        self.observable_value = observable_value
        self.observer = observer

    def dispose_async(self) -> None:
        self.observable_value.unsubscribe(self.observer)

# ---------------------------------------------------------------------
# KeyedObservableValue
# ---------------------------------------------------------------------
class Variable(AsyncObservable[Value], ABC) :

    def __init__(self, process_id, variable_id):
        self.subscribers = {}
        self.process_id  = process_id
        self.variable_id  = variable_id
        self.current_value = None


    def unsubscribe(self, observer):
        del self.subscribers[observer]

    async def subscribe_async(self, observer) -> ObservableValueSubscription:
        subscr =  ObservableValueSubscription(self, observer)
        self.subscribers[observer] = subscr
        if self.current_value is not None:
            keyed_value = Value(self.current_value)
            await observer.observer.asend(keyed_value)
        return subscr


    async def set_value(self, value):
        self.current_value = value
        for subscriber in self.subscribers.values():
            await subscriber.observer.asend(value)


class SystemModel(ABC) :
    def __init__(self) :
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


    # Create a variable
    def new_variable(self, variable : VarDescr):

        v = Variable(variable.process_id, variable.variable_id)
        self.variables[variable] = v

    def variable(self, variable : VarDescr) -> Variable:
        return self.variables.get(variable)

    def link_variable_to_metric(self, variable : VarDescr, metric : MetricDescr):
        self.variables_to_metrics[variable] = metric

        metrics = self.node_output_metrics.get(metric.node_name)
        if metrics is None :
            metrics = set()
            self.node_output_metrics[metric.node_name] = metrics
        metrics.add(metric)

        self.output_metrics.add(metric)

    def link_metric_to_variable(self, metric : MetricDescr, variable :  VarDescr , ):

        self.metrics_to_variables[metric] = variable

        metrics = self.node_input_metrics.get(metric.node_name)
        if metrics is None :
            metrics = set()
            self.node_input_metrics[metric.node_name] = metrics
        metrics.add(metric)

    def variable_for_metric(self, metric_descr) -> [Variable, None] :
        var = self.metrics_to_variables.get(metric_descr)
        if var is not None :
            return self.variables[var]
        return None

    def input_metrics_for_node(self, node_name) -> [set[(str,str)], None] :
        return self.node_input_metrics.get(node_name)

    @abstractmethod
    def initialise(selfself):
        pass




class ControlProcess(ABC):
    """Base class for Process implementations """

    def __init__(self, model):
        self.name = self.__class__.__name__
        self.model = model

    @abstractmethod
    async def run(self) -> None:
        """Run the process"""
        pass
