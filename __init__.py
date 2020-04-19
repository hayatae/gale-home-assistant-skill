from mycroft import MycroftSkill, intent_handler
from adapt.intent import IntentBuilder
from .ha_client import HomeAssistantClient
import json


class GaleHomeAssistant(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)
        self.ha = None

    def initialize(self):
        self.deviceMap = {}
        self.settings_change_callback = self.on_settings_changed
        self.on_settings_changed()

    def on_settings_changed(self):
        # Create new HA Client with host/token settings
        self.ha = HomeAssistantClient(
            self.settings.get('host', ''),
            self.settings.get('token', '')
        )

        # Load and process device map
        try:
            self.deviceMap = json.loads(self.settings.get('device_map', '{}'))
            scenes = self.deviceMap.get('scene', {})
            for sceneName in scenes:
                self.register_vocabulary(sceneName, 'HAScene')
        except json.JSONDecodeError:
            self.log.error("Invalid JSON in device map: %s" %
                           self.settings.get('device_map'))

    @intent_handler(IntentBuilder('RunScene').require('HAScene'))
    def handle_run_scene(self, message):
        entity = message.data["utterance"]
        scenes = self.deviceMap.get('scene', {})
        entityId = scenes.get(entity, '')

        if not entityId:
            self.speak_dialog('NotFound', {'entity': entity})
        else:
            self.ha.runScene(entityId)
            self.speak_dialog('TurnedOn', {'entity': entity})

    @intent_handler(IntentBuilder('TurnOn').require('entityOn'))
    def handle_turn_on(self, message):
        entity = message.data.get('entityOn')
        switches = self.deviceMap.get('switch', {})
        lights = self.deviceMap.get('light', {})

        # Check switch names first
        entityId = switches.get(entity, '')

        # Then check lights
        if not entityId:
            entityId = lights.get(entity, '')

        if not entityId:
            self.speak_dialog('NotFound', {'entity': entity})
        else:
            self.ha.turnOn(entityId)
            self.speak_dialog('TurnedOn', {'entity': entity})

    @intent_handler(IntentBuilder('TurnOff').require('entityOff'))
    def handle_turn_off(self, message):
        entity = message.data.get('entityOff')
        switches = self.deviceMap.get('switch', {})
        lights = self.deviceMap.get('light', {})

        # Check switch names first
        entityId = switches.get(entity, '')

        # Then check lights
        if not entityId:
            entityId = lights.get(entity, '')

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
        switches = self.deviceMap.get('switch', {})
        lights = self.deviceMap.get('light', {})
        lightFound = lights.get(entity, '')
        switchFound = switches.get(entity, '')

        if lightFound:
            self.ha.setLevel(lightFound, level)
        if switchFound:
            if level > 0:
                self.ha.turnOn(switchFound)
            else:
                self.ha.turnOff(switchFound)

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
