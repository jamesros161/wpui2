"""This module contains classes for handling
the overall flow and state of the application

Raises:
    U.ExitMainLoop: Exits the application
"""
import os
from datetime import datetime
import tempfile
import urwid as Urwid
import widgets as W
from statemanager import State
from menus import Menus
from views import Views
from actions import Actions


class App(object):
    """App Class is a container for the
    state, views, menu, loop, and frame classes"""

    def __init__(self, log, settings):
        self.log = log
        self.settings = settings
        # log.debug("App Class Initializing")

        # Setup home_dir and temp_dir
        self.home_dir = os.path.expanduser("~")
        tempfile.tempdir = self.home_dir
        self.temp_dir = tempfile.TemporaryDirectory()
        # log.debug('temp_dir: %s', self.temp_dir)

        # Initialize Frame
        self.frame = Urwid.Frame(
            Urwid.Filler(
                W.get_text(
                    'body',
                    'Loading...Please Wait',
                    'center')))

        # Initialize MainLoop
        self.loop = Urwid.MainLoop(
            self.frame,
            self.settings.display['palette'],
            unhandled_input=self.unhandled_input,
            handle_mouse=False)

        self.errors = 0
        self.state = State(self, self.log)
        self.menus = Menus(self)
        self.views = Views(self)
        self.actions = Actions(self)
        self.views.activate(self, {'view':'home'})
        self.action_pipes = []

    def exit(self, *args):
        """Exits the applications

        Raises:
            U.ExitMainLoop: Exits the application
        """
        self.log.debug("Args: %s", args)
        if self.errors:
            self.log.info(
                "\n****\nApplication Ended with %s errors at %s"
                "\n\n****", self.errors,
                datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S.%f")
                )
            self.log.info(
                "\nReported Errors:\n\n%s", self.log.error_log.getvalue())
            self.log.error_log.close()

        else:
            self.log.info(
                "\n****\nApplication Ended Normally at %s \n\n****\n",
                datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S.%f"))
        raise Urwid.ExitMainLoop(args)

    def view_return(self, source, user_data):
        self.log.debug("Return User Data: %s", user_data)
        if self.state.view_state['active_view_name'] == 'quit':
            return_view = self.state.view_state['previous_view_name']
            self.views.activate(self, {'view': return_view})

    def close_response(self, source, user_data):
        self.log.debug("Return User Data: %s", user_data)
        active_view = self.state.get_state('view_state', 'active_view')
        return_view = active_view.meta.user_data['return_view']
        self.views.activate(self, {'view': return_view})


    def unhandled_input(self, key):
        """Manages input that is not handled by a
        specific widget

         Arguments:
             key {str} -- the str/char representation of the
                          key pressed
        """
        if isinstance(key, str):
            # raw = loop.screen.get_input(raw_keys=True)
            # debug('raw: %s', raw)
            if key in 'ctrl e':
                self.views.activate(
                    self.state.get_state('active_view'),
                    {'view': 'quit'})
            if key in 'tab':
                if self.frame.focus_position == 'footer':
                    self.frame.focus_position = 'body'
                else:
                    if self.settings.display['menu_enabled']:
                        self.frame.focus_position = 'footer'
            if 'end' in key:
                view_chain_len = len(self.state.state_chain['view_chain'])
                if self.state.get_view_chain_pos() + 1 < view_chain_len:
                    self.state.go_forward()
                else:
                    self.log.debug('Unable to step forwards')
            if 'home' in key:
                if self.state.get_view_chain_pos() != 0:
                    self.state.go_back()
                else:
                    self.log.debug('Unable to step backwards')
