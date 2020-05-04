# -----------------------------------------------------------------------------
# HSS - Hermes Skill Server
# Copyright (c) 2020 - Patrick Fial
# -----------------------------------------------------------------------------
# http.py
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

import logging
import requests

# -----------------------------------------------------------------------------
# class Http
# temporary HTTP bridge for TTS to rhasspy
# -----------------------------------------------------------------------------


class Http:

    # --------------------------------------------------------------------------
    # ctor
    # --------------------------------------------------------------------------

    def __init__(self, url):
        self.log = logging.getLogger(__name__)
        self.url = url

        logging.getLogger("requests").setLevel(logging.ERROR)
        logging.getLogger("urllib3").setLevel(logging.ERROR)

    # --------------------------------------------------------------------------
    # post
    # --------------------------------------------------------------------------

    def post(self, message):
        try:
            self.log.info("POST response to '{}'".format(self.url))
            self.log.debug("Response '{}'".format(message))

            req = requests.post(self.url, data = message)
        except Exception as e:
            self.log.error(
                "Failed to POST message to url '{}' ({})".format(self.url, e))

        if req.status_code != 200:
            self.log.error("Received '' from '{}' (HTTP {} / {})".format(req.status_code, req.content.decode('utf-8')[:80] if req.content else "-"))
            return None

            self.log.info("Publishing response to '{}'".format(self.tts_topic))
            self.log.debug("Response '{}'".format(message))
            self.client.publish(self.tts_topic, message)
