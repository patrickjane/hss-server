# Hermes Skill Server

Intent handling based on modular skills written in python. Intents are supplied from the voice assistant via Hermes MQTT protocol.

```
Voice Assistant   <=== mqtt ===>   hss-server   <===>   hss-skill
```

Compatible with the [Rhasspy voice assistant](https://github.com/synesthesiam/rhasspy).

## Installation

The server is preferably installed within a virtualenv, and requires python >=3.6.

```
/home/s710 $> mkdir hss
/home/s710 $> cd hss
/home/s710/hss $> mkdir hss
/home/s710/hss $> python3.7 -m venv /home/s710/hss/venv

/home/s710/hss $> source venv/bin/activate
(venv) /home/s710/hss $> pip install hss_server

```

Afterwards the server can be run:

```
(venv) /home/s710/hss $> hss-server
INFO:hss: Hermes Skill Server v1.0.0
INFO:hss: Using config dir '/home/s710/.config/hss_server'
INFO:hss: Loading skills from '/home/s710/.config/skills'
INFO:hss_server.skillserver: Loading skills ...
INFO:hss_server.collection: Initializing skills ...
INFO:hss_server.collection: Skill 'hss-skill-s710-weather' loaded
INFO:hss_server.collection: Loaded 1 skill
INFO:hss_server.skillserver: Connecting to MQTT server ...
INFO:hss_server.mqtt: Connected to 10.0.50.5:1883
INFO:hss_server.mqtt: Publishing TTS to topic 'hermes/tts/say'
INFO:hss_server.mqtt: Subscribing to topic 'hermes/intent/#' ...
```

After the initial start, `hss-server` creates its configuration file (`[USER_CONFIG_DIR]/hss_server/config.ini`). The config file will contain the location where skills are installed, which by default is `[USER_CONFIG_DIR]/hss_server/skills`.

On Linux, the `USER_CONFIG_DIR` will be `~/.config`, on MacOS it will be `~/Library/Application Support`.

## Updating

Just simply use `pip` again to update:

```
/home/s710 $> cd hss
/home/s710/hss $> source venv/bin/activate
(venv) /home/s710/hss $> pip install hss_server --upgrade

```

## Features

The server opens a connection to the given MQTT broker, and listens on the intent-topics (by default: `hermes/intent/#`).
Also, all available skills from the skills directory will be loaded, each skill as own process with its own virtualenv.

For every incoming intent which is published via MQTT, the skill-server tries to find a matching skill, and, if found, hands the intent over to the skill so it can be handled. If the skill implements a response text, then this text will be returned via MQTT to the TTS topic (by default: `hermes/tts/say`).

Each skill is running in its own python virtualenv, with its own python dependencies and configuration. Skills can be installed easily from a git repository using the `hss-cli` tool.


## Options

```
Usage:
   $ ./hss-server [-dhv][-hptTurcl arg]

Options:

   -h [host]          MQTT host to connect to (default: localhost)
   -p [port]          MQTT port (default: 1883)
   -t [topic]         MQTT topic to listen on (default: hermes/intent/#)

   -T [topic]         MQTT topic to publish TTS to (default: hermes/tts/say)
   -u [url]           URL to post TTS to. If set, TTS is not sent via MQTT (default: None)

   -r [port]          Starting port for RCP communication (default: 51000)

   -c [dir]           Directory path where the server's config.ini is located (default: user config dir)

   -l [file]          Log file to write log entries to (default: console)
   -d                 Enable debug log output

   --help             Show this help and exit
   -v, --version      Show version and exit
```

The options `-h`/`-p`/`-t`/`-T` are needed for MQTT communication with the voice assistant.

The option `-u` switches the text-to-speech output from MQTT to HTTP, in case the voice assistant does not support MQTT-based TTS messages. For rhasspy <= 2.4, this should be set to `http://[RHASSPYHOST]:12101/api/text-to-speech`.

The `-r` option denotes the beginning of the dynamic RPC port range, and should not be changed unless there are issues with other services.

# CLI

The `hss-cli` tool is used to:

- list all installed skills
- install a skill
- uninstall a skill
- update one or all installed skills

## Usage

```
Usage:
   $ ./hss-cli [-lhv][-iur arg]

Options:

   -l              List all installed skills.

   -i [url]        Install a new skill using [url]. [url] must be a valid GIT link.
   -u ([name])     Update an already installed skill named [name].
                   If [name] is ommited, ALL skills will be updated.

   -r [name]       Uninstall an already installed skill named [name]

   -h, --help      Show this help and exit
   -v, --version   Show version and exit
```

### Installing

When installing skills, the GIT repository URL must be given. The repository name is considered to be the skill-name, and will be the subdirectory name within the skills-directory.

Installing a skill involves the following steps:

- cloning the remote repository
- creating a virtualenv
- installing dependencies given by the skill developer (`requirements.txt`)
- asking the user for configuration parameters, if the skill provides the `config.ini.default` file

The server must be restarted after installing a new skill.

### Updating

Updating one or more skills is as easy as pulling changes from the remote GIT repository of the skill.

In addition, `hss-cli` will compare the existing `config.ini` (if it exists) with a new `config.ini.default`, to detect newly added configuration parameters, and then prompt the user for the parameters.

### Uninstalling

Uninstalling simply leads to the deletion of the skill's subfolder within the skill-directory. No other actions involved.

# Skill development
In order to develop your own skill, check out the `hss_skill` package at [HSS - Skill](https://github.com/patrickjane/hss-skill). It will give detailed instructions of how to develop skills for the hermes skill server.
