from requests import get, post
import json

TIMEOUT = 10


class HomeAssistantClient(object):
    def __init__(self, host, token):
        self.url = "http://{}:8123".format(host)
        self.headers = {
            'Authorization': "Bearer {}".format(token),
            'Content-Type': 'application/json'
        }

    def execute_service(self, domain, service, data):
        response = post("{}/api/services/{}/{}".format(self.url, domain, service),
                        headers=self.headers, data=json.dumps(data), timeout=TIMEOUT)
        response.raise_for_status()
        return response

    def setLevel(self, entityId, level):
        data = {'entity_id': entityId, 'brightness_pct': level}
        self.execute_service('homeassistant', 'turn_on', data)

    def turnOn(self, entityId):
        data = {'entity_id': entityId}
        self.execute_service('homeassistant', 'turn_on', data)

    def turnOff(self, entityId):
        data = {'entity_id': entityId}
        self.execute_service('homeassistant', 'turn_off', data)

    def runScene(self, entityId):
        data = {'entity_id': entityId}
        self.execute_service('scene', 'turn_on', data)
