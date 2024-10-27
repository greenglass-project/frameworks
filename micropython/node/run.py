import asyncio
import network
import logging
import node
from simple import MQTTClient
#from primitives import RingbufQueue
from primitives import Queue

async def start() :


    logging.info("Starting tasks")
    mqtt = asyncio.create_task(node.mq_tt_task())
    wifi = asyncio.create_task(node.wifi_task())

    await mqtt

    logging.info("Exiting...")

logging.basicConfig(level=logging.INFO)
asyncio.run(start())