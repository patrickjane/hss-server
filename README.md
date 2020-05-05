# Hermes Skill Server

Intent handling based on modular skills written in python. Intents are supplied from the voice assistant via Hermes MQTT protocol.

```
Voice Assistant   <=== mqtt ===>   hss_server   <===>   hss_skill
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
(venv) /home/s710/hss $> hss_server
Please enter directory where skills shall be stored.
Note that this option can be set/changed any time in '/home/s710/.config/hss_server/config.ini'
However, the server does not start unless this option is set.
Enter directory: /home/s710/hss-skills
INFO:hss: Hermes Skill Server v1.0.0
INFO:hss: Copyright (c) 2020-2020 Patrick Fial
INFO:hss_server.skillserver: Loading skills ...
INFO:hss_server.collection: Initializing skills ...
INFO:hss_server.collection: Loaded 0 skills
INFO:hss_server.skillserver: Connecting to MQTT server ...
```

After the initial start, `hss_server` creates its configuration file (`[USER_CONFIG_DIR]/hss_server/config.ini`). The config file will contain the location where skills are installed, which by default is `[USER_CONFIG_DIR]/hss_server/skills`.

On Linux, the `USER_CONFIG_DIR` will be `~/.config`, on MacOS it will be `~/Library/Application Support`.

## Features

The server opens a connection to the given MQTT broker, and listens on the intent-topics (by default: `hermes/intent/#`).
Also, all available skills from the skills directory will be loaded, each skill as own process with its own virtualenv.

For every incoming intent which is published via MQTT, the skill-server tries to find a matching skill, and, if found, hands the intent over to the skill so it can be handled. If the skill implements a response text, then this text will be returned via MQTT to the TTS topic (by default: `hermes/tts/say`).

Each skill is running in its own python virtualenv, with its own python dependencies and configuration. Skills can be installed easily from a git repository using the `hss_cli` tool.


## Options

```
Usage:
   $ ./hss_server [OPTIONS]

Options:

   --host                  MQTT host to connect to (default: localhost)
   --port                  MQTT port (default: 1883)
   --topic                 MQTT topic to listen on (default: hermes/intent/#)
   --tts-topic             MQTT topic to publish TTS to (default: hermes/tts/say)
   --tts-url               URL to post TTS to. If set, TTS is not sent via MQTT (default: None)
   --start-port            Starting port for RCP communication (default: 51000)

   --config-dir            Location where the server's config.ini is located (default: user config dir)

   --console               Log to stdout instead of a dedicated logfile
   --log-file              Log file to write log entries to (default: ./hss.log)
   --debug                 Enable debug log output

   --help                  Show this help and exit
   --version               Show version and exit
```

## CLI

The `hss_cli` tool is used to: 

- list all installed skills
- install a skill
- uninstall a skill
- update one or all installed skills

### Usage

```
Usage:
   $ ./hss_cli [OPTIONS]

Options:

   --list                          List all installed skills

   --install    --url=[URL]        Install a new skill using [URL]. [URL] must be a valid GIT link.
   --update     (--skill=[NAME])   Update an already installed skill named [NAME].
                                   If skill is ommited, ALL skills will be updated.

   --uninstall  --skill=[NAME]     Uninstall an already installed skill named [NAME]

   --help                          Show this help and exit
   --version                       Show version and exit
```

#### Installing

When installing skills, the GIT repository URL must be given. The repository name is considered to be the skill-name, and will be the subdirectory name within the skills-directory.

Installing a skill involves the following steps:

- cloning the remote repository
- creating a virtualenv
- installing dependencies given by the skill developer (`requirements.txt`)
- asking the user for configuration parameters, if the skill provides the `config.ini.default` file

The server must be restarted after installing a new skill.

#### Updating

Updating one or more skills is as easy as pulling changes from the remote GIT repository of the skill.

In addition, `hss_cli` will compare the existing `config.ini` (if it exists) with a new `config.ini.default`, to detect newly added configuration parameters, and then prompt the user for the parameters.

#### Uninstalling

Uninstalling simply leads to the deletion of the skill's subfolder within the skill-directory. No other actions involved.

# Skill development
In order to develop your own skill, check out the `hss_skill` package at [HSS - Skill](https://github.com/patrickjane/hss-skill). It will give detailed instructions of how to develop skills for the hermes skill server.