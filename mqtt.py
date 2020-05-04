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
import paho.mqtt.client as mqtt

# -----------------------------------------------------------------------------
# class Mqtt
# -----------------------------------------------------------------------------


class Mqtt:

    # --------------------------------------------------------------------------
    # ctor
    # --------------------------------------------------------------------------

    def __init__(self, host, port, topic, tts_topic, username, password):
        self.log = logging.getLogger(__name__)

        self.topic = topic
        self.tts_topic = tts_topic
        self.host = host
        self.port = port
        self.username = username
        self.password = password

        self.client = mqtt.Client()
        self.client.user_data_set(self)

        self.client.on_connect = Mqtt.on_connect
        self.client.on_disconnect = Mqtt.on_disconnect
        self.client.on_message = Mqtt.on_message

    # --------------------------------------------------------------------------
    # connect
    # --------------------------------------------------------------------------

    def connect(self):
        self.client.connect(self.host, self.port)
        self.client.loop_forever()

    # --------------------------------------------------------------------------
    # disconnect
    # --------------------------------------------------------------------------

    def disconnect(self):
        self.client.disconnect()

    # --------------------------------------------------------------------------
    # publish
    # --------------------------------------------------------------------------

    def publish(self, message):
        try:
            self.log.info("Publishing response to '{}'".format(self.tts_topic))
            self.log.debug("Response '{}'".format(message))
            self.client.publish(self.tts_topic, message)
        except Exception as e:
            self.log.error(
                "Failed to send message to topic '{}' ({})".format(self.tts_topic, e))

    # --------------------------------------------------------------------------
    # callbacks (static)
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # on_connect

    def on_connect(client, self, flags, rc):
        if rc is not 0:
            self.log.error("Failed to connect to {}:{} ({})".format(
                self.host, self.port, connack_string(rc)))
        else:
            self.log.info("Connected to {}:{}".format(self.host, self.port))
            self.log.info(
                "Publishing TTS to topic '{}'".format(self.tts_topic))

            self.log.info("Subscribing to topic '{}' ...".format(self.topic))
            client.subscribe(self.topic)

    # --------------------------------------------------------------------------
    # on_disconnect

    def on_disconnect(client, self, rc):
        if rc != 0:
            self.log.error("Connection unexpectedly closed by server")
        else:
            self.log.info("Disconnected from {}:{}".format(
                self.host, self.port))

    # --------------------------------------------------------------------------
    # on_message

    def on_message(client, self, message):

        # extract intent_name from topic name
        # ('hermes/intent/s710:getTemperature' -> 'getTemperature')

        sub_topic = message.topic.replace(self.topic.replace('#', ''), '')

        self.log.debug(
            "Received message on topic '{}'".format(message.topic))

        try:
            self.controller.handle(message.topic, sub_topic, message.payload)
        except Exception as e:
            self.log.error("Failed to process message ({})".format(e))
