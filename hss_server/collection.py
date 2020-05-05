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

    def __init__(self, start_port, skills_path):
        self.log = logging.getLogger(__name__)
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

    def init(self):

        # read subdirectories of skills folder
        # subdirectories are expected to represent the skill-name (e.g. 's710-weather')
        # subdirectory name must not include '.' as a character
        # subdirectories must contain the file 'main.py'

        self.log.info("Initializing skills ...")

        current_port = self.start_port

        for filename in os.listdir(self.skills_directory):
            if filename in ignored_files:
                continue

            skill_name = filename

            res = self.init_skill(skill_name, filename, current_port)

            if res is not True:
                return res

            current_port = current_port+1

        self.log.info('Loaded {} skill{}'.format(len(self.skills), "s" if len(
            self.skills) is 0 or len(self.skills) > 1 else ""))
        return True

    # --------------------------------------------------------------------------
    # init_skill
    # --------------------------------------------------------------------------

    def init_skill(self, skill_name, filename, port):

        # create skill instance

        sk = skill.Skill(skill_name, filename, self.skills_directory, port)

        # spawn subprocess & connect to its RPC server

        res = sk.init()

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

        self.skills.append(sk)

        for intent in intent_list:
            self.log.debug(
                "Registering intent '{}' for skill '{}'".format(intent, skill_name))
            self.intent_map[intent] = sk

        self.log.info("Skill '{}' loaded".format(skill_name))
        return True

    # --------------------------------------------------------------------------
    # respawn_skill
    # --------------------------------------------------------------------------

    def respawn_skill(self, sk):

        # try to re-create skill when it appears to have crashed

        skill_name = sk.name
        filename = sk.filename
        port = sk.port

        # first remove it entirely from intent-map and list of skills

        try:
            for intent_name in sk.my_intents:
                del self.intent_map[intent_name]
        except Exception as e:
            self.log.error(e)

        self.skills.remove(sk)

        # shut it down properly (or rather killingly ...)

        sk.exit(kill=True)
        del sk

        # try to create it anew

        res = self.init_skill(skill_name, filename, port)

        if res is not True:
            self.log.error("Failed to respawn skill '{}'".format(skill_name))
        else:
            self.log.info("Skill '{}' respawned".format(skill_name))

    # --------------------------------------------------------------------------
    # exit
    # --------------------------------------------------------------------------

    def exit(self):
        self.log.info("Stopping skills ...")

        for sk in self.skills:
            try:
                sk.exit()
            except Exception as e:
                self.log.error(
                    'Failed to exit skill "{}" ({})'.format(skill.name, e))

    # --------------------------------------------------------------------------
    # get_skill
    # --------------------------------------------------------------------------

    def get_skill(self, intent_name):
        if intent_name in self.intent_map:
            return self.intent_map[intent_name]

        return None
