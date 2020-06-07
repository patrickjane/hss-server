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

from hss_server import rpc

# -----------------------------------------------------------------------------
# class Skill (wrapper for loaded skills)
# -----------------------------------------------------------------------------


class Skill:

    # --------------------------------------------------------------------------
    # ctor
    # --------------------------------------------------------------------------

    def __init__(self, skill_name, filename, skills_directory, port, parent_port):
        self.log = logging.getLogger("skill-" + skill_name)
        self.port = port
        self.parent_port = parent_port
        self.name = skill_name
        self.filename = filename
        self.rpc_client = rpc.RpcClient(port)

        self.python_bin = os.path.join(
            skills_directory, filename, "venv", "bin", "python")
        self.script_file = os.path.join(skills_directory, filename, "main.py")

    # --------------------------------------------------------------------------
    # init
    # --------------------------------------------------------------------------

    async def init(self):
        try:
            self.child_process = subprocess.Popen(
                [self.python_bin, self.script_file,
                    "--skill-name=" + self.name,
                    "--port="+str(self.port),
                    "--parent-port="+str(self.parent_port)])
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

        self.my_intents = await self.rpc_client.execute("get_intentlist")
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
