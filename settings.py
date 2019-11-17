"""imports settings from settings.json"""
from configloader import ConfigLoader


class Settings(object):
    """Class container for settings dict's"""

    def __init__(self):
        self.imported_settings = ConfigLoader.load('settings.json')
        for key, value in self.imported_settings.items():
            setattr(self, key, value)
