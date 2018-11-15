#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import ConfigParser
from hermes_python.hermes import Hermes
from hermes_python.ontology import *
import io

CONFIGURATION_ENCODING_FORMAT = "utf-8"
CONFIG_INI = "config.ini"

class SnipsConfigParser(ConfigParser.SafeConfigParser):
    def to_dict(self):
        return {section : {option_name : option for option_name, option in self.items(section)} for section in self.sections()}


def read_configuration_file(configuration_file):
    try:
        with io.open(configuration_file, encoding=CONFIGURATION_ENCODING_FORMAT) as f:
            conf_parser = SnipsConfigParser()
            conf_parser.readfp(f)
            return conf_parser.to_dict()
    except (IOError, ConfigParser.Error) as e:
        return dict()

def subscribe_intent_callback(hermes, intentMessage):
    conf = read_configuration_file(CONFIG_INI)
    action_wrapper(hermes, intentMessage, conf)


def action_wrapper(hermes, intentMessage, conf):
    from requests import post
    import json
    
    current_session_id = intentMessage.session_id
    try:
     if len(intentMessage.slots.state) > 0:
        myState = intentMessage.slots.state.first().value 
     if len(intentMessage.slots.device_name) > 0:
        myDeviceId = intentMessage.slots.device_name.first().value 
        myDeviceName = intentMessage.slots.device_name.first().value
# put this line back one once the bug is resolved: https://github.com/snipsco/snips-issues/issues/68
#        myDeviceName = intentMessage.slots.device_name.first().raw_value 
    
     payload = json.dumps({"entity_id": myDeviceId})
     url = 'http://'+ conf['secret']['haipaddress'] + ':' + conf['secret']['haport'] + '/api/services/homeassistant/turn_' + myState
     header = {'x-ha-access': conf['secret']['haapipassword'], 'Content-Type': 'application/json'}
     response = post(url, headers=header, data=payload)
    
     hermes.publish_end_session(current_session_id, "Turning " + myState + " " + myDeviceName)
    except:
     hermes.publish_end_session(current_session_id, "Sorry, something went wrong")
    


if __name__ == "__main__":
    with Hermes("localhost:1883") as h:
        h.subscribe_intent("wizbowes:turn_on", subscribe_intent_callback) \
         .start()
