# -----------------------------------------------------------------------------
# HSS - Hermes Skill Server
# # Copyright (c) 2020 - Patrick Fial
# -----------------------------------------------------------------------------
# skill.py
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

import os
import logging
import subprocess
import time
import json

from hss_server import rpc

# -----------------------------------------------------------------------------
# class Skill (wrapper for loaded skills)
# -----------------------------------------------------------------------------


class Skill:

    # --------------------------------------------------------------------------
    # ctor
    # --------------------------------------------------------------------------

    def __init__(self, cfg, skill_name, skills_directory, port, parent_port):
        self.log = logging.getLogger("skill-" + skill_name)
        self.cfg = cfg
        self.port = port
        self.parent_port = parent_port
        self.name = skill_name
        self.rpc_client = rpc.RpcClient(port)
        self.child_process = None
        self.skills_directory = skills_directory
        self.info = None

        self.python_bin = os.path.join(
            skills_directory, self.name, "venv", "bin", "python")
        self.info_file = os.path.join(skills_directory, self.name, "skill.json")

    # --------------------------------------------------------------------------
    # init
    # --------------------------------------------------------------------------

    async def init(self):
        def check_info_file():
            if not "platform" in self.info:
                self.log.error("Missing property 'platform' in skill.json")
                return False

            if not "intents" in self.info:
                self.log.error("Missing property 'intents' in skill.json")
                return False

            return True

        def complete_args(to):
            to.append("--skill-name=" + self.name)
            to.append("--port="+str(self.port))
            to.append("--parent-port="+str(self.parent_port))

            if self.cfg["debug"]:
                to.append("--debug=true")

            return to

        # load skill.json file for skill & platform info

        if not os.path.isfile(self.info_file):
            self.log.error("Missing file '{}', cannot start skill".format(self.info_file))
            return False

        with open(self.info_file) as json_file:
            try:
                self.info = json.load(json_file)
            except Exception as e:
                self.log.error("Invalid/malformed file '{}', cannot start skill".format(self.info_file))
                return False

        if not check_info_file():
            return False

        self.my_intents = self.info["intents"]

        # actually spawn skill-subprocess, depending on platform

        if self.info["platform"] == "hss-python":
            script_file = os.path.join(self.skills_directory, self.name, "main.py")
            args = [self.python_bin, script_file]

            try:
                self.child_process = subprocess.Popen(complete_args(args))
            except Exception as e:
                self.log.error("Failed to start skill ({})".format(e))

        elif self.info["platform"] == "hss-node":
            if not "node" in self.cfg:
                self.log.error("Missing configuration of 'node' in config.ini, cannot start Node.JS based skill")
                return False

            script_file = os.path.join(self.skills_directory, self.name, "index.js")
            args = [self.cfg["node"], script_file]

            try:
                self.child_process = subprocess.Popen(complete_args(args))
            except Exception as e:
                self.log.error("Failed to start skill ({})".format(e))

        tries = 0

        # try to connect to skill's RPC-server max 5 seconds (w/ 100ms pause)

        while True:
            try:
                await self.rpc_client.connect()
                break
            except Exception as e:
                tries = tries+1

            if tries > 50:
                self.log.error(
                    "Failed to start skill for more than 5 seconds, giving up")
                self.log.error("Failed to connect to RPC port of skill")
                return False

            time.sleep(0.1)

        return True

    # --------------------------------------------------------------------------
    # exit (async)
    # --------------------------------------------------------------------------

    async def exit(self, kill=False):
        if self.rpc_client:
            try:
                await self.rpc_client.disconnect()
            except:
                pass

        if self.child_process:
            if kill:
                self.child_process.kill()
            else:
                self.child_process.terminate()

            self.child_process.wait()

    # --------------------------------------------------------------------------
    # handle
    # --------------------------------------------------------------------------

    async def handle(self, request):
        return await self.rpc_client.execute("handle", request)

    # --------------------------------------------------------------------------
    # get_intentlist
    # --------------------------------------------------------------------------

    def get_intentlist(self):
        return self.my_intents
