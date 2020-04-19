from mycroft import MycroftSkill, intent_handler
from adapt.intent import IntentBuilder
from .ha_client import HomeAssistantClient
import json


class GaleHomeAssistant(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)
        self.ha = None

    def initialize(self):
        self.ha = HomeAssistantClient(
            self.settings.get('host', ''),
            self.settings.get('token', '')
        )
        self.settings_change_callback = self.on_settings_changed
        self.on_settings_changed()

    def on_settings_changed(self):
        try:
            self.deviceMap = json.loads(self.settings.get('device_map', '{}'))
            for entity in self.deviceMap['scene']:
                self.register_vocabulary(entity, 'HAScene')
        except json.JSONDecodeError:
            self.log.error("Invalid JSON in device map: %s" %
                           self.settings.get('device_map'))

    @intent_handler(IntentBuilder('RunScene').require('HAScene'))
    def handle_run_scene(self, message):
        entity = message.data["utterance"]
        entityId = ''

        if entity in self.deviceMap['scene']:
            entityId = self.deviceMap['scene'][entity]

        if not entityId:
            self.speak_dialog('NotFound', {'entity': entity})
        else:
            self.ha.runScene(entityId)
            self.speak_dialog('TurnedOn', {'entity': entity})

    @intent_handler(IntentBuilder('TurnOn').require('entityOn'))
    def handle_turn_on(self, message):
        entity = message.data.get('entityOn')
        entityId = ''

        if entity in self.deviceMap['switch']:
            entityId = self.deviceMap['switch'][entity]
        elif entity in self.deviceMap['light']:
            entityId = self.deviceMap['switch'][entity]

        if not entityId:
            self.speak_dialog('NotFound', {'entity': entity})
        else:
            self.ha.turnOn(entityId)
            self.speak_dialog('TurnedOn', {'entity': entity})

    @intent_handler(IntentBuilder('TurnOff').require('entityOff'))
    def handle_turn_off(self, message):
        entity = message.data.get('entityOff')
        entityId = ''

        if entity in self.deviceMap['switch']:
            entityId = self.deviceMap['switch'][entity]
        elif entity in self.deviceMap['light']:
            entityId = self.deviceMap['switch'][entity]

        if not entityId:
            self.speak_dialog('NotFound', {'entity': entity})
        else:
            self.ha.turnOff(entityId)
            self.speak_dialog('TurnedOff', {'entity': entity})

    @intent_handler(IntentBuilder('SetLightLevel')
                    .require('SetVerb').require('entity')
                    .require('level').optionally('PercentVerb'))
    def handle_set_level(self, message):
        entity = message.data.get('entity')
        level = int(message.data.get('level'))
        lightFound = False
        switchFound = False

        if entity in self.deviceMap['light']:
            lightFound = True
            self.ha.setLevel(self.deviceMap['light'][entity], level)
        if entity in self.deviceMap['switch']:
            switchFound = True
            if level > 0:
                self.ha.turnOn(self.deviceMap['switch'][entity])
            else:
                self.ha.turnOff(self.deviceMap['switch'][entity])

        if lightFound:
            self.speak_dialog('LightLevel', {
                'entity': entity, 'level': level})
        elif switchFound:
            self.speak_dialog('WrongType', {'entity': entity})
        else:
            self.speak_dialog('NotFound', {'entity': entity})

    def stop(self):
        pass


def create_skill():
    return GaleHomeAssistant()
