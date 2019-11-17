class State():
    """This is the state manager used to track movement between views,
    and allow user to go backwards and forwards
    """
    def __init__(self, app, log):
        self.app = app
        self.log = log
        self.log.debug('App.State Initializing')
        self.view_state = {
            'active_view': None,
            'active_view_name': None,
            'previous_view': None,
            'previous_view_name': None,
            'next_view': None,
            'next_view_name': None,
        }
        self.state_chain = {
            'view_chain': [],
            'view_chain_pos': -1,
            'view_count': 0
        }
        self.search_replace = {
            'search_term': None,
            'replace_term': None
        }
        self.active_installation = None
        if self.app.settings.views['gatekeeper_active']:
            self.gate_opened = False
        else:
            self.gate_opened = True
        self.db_exports = []

    def open_gate(self):
        self.gate_opened = True

    def update_state(self, state_prop, prop_key, value):
        """Update's a specified property of the application state

        Arguments:
            state_prop {str} -- the name of the prop to update
            value {str} -- the value you are setting the property to
        """
        try:
            getattr(self, state_prop)
        except AttributeError:
            self.log.warning(
                'App.State.%s Does not Exist! Propery Not Updated',
                state_prop)
        else:
            attribute = getattr(self, state_prop)
            if prop_key:
                if prop_key in attribute.keys():
                    attribute[prop_key] = value
                else:
                    self.log.warning(
                        'State Property %s does not have a key of %s',
                        state_prop,
                        prop_key)
            else:
                attribute = value

    def set_installation(self, obj, installation):
        """Sets the currently selected wp installation

        Arguments:
            obj {obj} -- the object / method that called this method
            installation {dict} -- dictionary of the active installation
        """
        self.log.debug("Obj %s, Installation: %s", obj, installation)
        self.active_installation = installation
        #Opens gate( allows application to load non-exempt views )
        self.open_gate()
        if self.active_installation['home_url']:
            sub_title = self.active_installation['directory'] + \
                ' ( ' + self.active_installation['home_url'] + ' )'
        else:
            sub_title = self.active_installation['directory']
        self.app.settings.display['sub_title'] = sub_title
        self.log.debug(
            'self.app.settings.display["subtitle"]: %s',
            self.app.settings.display['sub_title'])

    def set_sr_search_term(self, value):
        """Sets DB SearchReplace search term"""
        self.search_replace['search_term'] = value

    def set_sr_replace_term(self, value):
        """Sets DB SearchReplace replace term"""
        self.search_replace['replace_term'] = value

    def get_state(self, state_prop, prop_key=None):
        """class getter for state properties

        Arguments:
            state_prop {str} -- State Property

        Returns:
            var -- returns pointer to the state property
        """
        try:
            getattr(self, state_prop)
        except AttributeError:
            self.log.warning(
                'App.State.%s Does not Exist! Propery Not Retrievable',
                state_prop)
            return False
        else:
            attribute = getattr(self, state_prop)
            if prop_key:
                if prop_key in attribute.keys():
                    return attribute[prop_key]
                self.log.warning(
                    "State Property %s does not have a key of %s",
                    state_prop, prop_key)
                return False
            return attribute

    def set_view(self, view):
        """This method is called whenever user moves to a new view.
        This records the new view, and moves the old active_view to
        the previous view variable. This also tracks the user's position
        in the view_chain

        Arguments:
            view {obj} -- [the view instance]
        """
        self.log.debug(
            'Moving from view: %s %s to %s %s',
            self.view_state['active_view_name'],
            self.view_state['active_view'],
            view.name,
            view)

        # assigns the old active view to the previous view
        self.view_state['previous_view'] = self.view_state['active_view']
        self.view_state['previous_view_name'] = self.view_state[
            'active_view_name']

        # assigns the new view to active view
        self.view_state['active_view'] = view
        self.view_state['active_view_name'] = self.view_state[
            'active_view'].name

        # adds the new view to the view chain
        self.log.debug(
            "View Chain before view change: %s",
            self.state_chain)
        self.set_view_chain(view)
        self.set_view_chain_pos(1)
        self.log.debug(
            "View Chain after view change: %s",
            self.state_chain)

        self.log.debug(
            'Preview View: %s %s',
            self.view_state['previous_view_name'],
            self.view_state['previous_view'])
        self.log.debug(
            'View Chain Pos: %s, View Chain: %s',
            self.state_chain['view_chain_pos'],
            self.state_chain['view_chain'])

    def set_view_chain(self, view):
        if len(self.state_chain['view_chain']) > self.state_chain[
                'view_chain_pos']:
            # if not self.state_chain['view_chain']:
            #     self.state_chain['view_chain'].append(view)
            self.state_chain['view_chain'].insert(
                self.state_chain['view_chain_pos'], view)
        else:
            self.state_chain['view_chain'].append(view)
        # self.state_chain['view_chain'] = self.state_chain[
        #     'view_chain'][0:self.state_chain['view_chain_pos'] + 1]
    def set_view_chain_pos(self, adjustment):
        """This set's the user's position in the view chain
        when setting a activating a new view

        Arguments:
            adjustment {int} -- Whether to adjust the view + or -

        Returns:
            boolean -- True if the position change succeeded
                        False if it did not
        """
        chain_pos = self.get_view_chain_pos()
        self.log.debug(
            "chain_pos before view activation: %s",
            chain_pos)
        self.log.debug(
            "Length of View Chain: %s",
            len(self.state_chain['view_chain'])
        )
        if adjustment > 0 and chain_pos < len(
                self.state_chain['view_chain']):
            self.log.debug("view_chain_pos + %s", adjustment)
            self.state_chain['view_chain_pos'] += adjustment
            return True
        elif adjustment < 0 and chain_pos > 0:
            self.log.debug("view_chain_pos + %s", adjustment)
            self.state_chain['view_chain_pos'] += adjustment
            return True
        return False

    def get_view_from_chain(self, chain_pos):
        """Obtaines a view based on the provided chain_pos

        Arguments:
            chain_pos {int} -- Chain position

        Returns:
            obj -- view
        """
        try:
            view = self.state_chain['view_chain'][chain_pos]
            return view
        except IndexError:
            return None

    def get_view_chain_pos(self):
        """Obtains the chain pos of the current view_chain_pos

        Returns:
            [type] -- [description]
        """
        return self.state_chain['view_chain_pos']

    def go_back(self, *args):
        """Moves user back one position in view chain
        """
        self.log.debug(
            "Before go_back\n\tView State: %s \n\tState Chain: %s",
            self.view_state, self.state_chain)

        if self.get_view_from_chain(self.get_view_chain_pos() - 2):
            if self.get_view_chain_pos() - 3 >= -1:
                self.view_state['previous_view'] = self.get_view_from_chain(
                    self.get_view_chain_pos() - 3)
                self.view_state['previous_view_name'] = \
                    self.view_state['previous_view'].name
                self.view_state['next_view'] = self.get_view_from_chain(
                    self.get_view_chain_pos() - 1)
                self.view_state['next_view_name'] = \
                    self.view_state['next_view'].name
            else:
                self.view_state['previous_view'] = None
                self.view_state['previous_view_name'] = None
        else:
            self.view_state['previous_view'] = None
            self.view_state['previous_view_name'] = None

        if self.get_view_from_chain(self.get_view_chain_pos() - 1):
            self.view_state['next_view'] = self.get_view_from_chain(
                self.get_view_chain_pos() - 1)
            self.view_state['next_view_name'] = \
                self.view_state['next_view'].name
        else:
            self.view_state['next_view'] = None
            self.view_state['next_view_name'] = None
        if self.get_view_from_chain(self.get_view_chain_pos() - 2):
            _x = self.get_view_from_chain(self.get_view_chain_pos() - 2)
            self.log.debug('Going back to view: %s', _x.name)
            self.view_state['active_view'] = _x
            self.view_state['active_view_name'] = _x.name
            self.set_view_chain_pos(-1)
            self.log.debug(
                "After go_back\n\tView State: %s \n\tState Chain: %s",
                self.view_state, self.state_chain)
            _x.start({'view': _x.name})

    def go_forward(self):
        """Moves user forward one position in view chain"""
        self.log.debug(
            "Before go_forward\n\tView State: %s \n\tState Chain: %s",
            self.view_state, self.state_chain)

        self.view_state['previous_view'] = self.get_view_from_chain(
            self.get_view_chain_pos() - 1)
        self.view_state['previous_view_name'] = \
            self.view_state['previous_view'].name

        self.view_state['active_view'] = self.get_view_from_chain(
            self.get_view_chain_pos())
        self.view_state['active_view_name'] = \
            self.view_state['active_view'].name

        end_pos = self.get_view_chain_pos() + 2
        if end_pos < len(self.state_chain['view_chain']):
            self.view_state['next_view'] = self.get_view_from_chain(
                self.get_view_chain_pos() + 1)
            self.view_state['next_view_name'] = \
                self.view_state['next_view'].name
        else:
            self.view_state['next_view'] = None
            self.view_state['next_view_name'] = None

        self.view_state['active_view'].start({
            'view': self.view_state['active_view_name']
        })

        self.set_view_chain_pos(1)


        self.log.debug(
            "After go_forward\n\tView State: %s \n\tState Chain: %s",
            self.view_state, self.state_chain)
