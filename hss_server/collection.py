# -----------------------------------------------------------------------------
# HSS - Hermes Skill Server
# Copyright (c) 2020 - Patrick Fial
# -----------------------------------------------------------------------------
# collection.py
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

import logging
import os

from hss_server import skill

ignored_files = ["__init__.py", "__pycache__", ".DS_Store"]

# -----------------------------------------------------------------------------
# class Collection
# Manages skill child-processes
# -----------------------------------------------------------------------------


class Collection:

    # --------------------------------------------------------------------------
    # ctor
    # --------------------------------------------------------------------------

    def __init__(self, cfg, parent_port, start_port, skills_path):
        self.log = logging.getLogger(__name__)
        self.cfg = cfg
        self.parent_port = parent_port
        self.start_port = start_port
        self.skills_directory = os.path.join(
            os.path.abspath(os.path.dirname(__file__)), skills_path)

        # unique list of skill instances

        self.skills = []

        # dictionary intent->skill

        self.intent_map = {}

    # --------------------------------------------------------------------------
    # init
    # --------------------------------------------------------------------------

    async def init(self):

        # read subdirectories of skills folder
        # subdirectories are expected to represent the skill-name (e.g. 's710-weather')
        # subdirectory name must not include '.' as a character
        # subdirectories must contain the file 'main.py'

        current_port = self.start_port

        for folder_name in os.listdir(self.skills_directory):
            if folder_name in ignored_files:
                continue

            res = await self.init_skill(folder_name, current_port, self.parent_port)

            if res is not True:
                return res

            current_port = current_port+1

        self.log.info('Loaded {} skill{}'.format(len(self.skills), "s" if len(
            self.skills) is 0 or len(self.skills) > 1 else ""))
        return True

    # --------------------------------------------------------------------------
    # init_skill
    # --------------------------------------------------------------------------

    async def init_skill(self, skill_name, port, parent_port):

        # create skill instance

        sk = skill.Skill(self.cfg, skill_name,
                self.skills_directory, port, parent_port)

        self.skills.append(sk)

        # spawn subprocess & connect to its RPC server

        res = await sk.init()

        if res is not True:
            return res

        # get intent list and check for intent collision

        intent_list = sk.get_intentlist()

        for intent in intent_list:
            if intent in self.intent_map:
                self.log.error("Skill '{}' tried to register already registered intent '{}'".format(
                    skill_name, intent))
                return False

        # finally add skill to list & register its intents

        for intent in intent_list:
            self.log.debug(
                "Registering intent '{}' for skill '{}'".format(intent, skill_name))
            self.intent_map[intent] = sk

        self.log.info("Loaded {} skill '{}' v{}".format(sk.info["platform"],
            skill_name, sk.info["version"] if "version" in sk.info else "-"))
        return True

    # --------------------------------------------------------------------------
    # respawn_skill (async)
    # --------------------------------------------------------------------------

    async def respawn_skill(self, sk):

        # try to re-create skill when it appears to have crashed

        skill_name = sk.name
        port = sk.port

        # first remove it entirely from intent-map and list of skills

        try:
            for intent_name in sk.my_intents:
                del self.intent_map[intent_name]
        except Exception as e:
            self.log.error(e)

        self.skills.remove(sk)

        # shut it down properly (or rather killingly ...)

        await sk.exit(kill=True)
        del sk

        # try to create it anew

        res = await self.init_skill(self.cfg, skill_name, port, self.parent_port)

        if res is not True:
            self.log.error("Failed to respawn skill '{}'".format(skill_name))
        else:
            self.log.info("Skill '{}' respawned".format(skill_name))

    # --------------------------------------------------------------------------
    # exit
    # --------------------------------------------------------------------------

    async def exit(self):
        self.log.info("Stopping skills ...")

        for sk in self.skills:
            try:
                await sk.exit()
            except Exception as e:
                self.log.error(
                    'Failed to exit skill "{}" ({})'.format(skill.name, e))

        # reset containers

        self.skills = []
        self.intent_map = {}

    # --------------------------------------------------------------------------
    # get_skill
    # --------------------------------------------------------------------------

    def get_skill(self, intent_name):
        if intent_name in self.intent_map:
            return self.intent_map[intent_name]

        return None
