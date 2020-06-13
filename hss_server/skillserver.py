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
from hss_server import rpc
from hss_server import httptts # temporary

import asyncio

# -----------------------------------------------------------------------------
# class SkillServer
# -----------------------------------------------------------------------------


class SkillServer:

    # --------------------------------------------------------------------------
    # ctor
    # --------------------------------------------------------------------------

    def __init__(self, cfg):
        self.cfg = cfg
        self.log = logging.getLogger(__name__)
        self.http = None
        self.rpc_start_port = self.cfg["rpc_start_port"]
        self.rpc_server = None
        self.rpc_server_task = None
        self.mq = None
        self.collection = collection.Collection(
            cfg,
            self.rpc_start_port,
            self.rpc_start_port + 1,    # hss-server is having its own rpc port
            self.cfg["skill_directory"])

    # --------------------------------------------------------------------------
    # start
    # --------------------------------------------------------------------------

    async def start(self):

        # setup rhasspy 2.4 compatibility TTS via HTTP

        if self.cfg["tts_url"]:
            self.log.info("Sending TTS response to '{}'".format(self.cfg["tts_url"]))
            self.http = httptts.Http(self.cfg["tts_url"])

        # setup MQTT

        self.mq = mqtt.Mqtt(self.cfg["mqtt_server"],
                            self.cfg["mqtt_port"],
                            self.cfg["mqtt_user"],
                            self.cfg["mqtt_password"],
                            self.cfg["intents_topic"],
                            self.cfg["start_session_topic"],
                            self.cfg["continue_session_topic"],
                            self.cfg["end_session_topic"])

        # initialize the controller. it needs the collection + mqtt

        self.controller = controller.Controller(self.collection, self.mq, self.http)
        self.mq.controller = self.controller

        # start the RPC server (communication skill -> server)

        self.log.info("Starting RPC server ...")

        self.rpc_server = rpc.RpcServer(self.rpc_start_port, self.controller)

        loop = asyncio.get_event_loop()

        self.rpc_server_task = loop.create_task(self.rpc_server.start())

        # load/initialize collection of skills
        # this spawns skills (child-processes) and connects them via RPC

        self.log.info("Loading skills ...")

        res = await self.collection.init()

        if res is not True:
            self.log.error("Init failed")
            return res

        # start the MQTT listener, this will BLOCK until we disconnect & exit

        self.log.info("Connecting to MQTT server ...")

        try:
            await self.mq.connect()
        except Exception as e:
            pass

    # --------------------------------------------------------------------------
    # stop (async)
    # --------------------------------------------------------------------------

    async def stop(self):
        if self.collection:
            await self.collection.exit()

        if self.rpc_server_task:
            self.log.info("Shutting down RPC server ...")
            self.rpc_server_task.cancel()

            try:
                await self.rpc_server_task
            except asyncio.CancelledError as e:
                pass

        if self.mq:
            await self.mq.disconnect()

    # --------------------------------------------------------------------------
    # reload (async)
    # --------------------------------------------------------------------------

    async def reload(self):
        if not self.collection:
            self.log.error("No collection initialized, cannot reload")
            return False

        await self.collection.exit()

        res = await self.collection.init()

        if res is not True:
            self.log.error("Initializing skills failed")
            return res

        return True