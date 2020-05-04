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

import rpyc

# -----------------------------------------------------------------------------
# class Skill (wrapper for loaded skills)
# -----------------------------------------------------------------------------


class Skill:

    # --------------------------------------------------------------------------
    # ctor
    # --------------------------------------------------------------------------

    def __init__(self, skill_name, filename, skills_directory, port):
        self.log = logging.getLogger("skill-" + skill_name)
        self.port = port
        self.name = skill_name
        self.filename = filename
        self.rpc_client = None

        self.python_bin = os.path.join(
            skills_directory, filename, "venv", "bin", "python")
        self.script_file = os.path.join(skills_directory, filename, "main.py")

    # --------------------------------------------------------------------------
    # init
    # --------------------------------------------------------------------------

    def init(self):
        try:
            self.child_process = subprocess.Popen(
                [self.python_bin, self.script_file, "--skill-name=" + self.name, "--port="+str(self.port)])
        except Exception as e:
            self.log.error("Failed to start skill ({})".format(e))

        tries = 0

        # try to connect to skill's RPC-server max 5 seconds (w/ 100ms pause)

        while not self.rpc_client:
            try:
                cl = rpyc.connect("localhost", self.port)
                self.rpc_client = cl
                break
            except Exception as e:
                tries = tries+1

            if tries > 50:
                self.log.error(
                    "Failed to start skill for more than 5 seconds, giving up")
                break

            time.sleep(0.1)

        if not self.rpc_client:
            self.log.error("Failed to start skill")
            self.disconnect()
            return False

        self.my_intents = self.rpc_client.root.get_intentlist()

        return True

    # --------------------------------------------------------------------------
    # exit
    # --------------------------------------------------------------------------

    def exit(self, kill=False):
        if self.rpc_client:
            try:
                self.rpc_client.disconnect()
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

    def handle(self, request):
        return self.rpc_client.root.handle(request)

    # --------------------------------------------------------------------------
    # get_intentlist (static)
    # --------------------------------------------------------------------------

    def get_intentlist(self):
        return self.my_intents
