# -----------------------------------------------------------------------------
# HSS - Hermes Skill Server
# Copyright (c) 2020 - Patrick Fial
# -----------------------------------------------------------------------------
# rpc.py
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

import logging

import asyncio
import json

# -----------------------------------------------------------------------------
# class RpcClient
# -----------------------------------------------------------------------------


class RpcClient:

    # --------------------------------------------------------------------------
    # ctor
    # --------------------------------------------------------------------------

    def __init__(self, port):
        self.log = logging.getLogger(__name__)
        self.port = port
        self.channel = None
        self.rpc_client = None
        self.reader = None
        self.writer = None
        self.seq = 0

    # --------------------------------------------------------------------------
    # connect (async)
    # --------------------------------------------------------------------------

    async def connect(self):
        self.log.debug("Connecting to skill's RPC port ...")
        self.reader, self.writer = await asyncio.open_connection('127.0.0.1', self.port)

    # --------------------------------------------------------------------------
    # disconnect (async)
    # --------------------------------------------------------------------------

    async def disconnect(self):
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()

    # --------------------------------------------------------------------------
    # execute (async)
    # --------------------------------------------------------------------------

    async def execute(self, command, payload = None):
        package = { "seq": self.seq, "command": command, "payload": payload }

        self.seq = self.seq + 1

        json_string = json.dumps(package, ensure_ascii=False).replace('\n', '\\n') + '\n'

        self.writer.write(json_string.encode('utf8'))
        await self.writer.drain()

        response = await self.reader.readline()

        try:
            response_obj = json.loads(response.decode("utf-8").replace('\\n', '\n')) if response else None
        except Exception as e:
            self.log.error("Received malformed RPC response ({})".format(e))
            return

        if "payload" not in response_obj:
            self.log.error("Missing mandatory property 'payload' in RPC response")
            return None

        return response_obj["payload"]

# -----------------------------------------------------------------------------
# class RpcServer
# -----------------------------------------------------------------------------


class RpcServer:

    # --------------------------------------------------------------------------
    # ctor
    # --------------------------------------------------------------------------

    def __init__(self, port, controller):
        self.log = logging.getLogger(__name__)

        self.port = port
        self.controller = controller
        self.server = None

    # --------------------------------------------------------------------------
    # start (async)
    # --------------------------------------------------------------------------

    async def start(self):
        server = await asyncio.start_server(self.on_connected, '127.0.0.1', self.port)

        addr = server.sockets[0].getsockname()
        self.log.debug('Serving on {}'.format(addr))

        async with server:
            await server.serve_forever()

    # --------------------------------------------------------------------------
    # on_connected (async)
    # --------------------------------------------------------------------------

    async def on_connected(self, reader, writer):
        while True:
            data = await reader.readline()
            res = None

            if not data:
                return

            try:
                json_string = data.decode("utf-8").replace('\\n', '\n')
                request_obj = json.loads(json_string) if data else None
            except Exception as e:
                self.log.error("Failed to parse RPC request ({})".format(e))
                return

            self.log.debug("Got new RPC request with command '{}'".format(
                request_obj["command"] if "command" in request_obj else ""))

            if not request_obj or "command" not in request_obj or "payload" not in request_obj or "seq" not in request_obj:
                self.log.error("Received malformed RPC request (missing mandatory json propertis 'seq/command'/'payload'")
                return

            res = await self.controller.dispatch_skill_request(request_obj["command"], request_obj["payload"])

            if not res:
                res = ""

            json_string = json.dumps({"seq": request_obj["seq"], "command": "response", "payload": res},
                    ensure_ascii=False).replace('\n', '\\n') + '\n'

            writer.write(json_string.encode('utf8'))
            await writer.drain()
