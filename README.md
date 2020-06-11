![License](https://img.shields.io/badge/license-MIT-blue) ![PyPI](https://img.shields.io/pypi/v/hss-server?color=green)

# Hermes Skill Server

Modular intent handling server based on the Hermes MQTT protocol. 

# Features

The HSS Skill Server is built as platform for skills, and manages the MQTT connection to the voice assistant. Skills are running as separate processes in custody of the server, each with its own environment and configuration. Connection between skill server and skills is implemented using a simple RPC protocol, and therefore allows to run skills written in different programming languages. Currently, there are bindings for Python and Node.JS available (see below).

The server will listen for intents on the hermes intent-topic (`hermes/intent/#`). When intents are processed, the responses will be published to the according hermes topics (such as `hermes/dialogueManager/endSession`). The skill implementation can make use of several hermes topics (e.g. to answer follow up questions, or start new sessions).

![Architecture](architecture.png)

When started, the server loads all available skills from the skills directory and start them as separate process. For every incoming intent which is published via MQTT, the skill-server tries to find a matching skill, and, if found, hands the intent over to the skill so it can be handled. 

Skills can be managed easily using the `hss-cli` commandline tool (see below).

The HSS Skill Server is compatible with the [Rhasspy voice assistant](https://github.com/synesthesiam/rhasspy).

### Demo



```
(hss) hss@ceres:/srv/hss $ hss-server
INFO:hss: Hermes Skill Server v0.4.0
INFO:hss: Using config directory: '/home/hss/.config/hss_server'
INFO:hss: Using skills directory: '/home/hss/.config/hss_server/skills'
INFO:hss_server.skillserver: Sending TTS response to 'http://calypso.universe:12101/api/text-to-speech'
INFO:hss_server.skillserver: Starting RPC server ...
INFO:hss_server.skillserver: Loading skills ...
INFO:hss_server.collection: Loaded hss-python skill 'hss-skill-s710-weather' v1.0.0
INFO:hss_server.collection: Loaded hss-python skill 'hss-s710-lightsha' v1.0.0
INFO:hss_server.collection: Loaded hss-node skill 'hss-s710-nodedemo' v0.2.3
INFO:hss_server.collection: Loaded 3 skills
INFO:hss_server.skillserver: Connecting to MQTT server ...
INFO:hss_server.mqtt: Connecting to MQTT server ...
INFO:hss_server.mqtt: Connecting to mqtt://ceres.universe:1883 ...
INFO:hss_server.mqtt: Subscribing to hermes/intent/# ...
``` 

# Installation

The server is preferably installed within a virtualenv, and requires python >=3.7. 

## Default user (venv)

```
/home/s710 $> mkdir hss
/home/s710 $> cd hss
/home/s710/hss $> mkdir hss
/home/s710/hss $> python3.7 -m venv /home/s710/hss/venv

/home/s710/hss $> source venv/bin/activate
(venv) /home/s710/hss $> pip install hss_server

```

## Own user (venv)

It is also advised to have it run under a dedicated user. To do so, follow those steps, for a used named "hss" to be created and used:

```
pi@ceres:~ $ cd /srv
pi@ceres:/srv $ mkdir hss
pi@ceres:/srv $ sudo mkdir hss
pi@ceres:/srv $ sudo chown hss:hss hss
pi@ceres:/srv $ sudo -u hss -H -s
hss@ceres:/srv $ cd hss
hss@ceres:/srv/hss $ python3 -m venv .
hss@ceres:/srv/hss $ source bin/activate
(venv) hss@ceres:/srv/hss $ python3 -m pip install pip --upgrade     # optional: update pip 
(venv) hss@ceres:/srv/hss $ pip install hss-server
```


## Config directory

After the initial start, `hss-server` creates its configuration file (`[USER_CONFIG_DIR]/hss_server/config.ini`). The config file will contain several configuration options, especially the location where skills are installed, which by default is `[USER_CONFIG_DIR]/hss_server/skills`.

On Linux, the `USER_CONFIG_DIR` will be `~/.config`, on MacOS it will be `~/Library/Application Support`.

## Updating

Just simply use `pip` again to update:

```
pi@ceres:~ $ cd /srv/hss
pi@ceres:/srv/hss $ sudo -u hss -H -s
hss@ceres:/srv/hss $ source bin/activate
(venv) hss@ceres:/srv/hss $ pip install hss_server --upgrade
```


# Configuration

The main configuration is stored within `[USER_CONFIG_DIR]/hss_server/config.ini`, and might look like the following:

```
[server]
skill_directory = /home/hss/.config/hss_server/skills
rpc_start_port = 51000
tts_url = http://calypso.universe:12101/api/text-to-speech

[mqtt]
server = ceres.universe
port = 1883

[topics]
intents = hermes/intent/#
start_session = hermes/dialogueManager/startSession
continue_session = hermes/dialogueManager/continueSession
end_session = hermes/dialogueManager/endSession
```

### Parameters in `config.ini` 

After initial installation, `hss-server` will assume default values for the MQTT server. Topics *should* never be changed unless there is a good reason, since those are given by the hermes MQTT protocol.

##### `server` / `skill_directory`
Directory where skills are installed.

##### `server` / `rpc_start_port` 
Starting port for RPC communication.

Default: `51000`.
##### `server` / `tts_url` 
If the `tts_url` parameter is configured, replies from skills will be sent via HTTP instead of MQTT (this is for rhasspy 2.4 backwards compatibility). 

Default: `None`,
##### `mqtt`/ `server`
Hostname of the MQTT server.

Default: `localhost`.

##### `mqtt`/ `port`
Hostname of the MQTT server.

Default: `1883`.

##### `topcis`/ `intents `
MQTT topic on which `hss-server` listens for intents.

Default: `hermes/intent/#`.

##### `topcis`/ `start_session `
MQTT topic where `hss-server` publishes start-session messages.

Default: `hermes/dialogueManager/startSession`.

##### `topcis`/ `continue_session `
MQTT topic where `hss-server` publishes continue-session messages.

Default: `hermes/dialogueManager/continueSession`.

##### `topcis`/ `end_session `
MQTT topic where `hss-server` publishes end-session messages.

Default: `hermes/dialogueManager/endSession`.



### Command line


In Addition, several command line switches are available:

```
Usage:
   $ ./hss-server [-dhv][-cl arg]

Options:

   -c [dir]           Directory path where the server's config.ini is located (default: user config dir)

   -l [file]          Log file to write log entries to (default: console)
   -d                 Enable debug log output

   --help             Show this help and exit
   -v, --version      Show version and exit
```


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

## Installing

When installing skills, the GIT repository URL must be given. The repository name is considered to be the skill-name, and will be the subdirectory name within the skills-directory.

Installing a skill involves the following steps:

- cloning the remote repository
- creating a virtualenv
- installing dependencies given by the skill developer (`requirements.txt`)
- asking the user for configuration parameters, if the skill provides the `config.ini.default` file

The server must be restarted after installing a new skill.

Installing is done using the `-i` switch for `hss-cli` followed by the GIT repo URL of the skill.

```
(venv) hss@ceres:/srv/hss $ hss-cli -i https://github.com/patrickjane/hss-s710-lightsha
Installing 'hss-s710-lightsha' into '/home/hss/.config/hss_server/skills/hss-s710-lightsha'
Cloning repository ...
Creating venv ...
Installing dependencies ...
Collecting hss_skill>=0.2.1 (from -r requirements.txt (line 1))
  Using cached https://files.pythonhosted.org/packages/
...  
Initializing config.ini ...
Section 'skill'
Enter value for parameter 'hass_token': ABCXYZ

Skill 'hss-s710-lightsha' successfully installed.

(venv) hss@ceres:/srv/hss $ 
```

## Updating

Updating one or more skills is as easy as pulling changes from the remote GIT repository of the skill.

In addition, `hss-cli` will compare the existing `config.ini` (if it exists) with a new `config.ini.default`, to detect newly added configuration parameters, and then prompt the user for the parameters.

Updating is done using the `-u` switch for `hss-cli` followed by a skill name. If no skill name is given, all skills will be updated.

```
(venv) hss@ceres:/srv/hss $ hss-cli -u hss-s710-rmv
Updating skill 'hss-s710-rmv' ...

No update for skill 'hss-s710-rmv' available.

(venv) hss@ceres:/srv/hss $
```

## Uninstalling

Uninstalling simply leads to the deletion of the skill's subfolder within the skill-directory. No other actions involved.

Uninstalling is done using the `-r` switch for `hss-cli` followed by a skill name.

```
(venv) hss@ceres:/srv/hss $ hss-cli -r hss-s710-rmv
Uninstalling skill 'hss-s710-rmv'
This will erase the directory '/home/hss/.config/hss_server/skills/hss-s710-rmv'
WARNING: The operation cannot be undone. Continue? (yes|NO)
yes
Uninstalling ...

Skill 'hss-s710-rmv' successfully uninstalled.

(venv) hss@ceres:/srv/hss $
```

# Bindings

## Python

In order to develop your own skill in Python, check out the `hss_skill` package at [HSS - Skill](https://github.com/patrickjane/hss-skill). 

## Node.JS

In order to develop your own skill with Node.JS, check out the `node-hss-skill` package at [HSS - Skill](https://github.com/patrickjane/node-hss-skill). 


# Systemd service

In order to automatically start HSS at boot, and shut it down when the server is powering off, a systemd service could be created. It will also restart HSS in case of a failure.

Create a service file, assuming you've installed HSS under the user `hss` and the location of the installation is `/srv/hss` as described above:

```
pi@ceres:~ $ sudo vi /etc/systemd/system/hss.service
```

Put the following contents:

```
[Unit]
Description=Hermes Skill Server
After=network-online.target

[Service]
Type=simple
User=hss
ExecStart=/srv/hss/bin/python3 /srv/hss/bin/hss-server
Restart=always
RestartSec=60

[Install]
WantedBy=multi-user.target
```

Reload the daemon:

```
pi@ceres:~ $ sudo systemctl daemon-reload
```

Start the service:

```
pi@ceres:~ $ sudo systemctl start hss.service
```

The log will appear in `/var/log/syslog`:

```
pi@ceres:~ $ tail -f /var/log/syslog
May  7 08:54:22 ceres systemd[1]: Started Hermes Skill Server.
May  7 08:54:23 ceres python3[19600]: INFO:hss: Hermes Skill Server v0.4.0
May  7 08:54:23 ceres python3[19600]: INFO:hss: Using config directory: '/home/hss/.config/hss_server'
May  7 08:54:23 ceres python3[19600]: INFO:hss: Using skills directory: '/home/hss/.config/hss_server/skills'
```

If you need additional command line parameters, you can put them in the service file at the end of the following line:
```
ExecStart=/srv/hss/bin/python3 /srv/hss/bin/hss-server
```

Like so:

```
ExecStart=/srv/hss/bin/python3 /srv/hss/bin/hss-server -u http://calypso.universe:12101/api/text-to-speech
```

Remember, when changing the service file, the daemon must be reloaded for the changes to take effect:

Reload the daemon:

```
pi@ceres:~ $ sudo systemctl daemon-reload
```

To enable automatic startup, enable the service:

Reload the daemon:

```
pi@ceres:~ $ sudo systemctl enable hss.service
```
