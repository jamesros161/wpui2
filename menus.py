"""Imports Menus from associated menus.json file"""
from configloader import ConfigLoader


class Menus(object):
    """Imports Menus from associated menus.json file"""

    def __init__(self, app):
        self.log = app.log
        self.app = app
        # self.log.debug('Menus Class initialized')

    def get_menu(self, menu_name):
        """getter for view's menu

        Returns:
            boolean, attr
        """
        try:
            menus_json = ConfigLoader.load('menus.json')
            setattr(self, menu_name, Menu(menu_name, menus_json[menu_name]))
        except AttributeError:
            warning = (
                "No Menu Exists by the name " + menu_name +
                "!!! Menu Retrieval Failed!")
            self.log.warning(warning)
            self.app.errors.append(warning)
            return False
        else:
            return getattr(self, menu_name)

    def get_view_menu_items(self, menu_name):
        """Returns menu item list"""
        try:
            getattr(self, menu_name)
        except AttributeError:
            warning = (
                "No Menu Exists by the name " + menu_name +
                "!!! Menu Retrieval Failed!")
            self.log.warning(warning)
            self.app.errors.append(warning)
            return []
        else:
            menu = getattr(self, menu_name)
            return menu.items


class Menu(object):
    """Individual menu object for each view"""

    def __init__(self, menu_name, menu_items):
        # L.debug("Menu %s Initialized", menu_name)
        self.name = menu_name
        self.items = menu_items
        # L.debug("Menu Items: %s", self.items)
