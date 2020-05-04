# Hermes Skill Server

Intent handling based on modular skills written in python. Intents are supplied via MQTT/Hermes as introduces by snips.ai.

**Usage**:

```
./hss_server --help
Hermes Skill Server v1.0.0
Copyright (c) 2020-2020 Patrick Fial

Usage:
   $ ./server [OPTIONS]

Options:

   --host                  MQTT host to connect to (default: localhost)
   --port                  MQTT port (default: 1883)
   --topic                 MQTT topic to listen on (default: hermes/intent/#)
   --tts-topic             MQTT topic to publish TTS to (default: hermes/tts/say)
   --tts-url               URL to post TTS to. If set, TTS is not sent via MQTT (default: None)
   --start-port            Starting port for RCP communication (default: 51000)

   --console               Log to stdout instead of a dedicated logfile
   --log-file              Log file to write log entries to (default: ./hss.log)
   --debug                 Enable debug log output

   --help                  Show this help and exit
   --version               Show version and exit
```