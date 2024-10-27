import asyncio
import network
import logging

from simple import MQTTClient, MQTTException
from primitives import Queue
from sparkplug import Payload

MQTT_CONNECT_CMD = 1
MQTT_DISCONNECT_CMD = 2
MQTT_CONNECTED_EVENT = 3
MQTT_DISCONNECTED_EVENT = 4

ssid = "Fastnet2.4"
password = "worthgate"
broker = "elnor.local"
node_id = "123-456-789-012"
host_id = "development"
group_id = "development"

n_birth_topic = f"spBv1.0/{group_id}/NBIRTH/{node_id}"
n_death_topic = f"spBv1.0/{group_id}/NDEATH/{node_id}"
n_data_topic = f"spBv1.0/{group_id}/NDATA/{node_id}"
n_cmd_topic = f"spBv1.0/{group_id}/NCMD/{node_id}"
state_topic = f"spBv1.0/STATE/{host_id}"

connection_cmds = Queue()
client = MQTTClient(node_id, broker)

"""
    wifi task
    Attempts to join to the wifi network. If successful it sends 
    a CONNECT_CMD message to the mqtt coroutine, Thereafter it checks the
    status of the wifi connection every 30 seconds, and if down it sends a 
    DISCONNECT_CMD to the mqtt coroutine and attempt to reconnect
"""
async def wifi_task():
    logging.info('wifi_task: Starting wifi task')

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    first_pass = True
    connected = False
    while True :
        if not wlan.isconnected() :
            connected = False
            logging.info("wifi_task: Wifi open connection...")

            wlan.connect(ssid, password)
            while not wlan.isconnected():
                logging.info('wifi_task: Waiting for connection...')
                await asyncio.sleep(5)
        else :
            connected = True
            if first_pass :
                first_pass = False
                ip = wlan.ifconfig()[0]
                logging.info(f'wifi_task: Wifi Connected on {ip}')
                await connection_cmds.put(MQTT_CONNECT_CMD)
            #else :
            #    logging.info("Wifi still connected")

            await asyncio.sleep(30)

"""
    mq/tt connection task
    Creates the MQ/TT. This task is managed by the MQ/TT task, and runs only when 
    the connection is required i.e when there is a WiFi connection
"""
async def mq_tt_connection_task() :
    connected = False

    while True :
        if not connected :
            try :
                logging.info("mq_tt_connection_task: Trying toC cnnected to " + broker)

                client.connect()
                connected = True
                logging.info("mq_tt_connection_task: Connected to " + broker)
                await connection_cmds.put(MQTT_CONNECTED_EVENT)

            except OSError as oe :
                logging.warning("mq_tt_connection_task: ERROR %d", oe.errno)
                connected = False
                await asyncio.sleep(5)

        else :
            await asyncio.sleep(30)
            logging.info("mq_tt_connection_task: mq/tt tick")

"""
    mq/tt task
    Manages the mq/tt connection.
    listens to the connection_cmds queue and handles the following messages
    CONNECT_CMD - start the connection task
    DISCONNECT_CMD - stop the connection task
    
"""
async def mq_tt_task():
    logging.info('mq_tt_task: Starting mq/tt task')
    connect_task = None
    connected = False

    while True :
        logging.info('mq_tt_task: Waiting for command...')
        msg = await connection_cmds.get()
        logging.info('mq_tt_task: Received command: %d', msg)

        if msg == MQTT_CONNECT_CMD :
            logging.info('mq_tt_task: CONNECT_CMD')
            if connect_task is None :
                connect_task = asyncio.create_task(mq_tt_connection_task())

        elif msg == MQTT_DISCONNECT_CMD :
            logging.info('mq_tt_task: DISCONNECT_CMD')

            if connect_task is not None :
                connect_task.cancel()
                await connect_task
                connect_task = None
                connected = False

        elif msg == MQTT_CONNECTED_EVENT :
            logging.info('mq_tt_task: MQTT_CONNECTED_EVENT')
            pl = n_birth_payload()
            client.publish(n_birth_topic, "hello world")


        elif msg == MQTT_DISCONNECTED_EVENT :
            logging.info('mq_tt_task: MQTT_DISCONNECTED_EVENT')


def n_birth_payload() :
    return Payload()
