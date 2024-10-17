from abc import ABC
import asyncio

from sparkplug import Sparkplug
from src.system_model import VarDescr, MetricDescr, NodeDescr
from system_model import SystemModel, ControlProcess, Value
from tahu.sparkplug_b import MetricDataType
import logging

SYSTEM_TANK_VOLUME_VAR            = VarDescr("#SYSTEM", "TANK_VOLUME")
CIRCULATION_PUMP_STATE_VAR        = VarDescr("CIRCULATION_PUMP", "STATE")
CIRCULATION_PUMP_PUMP_VAR         = VarDescr("CIRCULATION_PUMP", "PUMP")
LIGHTING_STATE_VAR                = VarDescr("LIGHTING", "STATE")
LIGHTING_LIGHTS_VAR               = VarDescr("LIGHTING", "LIGHTS")
STATE_MANAGEMENT_PH_VAR           = VarDescr("STATE_MANAGEMENT", "PH")
STATE_MANAGEMENT_PH_SET_POINT_VAR = VarDescr("STATE_MANAGEMENT", "PH_SET_POINT")
STATE_MANAGEMENT_EC_VAR           = VarDescr("STATE_MANAGEMENT", "EC")
STATE_MANAGEMENT_EC_SET_POINT_VAR = VarDescr("STATE_MANAGEMENT", "EC_SET_POINT")
STATE_MANAGEMENT_PH_UP_VAR        = VarDescr("STATE_MANAGEMENT", "PH_UP")
STATE_MANAGEMENT_PH_DOWN_VAR      = VarDescr("STATE_MANAGEMENT", "PH_DOWN")
STATE_MANAGEMENT_EC_UP_VAR        = VarDescr("STATE_MANAGEMENT", "EC_UP")
STATE_MANAGEMENT_EC_DOWN_VAR      = VarDescr("STATE_MANAGEMENT", "EC_DOWN")

THREE_RELAYS_NODE = "3_RELAYS"
SENSORS_NODE      = "SENSORS"
DOSING_PUMPS_NODE = "DOSING_PUMPS"

THREE_RELAYS_NODE_ID = "32af8cd1-706b-4145-9947-be1ff931442a"
SENSORS_NODE_ID      = "bb7d075d-0987-4b45-82e3-4336be3ee8bb"
DOSING_PUMPS_NODE_ID = "677cd541-1e8c-4b35-8c18-22a6ea867410"

RELAY1_MTR       = MetricDescr(THREE_RELAYS_NODE, "/Relays/Relay 1/State", MetricDataType.Boolean)
RELAY2_MTR       = MetricDescr(THREE_RELAYS_NODE, "/Relays/Relay 2/State", MetricDataType.Boolean)
PH_MTR           = MetricDescr(SENSORS_NODE,      "/Sensors/ph",           MetricDataType.Boolean)
EC_MTR           = MetricDescr(SENSORS_NODE,      "/Sensors/ec",           MetricDataType.Boolean)
PH_UP_PUMP_MTR   = MetricDescr(DOSING_PUMPS_NODE, "/Dosing Pumps/Ph Up",   MetricDataType.Double)
PH_DOWN_PUMP_MTR = MetricDescr(DOSING_PUMPS_NODE, "/Dosing Pumps/Ph Down", MetricDataType.Double)
EC_UP_PUMP_MTR   = MetricDescr(DOSING_PUMPS_NODE, "/Dosing Pumps/Ec Up",   MetricDataType.Double)


class TestSystem(SystemModel, ABC) :


    def initialise(self) :
        logging.info("Initialising System")

        # =========================================================
        #                   Variables
        # =========================================================

        # Input Variables
        self.new_variable( variable = SYSTEM_TANK_VOLUME_VAR )
        self.new_variable( variable = CIRCULATION_PUMP_STATE_VAR )
        self.new_variable( variable = LIGHTING_STATE_VAR )

        # Output Variables
        self.new_variable( variable = CIRCULATION_PUMP_PUMP_VAR )
        self.new_variable( variable = LIGHTING_LIGHTS_VAR )

        # =========================================================
        #                   Sparkplug
        # =========================================================

        self.broker_url = "localhost"
        self.host_id    = "greenglass"
        self.group_id   = "greenglass"

        # Input metrics
        self.link_metric_to_variable( metric = PH_MTR, variable = STATE_MANAGEMENT_PH_VAR )
        self.link_metric_to_variable( metric = EC_MTR, variable = STATE_MANAGEMENT_EC_VAR )

        # Output metrics
        self.link_variable_to_metric( variable = CIRCULATION_PUMP_PUMP_VAR, metric = RELAY1_MTR )
        self.link_variable_to_metric( variable = LIGHTING_LIGHTS_VAR, metric = RELAY2_MTR )
        self.link_variable_to_metric( variable = STATE_MANAGEMENT_PH_UP_VAR, metric = PH_UP_PUMP_MTR )
        self.link_variable_to_metric( variable = STATE_MANAGEMENT_PH_DOWN_VAR, metric = PH_DOWN_PUMP_MTR )
        self.link_variable_to_metric( variable = STATE_MANAGEMENT_EC_UP_VAR, metric = EC_UP_PUMP_MTR )

        # node_ids
        self.node_id_map.add_node(NodeDescr(THREE_RELAYS_NODE, THREE_RELAYS_NODE_ID))
        self.node_id_map.add_node(NodeDescr(SENSORS_NODE, SENSORS_NODE_ID))
        self.node_id_map.add_node(NodeDescr(DOSING_PUMPS_NODE, DOSING_PUMPS_NODE_ID))

    async def run_processes(self):
        logging.info("Running Processes")
        self.processes.add(asyncio.create_task(CirculationPump(self).run()))
        self.processes.add(asyncio.create_task(Lighting(self).run()))
        self.processes.add(asyncio.create_task(WaterLevel(self).run()))
        self.processes.add(asyncio.create_task(StateManagement(self).run()))

        logging.info("Running Sparkplug")
        self.processes.add(asyncio.create_task(Sparkplug(self).run()))

        await asyncio.gather(*asyncio.all_tasks())


class CirculationPump(ControlProcess, ABC):
        def __init__(self, model) :
            super().__init__(model)

        async def run(self):
            logging.info("Running CirculationPump")
            await self.model.variable(CIRCULATION_PUMP_STATE_VAR).subscribe_async(
                self.model.variable(CIRCULATION_PUMP_PUMP_VAR)
            )

class Lighting(ControlProcess, ABC):
    def __init__(self, model) :
        super().__init__(model)

    async def run(self):
        logging.info("Running Lighting")
        await self.model.variable(LIGHTING_STATE_VAR).subscribe_async(
            self.model.variable(LIGHTING_LIGHTS_VAR)
        )

class WaterLevel(ControlProcess, ABC):
    interval = 60

    def __init__(self, model) :
        super().__init__(model)

    async def run(self):
        logging.info("Running WaterLevel")
        while True:
            await asyncio.sleep(self.interval)
        # to be completed

class StateManagement(ControlProcess, ABC):
    interval = 30

    def __init__(self, model):
        super().__init__(model)

        # Input variables
        self.tank_volume = self.model.variable(SYSTEM_TANK_VOLUME_VAR)
        self.ph = self.model.variable(STATE_MANAGEMENT_PH_VAR)
        self.ph_setpoint = self.model.variable(STATE_MANAGEMENT_PH_SET_POINT_VAR)
        self.ec = self.model.variable(STATE_MANAGEMENT_EC_VAR)
        self.ec_setpoint = self.model.variable(STATE_MANAGEMENT_EC_SET_POINT_VAR)

        # Output variables
        self.ph_up = self.model.variable(STATE_MANAGEMENT_PH_UP_VAR)
        self.ph_down = self.model.variable(STATE_MANAGEMENT_PH_DOWN_VAR)
        self.ec_up = self.model.variable(STATE_MANAGEMENT_EC_UP_VAR)
        self.ec_down = self.model.variable(STATE_MANAGEMENT_EC_DOWN_VAR)


    async def run(self):
        logging.info("Running StateManagement")
        # Loop calling controller at the given interval
        # if all the inputs have values
        while True:
            await asyncio.sleep(self.interval)
            logging.info("Tick")

            if (self.tank_volume.current_value is not None
                    and self.ph.current_value is not None
                    and self.ph_setpoint.current_value is not None
                    and self.ec.current_value is not None
                    and self.ec_setpoint.current_value is not None) :
                await self.controller()
            else:
                logging.info("No data")

    async def controller(self) :
        # Read the current values of the system variables
        print("Controller")

        print("TANK_VOLUME -> " + str(self.tank_volume.current_value.value))
        print("PH -> " + str(self.ph.current_value.value))
        print("PH_SETPOINT -> " + str(self.ph_setpoint.current_value.value))
        print("EC -> " + str(self.ec.current_value.value))
        print("EC_SETPOINT -> " + str(self.ec_setpoint.current_value.value))

        # Run the fuzzy-logic calculation using these values
        # ........

        # Set the ouput value
        await self.ph_up.set_value(Value(1))
        await self.ph_down.set_value(Value(2))
        await self.ec_up.set_value(Value(3))
        await self.ec_down.set_value(Value(4))
