# -----------------------------------------------------------------------------
# HSS - Hermes Skill Server
# Copyright (c) 2020 - Patrick Fial
# -----------------------------------------------------------------------------
# controller.py
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

import logging
import json

# -----------------------------------------------------------------------------
# class Collection
# -----------------------------------------------------------------------------


class Controller:

    # ---------------------------------------------------------------------------
    # ctor
    # ---------------------------------------------------------------------------

    def __init__(self, collection, mqtt, http):
        self.log = logging.getLogger(__name__)
        self.collection = collection
        self.mqtt = mqtt
        self.http = http

    # ---------------------------------------------------------------------------
    # handle
    # ---------------------------------------------------------------------------

    def handle(self, topic, sub_topic, payload):

        # intent_name equals the subtopic on which we received the request
        # try to find the correct skill for the requested intent

        skill = self.collection.get_skill(sub_topic)

        # bail out if we dont find a matching skill

        if not skill:
            self.log.warning(
                "No skill registered for intent '{}'".format(sub_topic))
            return None

        self.log.info(
            "Handling request with skill '{}/{}'".format(skill.name, sub_topic))

        # let the skill handle the request (via RPC)
        # send it the complete JSON string (python dict is causing some issues)

        try:
            res = skill.handle(payload)
            response = json.loads(res.decode("utf-8")) if res else None
        except Exception as e:
            msg = e.args[0] if e.args and len(e.args) else None
            self.log.error("Skill '{}' raised exception while handling intent '{}' ({})".format(
                skill.name, sub_topic, msg))
            self.log.error("Respawning skill")
            self.collection.respawn_skill(skill)
            return False

        # evaluate skill's response and possibly send a message to TTS

        if not response:
            self.log.error("Skill '{}' failed to handle intent '{}'".format(
                skill.name, sub_topic))
        else:
            if "text" in response and response["text"] is not None:
                self.log.info(
                    "Skill '{}/{}' response: '{}'".format(skill.name, sub_topic, response["text"]))
                self.say(response)
            else:
                self.log.info(
                    "Skill '{}/{}' returned empty response".format(skill.name, sub_topic))

    # ---------------------------------------------------------------------------
    # handle
    # ---------------------------------------------------------------------------

    def say(self, response):
        try:
            if self.http:
                # via http / rhasspy API (temporary until rhasspy supports TTS via hermes)

                self.http.post(response["text"])
            else:
                payload = {"sessionId": response["sessionId"], "siteId": response["siteId"],
                        "text": response["text"], "lang": response["lang"]}

                self.mqtt.publish(json.dumps(payload, ensure_ascii=False).encode('utf8'))
        except Exception as e:
            self.log.error(
                "Failed to publish response ({})".format(e))
