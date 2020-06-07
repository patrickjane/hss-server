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
import asyncio

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
    # handle (async)
    # ---------------------------------------------------------------------------

    async def handle(self, topic, sub_topic, payload):

        # intent_name equals the subtopic on which we received the request
        # try to find the correct skill for the requested intent

        skill = self.collection.get_skill(sub_topic)

        # bail out if we dont find a matching skill

        if not skill:
            self.log.warning(
                "No skill registered for intent '{}'".format(sub_topic))
            return True

        self.log.info(
            "Handling request with skill '{}/{}'".format(skill.name, sub_topic))

        # let the skill handle the request (via RPC)

        try:
            response = await skill.handle(payload)
        except KeyboardInterrupt:
            print("CONTROLLER: KEYBOARD EXCEPTION")
        except Exception as e:
            msg = e.args[0] if e.args and len(e.args) else None

            print("Exception while handling intent")

            if not msg:
                return False

            self.log.error("Skill '{}' raised exception while handling intent '{}' ({})".format(
                skill.name, sub_topic, msg))
            self.log.error("Respawning skill")

            await self.collection.respawn_skill(skill)

            return False

        # evaluate skill's response and possibly send a message to dialog manager

        if not response:
            self.log.error("Skill '{}' failed to handle intent '{}'".format(
                skill.name, sub_topic))
            return False

        self.log.info(
            "Skill '{}/{}' successfully handled intent '{}'".format(skill.name, sub_topic, sub_topic))

        # regular response

        if "text" in response and response["text"] is not None:
            await self.answer(response)

        # response with follow up question

        elif "question" in response and response["question"] is not None:
            await self.followup(response)

        return True

    # --------------------------------------------------------------------------
    # dispatch_skill_request (async)
    # --------------------------------------------------------------------------

    async def dispatch_skill_request(self, command, payload):
        self.log.debug("Got RPC request '{}'/'{}'".format(command, payload))

        if command == "ask":
            await self.ask(payload)

        elif command == "say":
            await self.say(payload)

    # ---------------------------------------------------------------------------
    # say (async) - voice output (tts) + done (= no session)
    # ---------------------------------------------------------------------------

    async def say(self, response):
        if self.http:
            # via http / rhasspy API (temporary until rhasspy supports TTS via hermes)

            self.http.post(response["text"], response["lang"])
        else:
            payload = {
                        "siteId": response["siteId"] if "siteId" in response else None,
                        "init": {
                            "type": "notification",
                            "text": response["text"],
                            "lang": response["lang"] if "lang" in response else None
                        }
                    }

            await self.mqtt.publish(payload, response["text"], type = "start_session")

    # ---------------------------------------------------------------------------
    # answer (async) - voice output (dialog) + done (= end session)
    # ---------------------------------------------------------------------------

    async def answer(self, response):
        if self.http:
            # via http / rhasspy API (temporary until rhasspy supports TTS via hermes)

            self.http.post(response["text"], response["lang"])
        else:
            payload = {
                        "sessionId": response["sessionId"],
                        "siteId": response["siteId"] if "siteId" in response else None,
                        "text": response["text"],
                        "lang": response["lang"] if "lang" in response else None
                    }

            await self.mqtt.publish(payload, response["text"], type = "end_session")

    # ---------------------------------------------------------------------------
    # followup (async) - voice output (dialog) + follow up question (= reuse session)
    # ---------------------------------------------------------------------------

    async def followup(self, response):
        payload = {
                    "sessionId": response["sessionId"],
                    "siteId": response["siteId"] if "siteId" in response else None,
                    "text": response["question"],
                    "lang": response["lang"] if "lang" in response else None
                }

        if "intentFilter" in response:
            payload["intentFilter"] = response["intentFilter"]

        if "slot" in response:
            payload["slot"] = response["slot"]

        await self.mqtt.publish(payload, response["question"], type = "continue_session")

    # ---------------------------------------------------------------------------
    # ask (async) - voice output (dialog) + new question (= new session)
    # ---------------------------------------------------------------------------

    async def ask(self, response):
        payload = {
                    "siteId": response["siteId"] if "siteId" in response else None,
                    "init": {
                        "type": "action",
                        "text": response["text"],
                        "canBeEnqueued": True,
                        "lang": response["lang"] if "lang" in response else None

                    }
                }

        if "intentFilter" in response:
            payload["init"]["intentFilter"] = response["intentFilter"]

        await self.mqtt.publish(payload, response["text"], type = "start_session")
