# ******************************************************************************
#  Copyright 2024 Greenglass Project
#
#  Use of this source code is governed by an MIT-style
#  license that can be found in the LICENSE file or at
#  https://opensource.org/licenses/MIT.
#
# *****************************************************************************/
import asyncio
import aiomqtt
import logging

from aioreactive import AsyncAnonymousObserver
from system_model import Value
from src.tahu.sparkplug_b_pb2 import Payload
from tahu.sparkplug_b import addMetric

class Sparkplug :
    def __init__(self, system_model) :

        self.url = system_model.broker_url
        self.group_id = system_model.group_id
        self.host_id = system_model.host_id

        self.system_model = system_model
        self.client = None

    async def run(self) :
        logging.info("Sparkplug starting...")

        interval = 5  # Seconds
        while True:
            try:
                self.client = aiomqtt.Client(self.url)
                logging.info("MQ/TT connected")

                async with (self.client):

                    # Connected
                    # Set up listeners for the outgoing metrics
                    for metric in self.system_model.output_metrics:
                         await asyncio.create_task(self.output_metric_observer(metric))

                    # Subscribe to all incoming messages from all nodes
                    await self.client.subscribe("spBv1.0/" + self.group_id + "/#")
                    async for message in self.client.messages:

                        # Split the received topic
                        # part[2] = command
                        # part[3] = node_id

                        topic_parts = message.topic.split('/')
                        command = topic_parts[2]
                        node_id = topic_parts[3]

                        # look up the node_name using the node_id
                        # ignore the message if no node_name is found

                        node_name = self.system_model.get_name_for_id(node_id)
                        if node_name is not None :

                            # Parse the message payload to create the Sparkplug payloa
                            payload = Payload()
                            payload.ParseFromString(message.payload)

                            if command == "NBIRTH" :

                                # Handle an NDATA payload
                                # For each metric in the payload look for
                                # a corresponding observable. If one is found
                                # set its value using the metric's value and timestamp

                                for metric in payload.metrics :
                                    print(metric.name)
                                    observable = self.system_model.get_input_metric_observable(node_name, metric.name)
                                    if observable is not None :
                                        await observable.set_value(Value(metric.value, metric.timestamp))

                            elif command == "NDEATH" :

                                # Handle an NDEATH payload
                                # Lookup the metrics for this node and set the
                                # Corresponding Variable values to None

                                metrics = self.system_model.input_metrics_for_node(node_name)
                                for metric in metrics :
                                    variable = self.system_model.variable_for_metric(node_name, metric.name)
                                    if variable is not None :
                                        await variable.set_value(Value(None, metric.timestamp))

                            elif command == "NDATA" :

                                # Handle a NDATA payload
                                # For each metric in the payload look for
                                # a corresponding observable. If one is found
                                # set its value using the metric's value and timestamp

                                for metric in payload.metrics :
                                    print(metric.name)
                                    variable = self.system_model.variable_for_metric(node_name, metric.name)
                                    if variable is not None :
                                        await variable.set_value(Value(metric.value, metric.timestamp))

            except aiomqtt.MqttError:
                logging.warn(f"No connection; Trying again in {interval} seconds ...")
                await asyncio.sleep(interval)

    # output_metric_observer()
    # Am AsyncAnonymousObserver for observing the variable corresponding
    # to the given none_name/metric_name
    # if there is an active mq/tt connection the observer function send_message()
    # will create and send an NDATA using the value received from the Variable
    async def output_metric_observer(self, metric) :
        logging.info(f"Starting observer on node={metric.node_name} metric={metric.metric_name}")

        async def send_message(value : Value):
            node_id = self.system_model.node_id_map.get_id_for_name(metric.node_name)
            if self.client is not None and node_id is not None:
                payload = Payload()
                addMetric(payload, metric.metric_name, None, metric.data_type, value.value, value.timestamp)
                topic = "spBv1.0/" + self.group_id + "/NCMD/" + node_id
                self.client.publish(topic, payload.SerializeToString())

        variable = self.system_model.variable_for_metric(metric)
        if variable is not None :
            await variable.subscribe_async(AsyncAnonymousObserver(send_message))


