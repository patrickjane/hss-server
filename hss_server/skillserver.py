# -----------------------------------------------------------------------------
# HSS - Hermes Skill Server
# Copyright (c) 2020 - Patrick Fial
# -----------------------------------------------------------------------------
# skill_server.py
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

import logging

from hss_server import collection
from hss_server import controller
from hss_server import mqtt
from hss_server import httptts # temporary

# -----------------------------------------------------------------------------
# class SkillServer
# -----------------------------------------------------------------------------


class SkillServer:

    # --------------------------------------------------------------------------
    # ctor
    # --------------------------------------------------------------------------

    def __init__(self, args, skill_directory):
        self.args = args
        self.log = logging.getLogger(__name__)
        self.skill_directory = skill_directory

        # this loads the skill collection from the filesystem

        self.collection = collection.Collection(
            self.args["start-port"], self.skill_directory)

    # --------------------------------------------------------------------------
    # start
    # --------------------------------------------------------------------------

    def start(self):
        self.log.info("Loading skills ...")

        # this spawns skills (child-processes) and connects them via RPC

        res = self.collection.init()

        if res is not True:
            self.log.error("Init failed")
            return res

        # setup MQTT

        self.log.info("Connecting to MQTT server ...")

        self.http = httptts.Http(self.args["tts-url"]) if "tts-url" in self.args else None

        self.mq = mqtt.Mqtt(self.args["host"], self.args["port"],
                            self.args["topic"], self.args["tts-topic"],
                            None, None)

        # initialize the controller. it needs the collection + mqtt

        self.controller = controller.Controller(self.collection, self.mq, self.http)
        self.mq.controller = self.controller

        # start the MQTT listener, this will BLOCK until we disconnect & exit

        self.mq.connect()

    # --------------------------------------------------------------------------
    # stop
    # --------------------------------------------------------------------------

    def stop(self):
        if self.mq:
            self.mq.disconnect()

        if self.collection:
            self.collection.exit()
