"""Contains methods and classes for activing and composing views"""
import typing # pylint: disable=unused-import
from threading import Thread
import widgets as W
from configloader import ConfigLoader
import bodywidgets
from logger import Log


class Views():
    """Stores individual View objects, and activates them"""
    def __init__(self, app: object):
        self.log = app.log
        self.app = app
        self.state = app.state

    def load_view_from_json(self, view_name: str):
        """loads the set of views from json file
        This creates a View object for each view
        """
        views_json = ConfigLoader.load('views.json')

        if view_name in views_json.keys():
            setattr(
                self, view_name, View(
                    self.app, view_name, views_json[view_name]))
            return True
        return False

    def activate(self, activation_source: object, user_data: dict):
        """Activates the selected view"""
        self.log.debug(
            'activation_source: %s, user_data: %s',
            activation_source, user_data)

        if 'view' in user_data.keys():
            activating_view_name = user_data['view']
        else:
            activating_view_name = 'invalid'

        if not self.load_view_from_json(activating_view_name):
            self.log.warning('There is no View named %s', activating_view_name)
            activating_view_name = 'invalid'
            user_data['invalid_error'] = 'There is no View named ' + str(
                user_data['view'])
        self.load_view_from_json(activating_view_name)
        self.log.debug(
            'Activating View Name (before gatekeeper): %s',
            activating_view_name)
        activating_view = self.gatekeeper(activating_view_name)


        self.log.debug(
            'About to activate view: %s', activating_view.name)
        if "no_view_chain" not in activating_view.meta.view_type:
            self.log.debug(
                "Add View %s to View Chain",
                activating_view.name)
            self.state.set_view(activating_view)
            # self.state.set_view_chain_pos(1)
            activating_view.start(user_data)

        else:
            activating_view.start(user_data)

    def gatekeeper(self, requested_view_name: object):
        """This method creates a "gateway". This is a condition, that
           must return true, in order for a view to be activated. If
           the application uses a gateway, then a set of views can be
           made exempt to the gateway, so they can be activated
           regardless of the state of the gate. If a non-exempt view
           is activated with the gate closed, the 'gatekeeper_redirect'
           view will be activated instead.

        Arguments:
            requested_view_name {string} -- The view trying to be activated

        Returns:
            [object] -- The view that will actually be activated
        """

        activating_view = None
        exempt_views = self.app.settings.views['exempt_views']
        self.log.debug("Exempt Views: %s", exempt_views)

        if self.state.gate_opened:
            self.log.debug('Gate is Open')
            activating_view = getattr(self, requested_view_name)
        else:
            if requested_view_name in exempt_views:
                self.log.debug(
                    'View %s is Exempt from Gatekeeper', requested_view_name)
                activating_view = getattr(self, requested_view_name)
            else:
                self.log.debug(
                    'View %s is not Exempt from Gatekeeper',
                    requested_view_name)
                activating_view = getattr(
                    self, self.app.settings.views['gatekeeper_redirect'])
        return activating_view

class MetaData():
    """Stores, updates, and retrieves a view's MetaData

    Returns:
        dict -- a dictionary of metadata results
    """
    def __init__(
            self, app, name: str = '', view_type: str = '', title: str = '',
            sub_title: str = '', text: str = '',
            has_progress_bar: bool = False, has_action: bool = False,
            is_threaded: bool = False, action_class: str = '',
            action_method: str = '', thread_ids: list = None,
            sub_menus: object = None, user_data: dict = None):
        self.app = app
        for key, value in locals().items():
            if key != 'self':
                setattr(self, key, value)
                self.name = name

    def update(self, keys_to_update):
        """Updates metadata"""
        for key, value in keys_to_update.items():
            if hasattr(self, key):
                attr_to_update = getattr(self, key)
                if isinstance(attr_to_update, dict):
                    if isinstance(key, dict):
                        for dict_key, dict_val in value.items():
                            attr_to_update[dict_key] = dict_val
                    else:
                        attr_to_update[key] = value
                if not attr_to_update:
                    setattr(self, key, value)
            else:
                setattr(self, key, value)

    def get(self, meta_keys: list):
        """Gets Meta Data values"""
        results = {}
        for meta_key in meta_keys:
            if hasattr(self, meta_key):
                results[meta_key] = getattr(self, meta_key)
            else:
                results[meta_key] = None
        return results

class View(object):
    """View Objects old the various parts of a given view
    such as the header, footer, body, etc"""

    def __init__(self, app: object, name, view_json_data: dict):
        self.app = app
        self.name = name
        self.log = app.log
        #self.log.debug("View %s Initialized", view_json_data)
        self.meta = MetaData(app)
        for key, value in view_json_data.items():
            if hasattr(self.meta, key):
                self.meta.update({key: value})
            else:
                warning = ('Metadata key ' + key + ' is invalid')
                self.log.warning(warning)
                self.app.errors += 1
        # self.log.debug("self.meta: %s", dir(self.meta))

        self.frame = {
            'footer': None,
            'body': None,
            'header':None
        }
        self.action = None
        self.return_view = self

    def start(self, user_data):
        """Starts the loading, and showing of the activated view
        Typically called by Views.activate, but sometimes called
        through other means"""
        self.log.debug('Meta.user_data:%s', self.meta.user_data)
        self.log.debug('User Data: %s', user_data)

        if "return_view" in user_data.keys():
            self.return_view = user_data["return_view"]
        if user_data and 'user_data' not in user_data.keys():
            self.meta.update({'user_data': user_data})
        elif user_data and 'user_data' in user_data.keys():
            self.meta.update(user_data)

        self.log.debug('Meta.user_data after update: %s', self.meta.user_data)

        if self.meta.has_action: # pylint: disable=no-member
            self.log.debug(
                "Has Action User Data: %s\n\tMeta Data: %s",
                user_data, dir(self.meta))
            action_class = getattr(self.app.actions, self.meta.action_class)
            run_action = getattr(action_class, self.meta.action_method)
        else:
            self.set_view_body()
            self.show_header()
            self.show_body()
            self.show_footer()
            if self.meta.view_type == 'StaticNoInput':
                self.set_focus('footer')
            else:
                self.set_focus('body')

        if self.meta.is_threaded:
            self.log.debug('This View has a threaded action')
            action_thread = Thread(
                target=run_action,
                args=[self.meta])
            self.log.debug(
                'action_thread.getName(): %s', action_thread.getName()
                )
            if self.meta.thread_ids:
                self.meta.thread_ids.append(action_thread.getName())
            else:
                self.meta.thread_ids = [action_thread.getName()]
            action_thread.start()

            self.set_view_body()
            self.show_header()
            self.show_body()
            self.show_footer()

    def reload(self):
        """Reloads a previously activated view. Used by State.go_back and
        State.go_forward"""
        self.show_header()
        self.show_body()
        self.show_footer()

    def show_header(self):
        """retrieves a header widget and sets the widget to the header section
        of App.frame"""
        if self.meta.title:
            title = self.meta.title
        else:
            title = self.app.settings.display['title']
        if self.meta.sub_title:
            sub_title = self.meta.sub_title
        else:
            sub_title = self.app.settings.display['sub_title']
        self.frame['header'] = W.get_header(
            self.app, self.meta.name, title, sub_title)
        self.app.loop.widget.contents.__setitem__(
            'header', [self.frame['header'], None])

    def show_body(self):
        """retrieves a body widget and sets the widget to the body section
        of App.frame"""
        self.app.loop.widget.contents.__setitem__(
            'body', [self.frame['body'].contents, None])

    def show_footer(self):
        """retrieves a footer widget and sets the widget to the footer section
        of App.frame"""
        self.frame['footer'] = W.get_footer(self.meta.name, self.app)
        self.app.loop.widget.contents.__setitem__(
            'footer', [self.frame['footer'], None])

    def draw_screen(self):
        """Re-draws the screen"""
        self.app.loop.draw_screen()

    def set_focus(self, focus_position):
        """Sets the cursor focus to the specified frame section"""
        self.app.frame.set_focus(focus_position)

    def set_view_body(self, *args):
        """sets the frame's body section to the specified body"""
        body_class = None
        # self.log.debug('self.meta.view_type: %s -- self.meta.name: %s',
        #               self.meta.view_type, self.meta.name)
        if self.meta.view_type and self.meta.view_type != 'custom':
            if hasattr(bodywidgets, self.meta.view_type):
                body_class = getattr(bodywidgets, self.meta.view_type)
            elif self.meta.name and hasattr(bodywidgets, self.meta.name):
                body_class = getattr(bodywidgets, self.meta.name)
            else:
                warning = (
                    'No widget type ' + str(self.meta.view_type) +
                    ' or widget named ' + str(self.meta.name)
                )
                self.log.warning(warning)
                self.app.errors += 1

                self.app.exit()
        elif self.meta.name and hasattr(bodywidgets, self.meta.name):
            body_class = getattr(bodywidgets, self.meta.name)
        else:
            warning = 'No custom widget named ' + str(self.meta.name)
            self.log.warning(warning)
            self.app.errors += 1
            self.app.exit(warning)

        #self.log.debug('body_class: %s', dir(body_class))
        if body_class:
            self.frame['body'] = body_class(
                self.app,
                self.meta,
                self.action,
                user_args=args,
                calling_view=self)
