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
        self.http = None

        # this loads the skill collection from the filesystem

        self.collection = collection.Collection(
            self.args["r"], self.skill_directory)

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

        if "u" in self.args:
            self.log.info("Sending TTS response to '{}'".format(self.args["u"]))
            self.http = httptts.Http(self.args["u"])

        self.log.info("Connecting to MQTT server ...")

        self.mq = mqtt.Mqtt(self.args["h"], self.args["p"],
                            self.args["t"], self.args["T"] if not self.http else None,
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
