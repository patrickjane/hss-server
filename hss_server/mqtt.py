# -----------------------------------------------------------------------------
# HSS - Hermes Skill Server
# Copyright (c) 2020 - Patrick Fial
# -----------------------------------------------------------------------------
# mqtt.py
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

import logging
import json
import asyncio

from amqtt.client import MQTTClient, ClientException
from amqtt.mqtt.constants import QOS_0

# -----------------------------------------------------------------------------
# class Mqtt
# -----------------------------------------------------------------------------

class Mqtt:

    # --------------------------------------------------------------------------
    # ctor
    # --------------------------------------------------------------------------

    def __init__(self, host, port, username, password, intents_topic,
                    start_session_topic, continue_session_topic, end_session_topic):

        self.log = logging.getLogger(__name__)

        self.intents_topic = intents_topic
        self.start_session_topic = start_session_topic
        self.continue_session_topic = continue_session_topic
        self.end_session_topic = end_session_topic
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.client = None

    # --------------------------------------------------------------------------
    # start (async)
    # --------------------------------------------------------------------------

    async def connect(self):
        self.log.info("Connecting to MQTT server ...")

        if self.username and self.password:
            uri = 'mqtt://{}:{}@{}:{}'.format(self.username, self.password, self.host, self.port)
        elif self.username:
            uri = 'mqtt://{}@{}:{}'.format(self.username, self.host, self.port)
        else:
            uri = 'mqtt://{}:{}'.format(self.host, self.port)

        safe_uri = uri if not self.password else uri.replace(self.password, '***')

        logging.getLogger("transitions.core").setLevel(logging.WARNING)
        logging.getLogger("hbmqtt.mqtt.protocol.handler").setLevel(logging.ERROR)

        self.log.info("Connecting to {} ...".format(safe_uri))

        client = MQTTClient(loop = asyncio.get_event_loop())

        await client.connect(uri)

        self.client = client

        self.log.info("Subscribing to {} ...".format(self.intents_topic))

        await self.client.subscribe([(self.intents_topic, QOS_0)])

        while True:
            self.log.debug("Waiting for message ...")

            try:
                message = await self.client.deliver_message()
                await self.on_message(message.publish_packet)
            except ClientException as e:
                self.log.error("MQTT Client exception: {}".format(e))
                break
            except Exception as e:
                if e and len(str(e)) and str(e) != "Unhandled exception: Event loop is closed" and str(e) != "pop from an empty deque":
                    self.log.error("MQTT exception: {}".format(e))
                break

    # --------------------------------------------------------------------------
    # disconnect (async)
    # --------------------------------------------------------------------------

    async def disconnect(self):
        if not self.client:
            return

        try:
            await self.client.unsubscribe([self.intents_topic])
            await self.client.disconnect()
            self.log.info("Disconnecting")
        except Exception as e:
            pass

    # --------------------------------------------------------------------------
    # on_message (async)
    # --------------------------------------------------------------------------

    async def on_message(self, message):

        # extract intent_name from topic name
        # ('hermes/intent/s710:getTemperature' -> 'getTemperature')

        message_topic = message.variable_header.topic_name

        sub_topic = message_topic.replace(self.intents_topic.replace('#', ''), '')

        self.log.debug("Received message on topic '{}'".format(message_topic))

        try:
            contents = json.loads(message.payload.data.decode("utf-8"))
        except Exception as e:
            self.log.error("Failed to parse message contents ({})".format(e))
            return

        try:
            await self.controller.handle(message_topic, sub_topic, contents)
        except Exception as e:
            self.log.error("Failed to process message ({})".format(e))

    # --------------------------------------------------------------------------
    # publish (async)
    # --------------------------------------------------------------------------

    async def publish(self, message, text, type):
        destination = None

        if type == "start_session":
            destination = self.start_session_topic
        elif type == "continue_session":
            destination = self.continue_session_topic
        elif type == "end_session":
            destination = self.end_session_topic

        if not self.client:
            self.log.error("Can't publish message, not connected to MQTT server")
            return

        if not destination:
            self.log.error("Can't publish message to unknown/invalid destination '{}'".format(type))
            return

        try:
            self.log.info("Publishing message to '{}' with text '{}'".format(destination, text))
            self.log.debug("Message '{}'".format(message))

            payload = json.dumps(message, ensure_ascii=False).encode('utf8')

            await self.client.publish(destination, payload)
        except Exception as e:
            self.log.error(
                "Failed to send message to topic '{}' ({})".format(destination, e))
