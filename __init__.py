from mycroft import MycroftSkill, intent_file_handler


class GaleHomeAssistant(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler('assistant.home.gale.intent')
    def handle_assistant_home_gale(self, message):
        self.speak_dialog('assistant.home.gale')


def create_skill():
    return GaleHomeAssistant()

