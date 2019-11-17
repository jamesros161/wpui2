"""Collection of classes each used for a view"""
import datetime
import time
import getpass
from html.parser import HTMLParser
from collections import OrderedDict
import urwid as U
import widgets as W
BODY = 'body'
CENTER = 'center'

class StaticNoInput():
    """Body Widget with static text content,
       and no input

    Returns:
        object -- A widget to be used as the body widget
    """

    def __init__(self, app: object, meta: object,
                 action: callable, user_args: dict = None,
                 calling_view: object = None):
        self.app = app
        self.log = app.log
        self.metadata = meta
        self.action = action
        self.user_args = user_args
        self.calling_view = calling_view
        self.contents = self.get_contents()

    def get_contents(self):
        """This method is used to return the actual widget object"""
        text_widget = W.get_text(
            BODY,
            str(self.metadata.text),
            CENTER)

        main_pile = U.Pile([text_widget])

        return U.Filler(main_pile, 'middle')

class StaticMenuPrompt():
    """Body Widget with Static text prompt in a box,
       with a set of buttons to choose from to respond

    Returns:
        object -- A widget to be used as the body widget
    """

    def __init__(self, app: object, meta: object,
                 action: callable, user_args: dict = None,
                 calling_view: object = None):
        self.app = app
        self.log = app.log
        self.metadata = meta
        self.action = action
        self.user_args = user_args
        self.calling_view = calling_view
        self.contents = self.get_contents()

    def get_contents(self):
        """This method is used to return the actual widget object"""

        self.log.debug(self.metadata)

        prompt = W.get_col_row([
            W.get_blank_flow(),
            W.get_text(BODY, self.metadata.text, CENTER),
            W.get_blank_flow()
        ])

        prompt_menu = self.app.menus.get_menu(self.metadata.sub_menus[0])
        prompt_menu_grid = W.get_grid_flow(self.app, prompt_menu.items)

        box_contents = U.Pile([
            W.get_div(), prompt, W.get_div(), prompt_menu_grid
        ])

        line_box = W.get_line_box(
            self.app, box_contents, self.metadata.title
        )
        outer_col = W.get_col_row([
            W.get_blank_flow(),
            line_box,
            W.get_blank_flow()
        ])

        main_pile = U.Pile([outer_col])

        return U.Filler(main_pile, 'middle')

class ApiResponse():
    """Body Widget with Static text prompt in a box,
       with a set of buttons to choose from to respond

    Returns:
        object -- A widget to be used as the body widget
    """

    def __init__(self, app: object, meta: object,
                 action: callable, user_args: dict = None,
                 calling_view: object = None):
        self.app = app
        self.log = app.log
        self.metadata = meta
        self.action = action
        self.user_args = user_args
        self.calling_view = calling_view
        self.contents = self.get_contents()

    def get_contents(self):
        """This method is used to return the actual widget object"""

        self.log.debug("api response user_data %s", self.metadata.user_data)
        result, error = ['','']
        if 'api_response' in self.metadata.user_data.keys():
            result = self.metadata.user_data['api_response']['result']
            error = self.metadata.user_data['api_response']['error']
        prompt = []
        if result:
            prompt.append(W.get_col_row([
                W.get_blank_flow(),
                W.get_text(BODY, result, CENTER),
                W.get_blank_flow()
            ]))
        if error:
            prompt.append(W.get_col_row([
                W.get_blank_flow(),
                W.get_text(BODY, error, CENTER),
                W.get_blank_flow()
            ]))
        prompt_menu = self.app.menus.get_menu(self.metadata.sub_menus[0])
        prompt_menu_grid = W.get_grid_flow(self.app, prompt_menu.items)

        box_contents = [W.get_div()]
        box_contents.extend(prompt)
        box_contents.extend([W.get_div(), prompt_menu_grid])

        box_pile = U.Pile(box_contents)

        line_box = W.get_line_box(
            self.app, box_pile, self.metadata.title
        )
        outer_col = W.get_col_row([
            W.get_blank_flow(),
            line_box,
            W.get_blank_flow()
        ])

        main_pile = U.Pile([outer_col])

        return U.Filler(main_pile, 'middle')

class ApiRequestProgressBar():
    """Body Widget with Static text prompt in a box,
       with a set of buttons to choose from to respond

    Returns:
        object -- A widget to be used as the body widget
    """
    def __init__(self, app: object, meta: object,
                 action: callable, user_args: dict = None,
                 calling_view: object = None):
        self.app = app
        self.log = app.log
        self.metadata = meta
        self.action = action
        self.user_args = user_args
        self.calling_view = calling_view
        self.progress_bar = U.ProgressBar(
            'body',
            'progressbar',
            current=0,
            done=100)
        self.contents = self.get_contents()

    def get_contents(self):
        """This method is used to return the actual widget object"""

        prompt = W.get_col_row([
            W.get_blank_flow(),
            ('weight', 2, W.get_text(BODY, self.metadata.text, CENTER)),
            W.get_blank_flow()
        ])
        self.log.debug("has_progress_bar: %s", self.metadata.has_progress_bar)
        if self.metadata.has_progress_bar:
            progress_row = W.get_col_row([
                ('weight', 1, W.get_blank_flow()),
                ('weight', 2, self.progress_bar),
                ('weight', 1, W.get_blank_flow())
            ])
            box_contents = U.Pile([
                W.get_div(), prompt, W.get_div(),
                progress_row, W.get_div()])

            self.app.action_pipes.append(self.app.loop.watch_pipe(
                self.update_progress_bar))
            self.log.debug(
                'self.app.action_pipe: %s', self.app.action_pipes[-1])
            self.metadata.user_data['action_pipe'] = \
                self.app.action_pipes[-1]
        else:
            box_contents = U.Pile([
                W.get_div(), prompt, W.get_div()
                ])

        line_box = W.get_line_box(
            self.app, box_contents, self.metadata.title
        )
        outer_col = W.get_col_row([
            W.get_blank_flow(),
            line_box,
            W.get_blank_flow()
        ])

        main_pile = U.Pile([outer_col])

        return U.Filler(main_pile, 'middle')

    def update_progress_bar(self, progress):
        self.log.debug('Progress: %s', progress)

        if progress:
            self.progress_bar.set_completion(int(float(progress)))
        else:
            self.progress_bar.set_completion(100)
        if int(float(progress)) >= 100:
            self.progress_bar.set_completion(100)
            try:
                self.app.loop.remove_watch_pipe(
                    self.metadata.user_data['action_pipe'])
            except OSError:
                self.log.Warning('Error trying to remove watch_pipe')
            self.app.loop.draw_screen()

            after_action_view = self.metadata.user_data['after_action_view']
            self.app.views.activate(self, {'view': after_action_view})

class DisplayTableWithSelectRows():
    def __init__(self, app: object, meta: object,
                 action: callable, user_args: dict = None,
                 calling_view: object = None):
        self.app = app
        self.log = app.log
        self.metadata = meta
        self.action = action
        self.user_args = user_args
        self.calling_view = calling_view
        sel_action_class = getattr(
            self.app.actions,
            self.metadata.user_data['sel_action']['action_class'])
        self.sel_action = getattr(
            sel_action_class,
            self.metadata.user_data['sel_action']['action_method'])

        self.contents = self.get_contents()

    def get_contents(self):
        """Updates the view's body in response to
        the views action_on_load function

        Arguments:
            installations {list} -- [list of installations]
        """

        box_width = self.metadata.user_data['box_width']
        data_from_api = None
        api_vars = self.app.actions.apis.api_vars
        self.log.debug("ap_vars: %s", api_vars)
        table_data = self.metadata.user_data['table_data']
        table_headers = self.app.menus.get_menu(
            self.metadata.user_data['header_keys']
            ).items
        if table_data['api_vars'] in api_vars.keys():
            api = api_vars[table_data['api_vars']]
            if table_data['key'] in api.keys():
                data_from_api = api[table_data['key']]

        for row in data_from_api:
            for col in table_headers:
                col.append([])
                if col[1] in row.keys():
                    col[2].append(len(str(row[col[1]])) + 6)
                col[2].append(len(str(col[0])) + 6)

        for col in table_headers:
            col[2].sort()
            if col[2]:
                col[2] = col[2][-1]

        headers = []
        for col in table_headers:
            if table_headers.index(col) == len(table_headers) - 1:
                headers.append(
                    ('weight', 3, U.AttrMap(
                        W.get_text('header', col[0], CENTER),
                        'header'
                    ))
                )
            elif col[2]:
                headers.append(
                    (int(col[2]), U.AttrMap(
                        W.get_text('header', col[0], CENTER),
                        'header'
                    ))
                )
            else:
                headers.append(
                    ('pack', U.AttrMap(
                        W.get_text('header', col[0], CENTER),
                        'header'
                    ))
                )
        rows = [
            W.get_div(),
            U.AttrMap(
            W.get_col_row(headers),
            'headers')]
        for row in data_from_api:
            cols = []
            for col in table_headers:
                if table_headers.index(col) == len(table_headers) - 1:
                    self.log.info('This is the last column')
                    self.log.debug("Column Width: %s", col[2])
                    cols.append(
                            ('weight', 2, W.get_text(
                                BODY,
                                "\n" + str(row[col[1]]) + "\n", CENTER)))
                elif table_headers.index(col) == 0:
                    cols.append(
                            (int(col[2]),
                            W.BoxButton(
                                str(row[col[1]]),
                                on_press=self.sel_action,
                                user_data=row)
                            )
                        )
                elif col[1] in row.keys():
                    if col[2]:
                        cols.append(
                            (int(col[2]), W.get_text(
                                BODY, "\n" + str(row[col[1]]) + "\n", CENTER)))
                    else:
                        cols.append(
                            ('pack', W.get_text(
                                BODY, "\n" + str(row[col[1]]) + "\n", CENTER)))
            rows.append(W.get_col_row(cols))
        rows.append(W.get_div())
        self.log.debug(rows)
        table = U.Pile(rows)

        box = W.get_line_box(self.app, table, self.metadata.title)
        box_col = W.get_col_row([
            W.get_blank_flow(), ('weight', box_width, box), W.get_blank_flow()
        ])

        return U.Filler(box_col, 'middle')


        # location_list = self.app.actions.apis.api_vars
        # if installations:
        #     for installation in installations:
        #         location_list.append(len(installation['directory']))
        #     location_list.sort(reverse=True)
        #     location_width = location_list[0] + 4
        #     installation_columns = [W.get_col_row([
        #         W.get_blank_flow(),
        #         (10, U.AttrMap(W.get_div(), 'header')),
        #         (
        #             location_width,
        #             U.AttrMap(
        #                 W.get_text(
        #                     'header',
        #                     'Location',
        #                     'center'
        #                 ),
        #                 'header')),
        #         ('weight', 2, U.AttrMap(
        #             W.get_text(
        #                 'header',
        #                 'Home URL',
        #                 'center'
        #             ),
        #             'header')),
        #         (18, U.AttrMap(
        #             W.get_text(
        #                 'header',
        #                 'Valid wp_options',
        #                 'center'
        #             ),
        #             'header')),
        #         (20, U.AttrMap(
        #             W.get_text(
        #                 'header',
        #                 'wp_db_check passed',
        #                 'center'
        #             ),
        #             'header')),
        #         W.get_blank_flow()
        #     ])]
        #     for installation in installations:
        #         installation_rows = [
        #             W.get_blank_flow(),
        #             (10, widgets.BoxButton(
        #                 ' + ',
        #                 on_press=self.app.state.set_installation,
        #                 user_data=installation)),
        #             (location_width, W.get_text(
        #                 'body',
        #                 installation['directory'],
        #                 'center'))
        #         ]
        #         # self.log.debug(
        #         #     'valid_wp_options: %s',
        #         #     installation['valid_wp_options'])
        #         if installation['valid_wp_options']:
        #             installation_rows.extend([
        #                 ('weight', 2, W.get_text(
        #                     'body',
        #                     installation['home_url'],
        #                     'center')),
        #                 (18, W.get_text(
        #                     'body',
        #                     str(installation['valid_wp_options']),
        #                     'center')),
        #                 (20, W.get_text(
        #                     'body',
        #                     str(installation['wp_db_check_success']),
        #                     'center'))
        #             ])
        #         else:
        #             installation_rows.append(
        #                 (
        #                     'weight',
        #                     3,
        #                     W.get_text(
        #                         'body',
        #                         str(installation['wp_db_error']),
        #                         'center'))
        #             )
        #         installation_rows.append(
        #             W.get_blank_flow()
        #         )
        #         installation_columns.append(
        #             W.get_col_row(installation_rows)
        #         )
        # else:
        #     installation_columns = [W.get_col_row([
        #         W.get_blank_flow(),
        #         W.get_text(
        #             'body',
        #             'There Are No WordPress Installations found for User: ' +
        #             getpass.getuser(),
        #             'center'),
        #         W.get_blank_flow()
        #     ])]
        # installation_pile = U.Pile(installation_columns)
        # filler = U.Filler(installation_pile, 'middle')
        # self.app.frame.contents.__setitem__('body', [filler, None])
        # time.sleep(1)
        # if installations:
        #     self.app.frame.set_focus('body')
        # else:
        #     self.app.frame.set_focus('footer')
        # self.app.loop.draw_screen()


# class Default(object):
#     """Parent Class for body widgets

#     Returns:
#         obj -- Returns a widget to be used as the 'body' portion of the frame
#     """

#     def __init__(self, app, metadata):
#         self.progress_bar = U.ProgressBar(
#             'body',
#             'progressbar',
#             current=0,
#             done=100)
#         self.app = app
#         self.log = app.log
#         self.metadata = metadata
#         self.widget = self.define_widget()
#         self.pile = None
#         self.progress = 0

#     def define_widget(self):
#         """Page displayed as Home Page for the application
#         """
#         initial_text = self.metadata['initial_text']
#         progress_bar = self.metadata['has_progress_bar']
#         self.log.debug(' Initial_Text : %s, Progress_bar: %s',
#                        initial_text, progress_bar)
#         if initial_text:
#             initial_text_str = str(initial_text)
#         else:
#             initial_text_str = str(' ')
#         initial_text = W.get_text(
#             'body',
#             str(initial_text_str),
#             'center')
#         if progress_bar:
#             progress_row = W.get_col_row([
#                 ('weight', 2, W.get_blank_flow()),
#                 self.progress_bar,
#                 ('weight', 2, W.get_blank_flow())
#             ])
#             main_pile = U.Pile([initial_text, progress_row])
#             self.app.action_pipe = self.app.loop.watch_pipe(
#                 self.update_progress_bar)
#             self.log.debug('self.app.action_pipe: %s', self.app.action_pipe)
#         else:
#             main_pile = U.Pile([initial_text])
#         return U.Filler(main_pile, 'middle')

#     def update_progress_bar(self, progress):
#         """Updates the progress bar on body widgets that
#         have a progress bar

#         Arguments:
#             progress {str} -- string representation of the current
#                               progress
#         """
#         self.log.debug('Pipe: %s :: Progress: %s', self.app.action_pipe, progress)
#         if progress:
#             self.progress_bar.set_completion(int(float(progress)))
#         else:
#             self.progress_bar.set_completion(100)
#             try:
#                 self.app.loop.remove_watch_pipe(self.app.action_pipe)
#             except OSError:
#                 self.log.Warning('Error trying to remove watch_pipe')
#             self.app.loop.draw_screen()

# # ADD SUBCLASSES HERE for each view's body


# class Home(Default):
#     """Creates the specific body widget for the view of the same name"""

#     def __init__(
#         self, app, metadata, action, user_args=None,
#                  calling_view=None):
#         super(Home, self).__init__(
#             app, initial_text, progress_bar=progress_bar)
#         self.log.debug("user_args: %s, calling_view: %s", user_args, calling_view)


# class Invalid(Default):
#     """Creates the specific body widget for the view of the same name"""

#     def __init__(self, app, initial_text, user_args=None,
#                  calling_view=None, progress_bar=False):
#         super(Invalid, self).__init__(
#             app, initial_text, progress_bar=progress_bar)
#         self.log.debug("user_args: %s, calling_view: %s", user_args, calling_view)


# class Installs(Default):
#     """Creates the specific body widget for the view of the same name"""

#     def __init__(self, app, initial_text, user_args=None,
#                  calling_view=None, progress_bar=False):
#         super(Installs, self).__init__(
#             app, initial_text, progress_bar=progress_bar)
#         self.log.debug("user_args: %s, calling_view: %s", user_args, calling_view)

#     def after_action(self, installations):
#         """Updates the view's body in response to
#         the views action_on_load function

#         Arguments:
#             installations {list} -- [list of installations]
#         """
#         location_list = []
#         if installations:
#             for installation in installations:
#                 location_list.append(len(installation['directory']))
#             location_list.sort(reverse=True)
#             location_width = location_list[0] + 4
#             installation_columns = [W.get_col_row([
#                 W.get_blank_flow(),
#                 (10, U.AttrMap(W.get_div(), 'header')),
#                 (
#                     location_width,
#                     U.AttrMap(
#                         W.get_text(
#                             'header',
#                             'Location',
#                             'center'
#                         ),
#                         'header')),
#                 ('weight', 2, U.AttrMap(
#                     W.get_text(
#                         'header',
#                         'Home URL',
#                         'center'
#                     ),
#                     'header')),
#                 (18, U.AttrMap(
#                     W.get_text(
#                         'header',
#                         'Valid wp_options',
#                         'center'
#                     ),
#                     'header')),
#                 (20, U.AttrMap(
#                     W.get_text(
#                         'header',
#                         'wp_db_check passed',
#                         'center'
#                     ),
#                     'header')),
#                 W.get_blank_flow()
#             ])]
#             for installation in installations:
#                 installation_rows = [
#                     W.get_blank_flow(),
#                     (10, widgets.BoxButton(
#                         ' + ',
#                         on_press=self.app.state.set_installation,
#                         user_data=installation)),
#                     (location_width, W.get_text(
#                         'body',
#                         installation['directory'],
#                         'center'))
#                 ]
#                 # self.log.debug(
#                 #     'valid_wp_options: %s',
#                 #     installation['valid_wp_options'])
#                 if installation['valid_wp_options']:
#                     installation_rows.extend([
#                         ('weight', 2, W.get_text(
#                             'body',
#                             installation['home_url'],
#                             'center')),
#                         (18, W.get_text(
#                             'body',
#                             str(installation['valid_wp_options']),
#                             'center')),
#                         (20, W.get_text(
#                             'body',
#                             str(installation['wp_db_check_success']),
#                             'center'))
#                     ])
#                 else:
#                     installation_rows.append(
#                         (
#                             'weight',
#                             3,
#                             W.get_text(
#                                 'body',
#                                 str(installation['wp_db_error']),
#                                 'center'))
#                     )
#                 installation_rows.append(
#                     W.get_blank_flow()
#                 )
#                 installation_columns.append(
#                     W.get_col_row(installation_rows)
#                 )
#         else:
#             installation_columns = [W.get_col_row([
#                 W.get_blank_flow(),
#                 W.get_text(
#                     'body',
#                     'There Are No WordPress Installations found for User: ' +
#                     getpass.getuser(),
#                     'center'),
#                 W.get_blank_flow()
#             ])]
#         installation_pile = U.Pile(installation_columns)
#         filler = U.Filler(installation_pile, 'middle')
#         self.app.frame.contents.__setitem__('body', [filler, None])
#         time.sleep(1)
#         if installations:
#             self.app.frame.set_focus('body')
#         else:
#             self.app.frame.set_focus('footer')
#         self.app.loop.draw_screen()


# class GetWpConfig(Default):
#     """Creates the specific body widget for the view of the same name"""

#     def __init__(self, app, initial_text, user_args=None,
#                  calling_view=None, progress_bar=False):
#         super(GetWpConfig, self).__init__(
#             app, initial_text, progress_bar=progress_bar)
#         self.log.debug("user_args: %s, calling_view: %s", user_args, calling_view)

#     def after_action(self, wp_config):
#         """Updates the view's body in response to the
#         views action_on_load function
#         """

#         self.log.debug(' wp_config : %s', wp_config)
#         directives_list = [
#             W.get_col_row([
#                 W.get_blank_flow(),
#                 (10, U.AttrMap(W.get_text(
#                     'header',
#                     'Type',
#                     'center'), 'header')),
#                 U.AttrMap(W.get_text('header', 'Name', 'center'), 'header'),
#                 ('weight', 2, U.AttrMap(W.get_text(
#                     'header',
#                     'Value',
#                     'left'), 'header')),
#                 W.get_blank_flow()
#                 ])]
#         for directive in wp_config.wp_config_directive_list:
#             if 'DB_NAME' in str(directive['name']):
#                 self.app.state.active_installation['db_name'] = str(
#                     directive['value']
#                 )
#             button = widgets.WpConfigValueMap(
#                 self.app,
#                 'default',
#                 on_enter=self.app.views.actions.wp_config.set_wp_config,
#                 user_data={'directive_name': str(directive['name'])},
#                 edit_text=str(directive['value']),
#                 align='left')
#             row_items = [
#                 W.get_blank_flow(),
#                 (10, W.get_text('default', str(directive['type']), 'center')),
#                 W.get_text('default', str(directive['name']), 'center'),
#                 ('weight', 2, button),
#                 W.get_blank_flow()
#             ]
#             row = W.get_col_row(row_items)
#             directives_list.append(row)
#         add_option_value_button = widgets.WpConfigValueMap(
#             self.app,
#             'underline',
#             body_widget=self,
#             align="left",
#             on_enter=self.app.views.GetWpConfig.start)
#         add_option_name_button = widgets.WpConfigValueMap(
#             self,
#             'underline',
#             user_data={'option_value_widget': add_option_value_button},
#             align='left')
#         directives_list.extend([
#             W.get_div(),
#             W.get_div()
#         ])
#         directives_list.extend([
#             W.get_col_row([
#                 W.get_blank_flow(),
#                 ('weight', 3, U.AttrMap(
#                     W.get_text('header', 'Add Option', 'center'),
#                     'header')),
#                 W.get_blank_flow()
#             ]),
#             W.get_div(),
#             W.get_col_row([
#                 W.get_blank_flow(),
#                 (13, W.get_text('default', 'Option Name:', 'right')),
#                 add_option_name_button,
#                 W.get_blank_flow()
#             ]),
#             W.get_col_row([
#                 W.get_blank_flow(),
#                 (13, W.get_text('default', 'Option Value:', 'right')),
#                 add_option_value_button,
#                 W.get_blank_flow()
#             ]),
#             W.get_div(),
#             W.get_div()
#         ])
#         directives_list.append(
#             W.get_col_row([
#                 W.get_blank_flow(),
#                 widgets.BoxButton(
#                     'Re-Salt Config',
#                     on_press=self.app.views.actions.wp_config.re_salt
#                 ),
#                 W.get_blank_flow()
#             ])
#         )
#         self.pile = U.Pile(directives_list)
#         filler = U.Filler(self.pile)
#         self.app.frame.contents.__setitem__('body', [filler, None])
#         time.sleep(1)
#         self.app.loop.draw_screen()


# class Database(Default):
#     """Creates the specific body widget for the view of the same name"""

#     def __init__(self, app, initial_text, user_args=None,
#                  calling_view=None, progress_bar=False):
#         super(Database, self).__init__(
#             app, initial_text, progress_bar=progress_bar)
#         self.log.debug("user_args: %s, calling_view: %s", user_args, calling_view)
#         self.menu_items = self.app.menus.DbSubMenu.items
#         self.response_pile = None

#     def after_action(self, db_info):
#         """Updates the view's body in response to
#         the views action_on_load function
#         """

#         db_info_rows = [
#             W.get_col_row([
#                 U.AttrMap(W.get_text(
#                     'header',
#                     'Database Information',
#                     'center'
#                 ), 'header')
#             ])
#         ]
#         if db_info['size_error']:
#             db_info_rows.append(
#                 W.get_text('default',
#                            "Database Error:\n\n" +
#                            db_info['size_error'] + "\n" +
#                            "Troubleshoot Database Connection",
#                            'center')
#             )
#         elif db_info['check_error']:
#             db_info_rows.append(
#                 W.get_text('default',
#                            "Database Error:\n\n" +
#                            db_info['check_error'] + "\n" +
#                            "Troubleshoot Database Connection",
#                            'center')
#             )
#         else:
#             db_info_rows.append(
#                 W.get_col_row([
#                     U.AttrMap(W.get_text(
#                         'header', 'Database Name',
#                         'center'
#                     ), 'header'),
#                     U.AttrMap(W.get_text(
#                         'header', 'Database Size',
#                         'center'
#                     ), 'header')
#                 ])
#             )
#             db_info_rows.append(W.get_div())
#             db_info_rows.append(
#                 W.get_col_row([
#                     W.get_text('body', str(db_info['name']), 'center'),
#                     W.get_text('body', str(db_info['size']), 'center')
#                 ])
#             )
#             db_info_rows.append(W.get_div())
#             db_info_rows.append(
#                 W.get_col_row([
#                     U.AttrMap(W.get_text(
#                         'header',
#                         'Database Table Check Results',
#                         'center'
#                     ), 'header')
#                 ])
#             )
#             db_info_rows.append(
#                 W.get_col_row([
#                     (5, U.AttrMap(W.get_blank_flow(), 'header')),
#                     U.AttrMap(W.get_text(
#                         'header',
#                         'Table Name',
#                         'left'), 'header'),
#                     (18, U.AttrMap(W.get_text(
#                         'header',
#                         'Check Status',
#                         'center'), 'header')),
#                     (5, U.AttrMap(W.get_blank_flow(), 'header'))
#                 ])
#             )
#             for table in db_info['check_tables']:
#                 db_info_rows.append(
#                     W.get_col_row([
#                         (5, W.get_blank_flow()),
#                         W.get_text('body', table['table_name'], 'left'),
#                         (16, W.get_text(
#                             'body',
#                             table['check_status'],
#                             'center')),
#                         (5, W.get_blank_flow())
#                     ])
#                 )
#         options = [W.get_blank_flow()]
#         for item in self.menu_items:
#             if 'action' in item[1].keys():
#                 action_class = getattr(
#                     self.app.views.actions, item[1]['action_class'])
#                 action = getattr(action_class, item[1]['action'])
#                 options.append((
#                     len(item[0].lstrip().rstrip()) + 8,
#                     widgets.BoxButton(
#                         item[0],
#                         on_press=action,
#                         strip_padding=True)))
#             if 'view' in item[1].keys():
#                 action = self.app.views.activate
#                 options.append((
#                     len(item[0].lstrip().rstrip()) + 8,
#                     widgets.BoxButton(
#                         item[0],
#                         on_press=action,
#                         user_data=item[1],
#                         strip_padding=True)))
#         options.append(W.get_blank_flow())
#         db_info_rows.extend([
#             W.get_div(),
#             W.get_div(),
#             W.get_col_row(options)
#         ])
#         db_info_pile = U.Pile(db_info_rows)
#         db_info_wrapper = W.get_col_row([
#             W.get_blank_flow(),
#             ('weight', 3, db_info_pile),
#             W.get_blank_flow()
#         ])
#         outer_pile = U.Pile([
#             W.get_div(),
#             db_info_wrapper,
#             W.get_div()
#         ])
#         filler = U.Filler(outer_pile, 'middle')
#         self.app.frame.contents.__setitem__('body', [filler, None])
#         time.sleep(2)
#         self.app.loop.draw_screen()

#     def show_database_action_response(self, response_text=None):
#         """Displays response from plugin-actions"""
#         response_text = [
#             W.get_col_row([
#                 W.get_blank_flow(),
#                 U.AttrMap(W.get_text('header', 'Result', 'center'), 'header'),
#                 W.get_blank_flow()
#             ]),
#             W.get_div()
#         ]
#         self.response_pile = U.Pile(response_text)
#         filler = U.Filler(self.response_pile)
#         self.app.frame.contents.__setitem__('body', [filler, None])
#         time.sleep(1)
#         self.app.loop.draw_screen()

#     def update_view(self, wpcli_output):
#         """Updates the view from pipe"""

#         self.log.debug("Update: %s", wpcli_output)
#         if not wpcli_output:
#             self.app.loop.remove_watch_pipe(self.app.wpcli_pipe)
#         if self.response_pile:
#             self.response_pile.contents.append((
#                 W.get_col_row([
#                     W.get_blank_flow(),
#                     W.get_text('default', wpcli_output, 'left'),
#                     W.get_blank_flow()
#                 ]), ('weight', 1)))

#     def after_response(self):
#         """Redirects to plugin_list after response"""
#         time.sleep(2)
#         self.app.views.actions.database.get_database_information()


# class DbImport(Default):
#     """Creates the specific body widget for the view of the same name"""

#     def __init__(self, app, initial_text, user_args=None,
#                  calling_view=None, progress_bar=False):
#         super(DbImport, self).__init__(
#             app, initial_text, progress_bar=progress_bar)
#         self.log.debug("user_args: %s, calling_view: %s", user_args, calling_view)

#     def after_action(self, import_list):
#         """Displays list of imports available"""
#         import_rows = []
#         if import_list:
#             for item in import_list:
#                 import_rows.append(
#                     W.get_col_row([
#                         W.get_blank_flow(),
#                         ('weight', 3, widgets.BoxButton(
#                             item,
#                             on_press=self.app.views.actions.database.import_db,
#                             user_data=item)),
#                         W.get_blank_flow()
#                     ])
#                 )
#         import_edit = widgets.DbImportEditMap(
#             self.app,
#             'body',
#             edit_text=self.app.state.homedir,
#             align='left',
#             on_enter=self.app.views.actions.database.import_db,
#             caption='Other Import Path: ')
#         import_edit_linebox = W.get_line_box(import_edit, '')
#         import_edit_row = W.get_col_row([
#             W.get_blank_flow(),
#             ('weight', 1, import_edit_linebox),
#             W.get_blank_flow()
#         ])
#         import_rows.append(import_edit_row)
#         import_list_box = W.get_list_box(import_rows)[0]
#         # pile = U.Pile(import_rows)
#         # filler = U.Filler(pile, 'middle')
#         self.app.frame.contents.__setitem__('body', [import_list_box, None])
#         time.sleep(1)
#         self.app.loop.draw_screen()

#     def after_import(self, result):
#         """Updates the view's body in response to
#         wp-cli's import function
#         """
#         self.log.debug('Result: %s', result)
#         if result:
#             text = result
#         else:
#             text = "Database import failed"
#         main_text = W.get_text(
#             'body',
#             text,
#             'center')
#         pile = U.Pile([main_text])
#         filler = U.Filler(pile, 'middle')
#         self.app.frame.contents.__setitem__('body', [filler, None])
#         time.sleep(1)
#         self.app.loop.draw_screen()


# class DbOptimize(Default):
#     """Creates the specific body widget for the view of the same name"""

#     def __init__(self, app, initial_text, user_args=None,
#                  calling_view=None, progress_bar=False):
#         super(DbOptimize, self).__init__(
#             app, initial_text, progress_bar=progress_bar)
#         self.log.debug("user_args: %s, calling_view: %s", user_args, calling_view)

#     def after_action(self, result):
#         """Updates the view's body in response to
#         the views action_on_load function
#         """
#         self.log.debug('Result: %s', result)
#         if result:
#             text = result
#         else:
#             text = "Database Optimize failed"
#         main_text = W.get_text(
#             'body',
#             text,
#             'center')
#         pile = U.Pile([main_text])
#         filler = U.Filler(pile, 'middle')
#         self.app.frame.contents.__setitem__('body', [filler, None])
#         time.sleep(1)
#         self.app.loop.draw_screen()


# class DbRepair(Default):
#     """Creates the specific body widget for the view of the same name"""

#     def __init__(self, app, initial_text, user_args=None,
#                  calling_view=None, progress_bar=False):
#         super(DbRepair, self).__init__(
#             app, initial_text, progress_bar=progress_bar)
#         self.log.debug("user_args: %s, calling_view: %s", user_args, calling_view)

#     def after_action(self, result):
#         """Updates the view's body in response to
#         the views action_on_load function
#         """
#         self.log.debug('Result: %s', result)
#         if result:
#             text = result
#         else:
#             text = "Database Repair failed"
#         main_text = W.get_text(
#             'body',
#             text,
#             'center')
#         pile = U.Pile([main_text])
#         filler = U.Filler(pile, 'middle')
#         self.app.frame.contents.__setitem__('body', [filler, None])
#         time.sleep(1)
#         self.app.loop.draw_screen()


# class DbSearch(Default):
#     """Creates the specific body widget for the view of the same name"""

#     def __init__(self, app, initial_text, user_args=None,
#                  calling_view=None, progress_bar=False):
#         super(DbSearch, self).__init__(
#             app, initial_text, progress_bar=progress_bar)
#         self.log.debug("user_args: %s, calling_view: %s", user_args, calling_view)

#     def define_widget(self):
#         self.log.debug(' initial_text : %s', self.metadata['initial_text'])
#         db_search_row = W.get_col_row([
#             W.get_blank_flow(),
#             (
#                 'weight',
#                 3,
#                 widgets.DbSearchEditMap(
#                     self.app,
#                     self,
#                     'body',
#                     caption='Database Search Query: ',
#                     on_enter=self.app.views.actions.database.db_search,
#                     align='left')),
#             W.get_blank_flow()
#         ])
#         return U.Filler(db_search_row, 'middle')

#     def after_action(self, db_search_results, query):
#         """Displays after_action contents"""
#         self.log.debug('Search Results: %s', db_search_results)
#         search_result_rows = [
#             W.get_col_row([
#                 W.get_blank_flow(),
#                 ('weight', 4, U.AttrMap(W.get_text(
#                     'header', 'DB Search Results for: ', 'right'), 'header')),
#                 ('weight', 4, U.AttrMap(W.get_text(
#                     'header', query, 'left'), 'header')),
#                 W.get_blank_flow()]),
#             W.get_col_row([
#                 W.get_blank_flow(),
#                 ('weight', 4, U.AttrMap(W.get_blank_flow(), 'header')),
#                 ('weight', 4, U.AttrMap(W.get_blank_flow(), 'header')),
#                 W.get_blank_flow()]),
#             W.get_col_row([
#                 W.get_blank_flow(),
#                 ('weight', 1, U.AttrMap(W.get_text(
#                     'header', 'Row', 'center'), 'header')),
#                 ('weight', 1, U.AttrMap(W.get_text(
#                     'header', 'Table', 'center'), 'header')),
#                 ('weight', 2, U.AttrMap(W.get_text(
#                     'header', 'Column', 'center'), 'header')),
#                 ('weight', 4, U.AttrMap(W.get_text(
#                     'header', 'Value', 'center'), 'header')),
#                 W.get_blank_flow()
#             ]),
#         ]
#         for result in db_search_results:
#             search_result_rows.append(
#                 W.get_col_row([
#                     W.get_blank_flow(),
#                     ('weight', 1, W.get_text(
#                         'default', result['row'], 'center')),
#                     ('weight', 1, W.get_text(
#                         'default', result['table'], 'center')),
#                     ('weight', 2, W.get_text(
#                         'default', result['column'], 'center')),
#                     ('weight', 4, W.get_text(
#                         'default', result['value'], 'center')),
#                     W.get_blank_flow()
#                 ])
#             )
#         pile = U.Pile(search_result_rows)
#         filler = U.Filler(pile, 'middle')
#         self.app.frame.contents.__setitem__('body', [filler, None])
#         time.sleep(1)
#         self.app.loop.draw_screen()


# class SearchReplace(Default):
#     """Creates the specific body widget for the view of the same name"""

#     def __init__(self, app, initial_text, user_args=None,
#                  calling_view=None, progress_bar=False):
#         super(SearchReplace, self).__init__(
#             app, initial_text, progress_bar=progress_bar)
#         self.log.debug("user_args: %s, calling_view: %s", user_args, calling_view)

#     def define_widget(self):
#         self.log.debug(' initial_text : %s', self.metadata['initial_text'])
#         self.sr_pile = widgets.SRSearchEditMap(self.app)
#         return U.Filler(self.sr_pile, 'middle')

#     def after_dry_run(self, search_term, replace_term, results, db_export):
#         """Displays the Search-replace dry-run results"""

#         self.log.debug('results: %s', results)
#         dry_run_rows = []
#         if not db_export:
#             db_export_msg = self.app.settings.messages['db_export_warning']
#             db_export_msg = db_export_msg + \
#                 self.app.settings.messages['mycophagists']
#             self.log.debug('db_export_message: %s', db_export_msg)
#             dry_run_rows.append(
#                 W.get_col_row([
#                     W.get_blank_flow(),
#                     U.AttrMap(
#                         W.get_text(
#                             'flashing', db_export_msg, 'center'),
#                         'flashing'),
#                     W.get_blank_flow()
#                 ])
#             )
#             dry_run_rows.append(W.get_div())
#         header_string = 'There are ' + str(results['count']) + \
#             ' replacements to be made'
#         dry_run_rows.append(
#             W.get_col_row([
#                 W.get_blank_flow(),
#                 U.AttrMap(W.get_blank_flow(), 'header'),
#                 U.AttrMap(
#                     W.get_text(
#                         'header',
#                         header_string,
#                         'center'),
#                     'header'),
#                 U.AttrMap(W.get_blank_flow(), 'header'),
#                 W.get_blank_flow()
#             ])
#         )
#         if str(results['count']) == '0':
#             dry_run_rows.append(
#                 W.get_col_row([
#                     W.get_blank_flow(),
#                     widgets.BoxButton(
#                         'New Search & Replace',
#                         on_press=self.app.views.activate,
#                         user_data='SearchReplace'),
#                     W.get_blank_flow()
#                 ])
#             )
#         if str(results['count']) != '0':
#             dry_run_rows.append(
#                 W.get_col_row([
#                     W.get_blank_flow(),
#                     U.AttrMap(
#                         W.get_text(
#                             'header', 'Table', 'center'),
#                         'header'),
#                     U.AttrMap(
#                         W.get_text(
#                             'header', 'Column', 'center'),
#                         'header'),
#                     U.AttrMap(
#                         W.get_text(
#                             'header', 'Count', 'center'),
#                         'header'),
#                     W.get_blank_flow()
#                 ])
#             )
#             for result in results['results']:
#                 if not isinstance(result, str):
#                     if int(result['count']) > 0:
#                         dry_run_rows.append(
#                             W.get_col_row([
#                                 W.get_blank_flow(),
#                                 U.AttrMap(
#                                     W.get_text(
#                                         'default',
#                                         result['table'],
#                                         'center'),
#                                     'default'),
#                                 U.AttrMap(
#                                     W.get_text(
#                                         'default',
#                                         result['column'],
#                                         'center'),
#                                     'default'),
#                                 U.AttrMap(
#                                     W.get_text(
#                                         'default',
#                                         result['count'],
#                                         'center'),
#                                     'default'),
#                                 W.get_blank_flow()
#                             ])
#                         )
#             dry_run_rows.append(W.get_div())
#             sr_replace = self.app.views.actions.database.sr_replace
#             self.log.debug('sr_replace: %s', sr_replace)
#             dry_run_rows.append(
#                 W.get_col_row([
#                     W.get_blank_flow(),
#                     widgets.BoxButton(
#                         'Perform Replacement',
#                         on_press=sr_replace,
#                         user_data=[search_term, replace_term]),
#                     widgets.BoxButton(
#                         'New Search & Replace',
#                         on_press=self.app.views.activate,
#                         user_data='SearchReplace'),
#                     W.get_blank_flow()
#                 ])
#             )
#         pile = U.Pile(dry_run_rows)
#         if not db_export:
#             self.app.loop.set_alarm_in(
#                 5, self.app.views.actions.change_text_attr,
#                 user_data=[
#                     pile.contents[0][0].contents[1][0].original_widget,
#                     'alert'
#                 ])
#         filler = U.Filler(pile, 'middle')
#         self.app.frame.contents.__setitem__('body', [filler, None])
#         time.sleep(1)
#         self.app.loop.draw_screen()

#     def after_replacement(self, results):
#         """Displays search-replace results after replacement"""

#         self.log.debug("After Replacement: %s", results)
#         replaced_rows = []
#         if results:
#             replaced_rows.append(
#                 W.get_col_row([
#                     W.get_blank_flow(),
#                     U.AttrMap(W.get_blank_flow(), 'header'),
#                     U.AttrMap(
#                         W.get_text(
#                             'header',
#                             'There were ' + str(results['count']) +
#                             ' Replacements made',
#                             'center'),
#                         'header'),
#                     U.AttrMap(W.get_blank_flow(), 'header'),
#                     W.get_blank_flow()
#                 ])
#             )
#             replaced_rows.append(
#                 W.get_col_row([
#                     W.get_blank_flow(),
#                     U.AttrMap(
#                         W.get_text(
#                             'header', 'Table', 'center'),
#                         'header'),
#                     U.AttrMap(
#                         W.get_text(
#                             'header', 'Column', 'center'),
#                         'header'),
#                     U.AttrMap(
#                         W.get_text(
#                             'header', 'Count', 'center'),
#                         'header'),
#                     W.get_blank_flow()
#                 ])
#             )
#             self.log.debug('results["results"]: %s', results['results'])
#             for result in results['results']:
#                 if not isinstance(result, str):
#                     self.log.debug('result["count"]: %s', result['count'])
#                     if int(result['count']) > 0:
#                         replaced_rows.append(
#                             W.get_col_row([
#                                 W.get_blank_flow(),
#                                 U.AttrMap(
#                                     W.get_text(
#                                         'default', result['table'], 'center'),
#                                     'default'),
#                                 U.AttrMap(
#                                     W.get_text(
#                                         'default', result['column'], 'center'),
#                                     'default'),
#                                 U.AttrMap(
#                                     W.get_text(
#                                         'default', result['count'], 'center'),
#                                     'default'),
#                                 W.get_blank_flow()
#                             ])
#                         )
#             replaced_rows.append(W.get_div())
#             replaced_rows.append(
#                 W.get_col_row([
#                     W.get_blank_flow(),
#                     widgets.BoxButton(
#                         'Undo',
#                         on_press=self.app.views.activate,
#                         user_data={
#                             'view': 'RevertChanges',
#                             'return_view': self.app.views.Database}),
#                     W.get_blank_flow()
#                 ])
#             )
#         pile = U.Pile(replaced_rows)
#         filler = U.Filler(pile, 'middle')
#         self.app.frame.contents.__setitem__('body', [filler, None])
#         time.sleep(1)
#         self.app.loop.draw_screen()


# class Themes(Default):
#     """Creates the specific body widget for the view of the same name"""

#     def __init__(self, app, initial_text, user_args=None,
#                  calling_view=None, progress_bar=False):
#         super(Themes, self).__init__(
#             app, initial_text, progress_bar=progress_bar)
#         self.log.debug("user_args: %s, calling_view: %s", user_args, calling_view)
#         self.parser = HTMLParser()
#         self.response_pile = None

#     # def update_progress_bar(self, progress):
#     #     self.progress = 0
#     #     while self.progress < 100:
#     #         self.log.debug('Progress: %s', int(self.progress))
#     #         self.progress = self.progress + 10
#     #         self.progress_bar.set_completion(int(self.progress))
#     #         self.app.loop.draw_screen()
#     #         time.sleep(.250)
#     #     self.progress_bar.set_completion(100)
#     #     self.app.loop.remove_watch_pipe(self.app.action_pipe)
#     #     self.app.loop.draw_screen()

#     def after_action(self, theme_list):
#         """Displays after_action contents"""
#         theme_rows = [
#             U.AttrMap(W.get_col_row([
#                 W.get_blank_flow(),
#                 W.get_text(
#                     'header', 'Theme Name', 'center'),
#                 W.get_text(
#                     'header', 'Theme Title', 'center'),
#                 W.get_text(
#                     'header', 'Theme Version', 'center'),
#                 W.get_text(
#                     'header', 'Theme Status', 'center'),
#                 W.get_text(
#                     'header', 'Update Status', 'center'),
#                 W.get_text(
#                     'header', 'Update Version', 'center'),
#                 ('weight', 4, W.get_text(
#                     'header', 'Options', 'center')),
#                 W.get_blank_flow()
#             ]), 'header')
#         ]
#         for theme in theme_list:
#             theme_row = [
#                 W.get_blank_flow(),
#                 W.get_text(
#                     'default', '\n' + theme['name'] + '\n', 'center'),
#                 W.get_text(
#                     'default', '\n' + theme['title'] + '\n', 'center'),
#                 W.get_text(
#                     'default', '\n' + theme['version'] + '\n', 'center'),
#                 W.get_text(
#                     'default', '\n' + theme['status'] + '\n', 'center'),
#                 W.get_text(
#                     'default', '\n' + theme['update'] + '\n', 'center'),
#             ]
#             if theme['update'] == 'available':
#                 theme_row.append(
#                     W.get_text(
#                         'default', '\n' + theme['update_version'] + '\n',
#                         'center'),
#                 )
#             else:
#                 theme_row.append(
#                     W.get_blank_flow()
#                 )
#             theme_row.extend([
#                 widgets.BoxButton(
#                     'Details',
#                     on_press=self.app.views.actions.themes.details,
#                     user_data=theme),
#                 widgets.BoxButton(
#                     'Uninstall',
#                     on_press=self.app.views.actions.themes.uninstall,
#                     user_data=theme)
#             ])
#             if theme['update'] == 'available':
#                 theme_row.append(widgets.BoxButton(
#                     'Update',
#                     on_press=self.app.views.actions.themes.update,
#                     user_data=theme))
#             else:
#                 theme_row.append(
#                     W.get_blank_flow()
#                 )

#             if theme['status'] == 'inactive':
#                 theme_row.append(widgets.BoxButton(
#                     'Activate',
#                     on_press=self.app.views.actions.themes.activate,
#                     user_data=theme))
#             else:
#                 theme_row.append(
#                     W.get_blank_flow()
#                 )

#             theme_row.append(
#                 W.get_blank_flow()
#             )
#             theme_rows.append(
#                 W.get_col_row(theme_row)
#             )
#         theme_rows.append(
#             W.get_div()
#         )
#         theme_rows.append(
#             W.get_col_row([
#                 W.get_blank_flow(),
#                 widgets.BoxButton(
#                     'Update All',
#                     on_press=self.app.views.actions.themes.update_all,
#                     user_data='--all'),
#                 W.get_blank_flow()
#             ])
#         )
#         theme_rows.append(
#             W.get_col_row([
#                 W.get_blank_flow(),
#                 W.get_text(
#                     'body', 'Install Theme:', 'right'
#                 ),
#                 widgets.DbSearchEditMap(
#                     self.app,
#                     self,
#                     'underline',
#                     on_enter=self.app.views.actions.themes.install_theme,
#                     align='left'),
#                 W.get_blank_flow()
#             ]))
#         theme_pile = U.Pile(theme_rows)
#         filler = U.Filler(theme_pile)
#         self.app.frame.contents.__setitem__('body', [filler, None])
#         # time.sleep(1)
#         # self.app.loop.draw_screen()

#     def show_theme_details(self, theme_details):
#         """Shows Theme Details"""
#         self.log.debug('Theme Details: %s', theme_details)
#         theme_name = ''
#         theme_title = ''
#         theme_version = ''
#         if 'name' in theme_details.keys():
#             theme_name = theme_details['name']
#             del theme_details['name']
#         if 'title' in theme_details.keys():
#             theme_title = theme_details['title']
#             del theme_details['title']
#         if 'version' in theme_details.keys():
#             theme_version = theme_details['version']
#             del theme_details['version']
#         theme_details_rows = [
#             W.get_col_row([
#                 W.get_blank_flow(),
#                 U.AttrMap(
#                     W.get_text('header', theme_name, 'center'), 'header'),
#                 U.AttrMap(
#                     W.get_text('header', theme_title, 'center'), 'header'),
#                 U.AttrMap(
#                     W.get_text(
#                         'header', theme_version, 'center'), 'header'),
#                 W.get_blank_flow()
#             ])
#         ]
#         theme_details_rows.append(W.get_div())
#         for key, value in theme_details.items():
#             if isinstance(value, list):
#                 value = " | ".join(value)
#             if value:
#                 theme_details_rows.append(
#                     W.get_col_row([
#                         W.get_blank_flow(),
#                         (15, W.get_text(
#                             'default', str(key).capitalize(), 'left')),
#                         (3, W.get_text('default', ' : ', 'center')),
#                         W.get_text(
#                             'default', self.parser.unescape(value), 'left'),
#                         W.get_blank_flow()
#                     ])
#                 )
#         theme_details_pile = U.Pile(theme_details_rows)
#         filler = U.Filler(theme_details_pile)
#         self.app.frame.contents.__setitem__('body', [filler, None])
#         time.sleep(1)
#         self.app.loop.draw_screen()

#     def show_theme_action_response(self):
#         """Shows theme-action Response"""
#         processing = W.get_text('body', 'Processing request...', 'center')
#         response_text = [
#             W.get_col_row([
#                 W.get_blank_flow(),
#                 U.AttrMap(W.get_text('header', 'Result', 'center'), 'header'),
#                 W.get_blank_flow()
#                 ]),
#             W.get_div(),
#             processing
#         ]
#         self.response_pile = U.Pile(response_text)
#         filler = U.Filler(self.response_pile)
#         self.app.frame.contents.__setitem__('body', [filler, None])
#         time.sleep(1)
#         self.app.loop.draw_screen()

#     def update_view(self, wpcli_output):
#         """Updates the view from pipe"""

#         self.log.debug("Update: %s", wpcli_output)
#         if not wpcli_output:
#             self.app.loop.remove_watch_pipe(self.app.wpcli_pipe)
#         self.response_pile.contents.append((
#             W.get_col_row([
#                 W.get_blank_flow(),
#                 W.get_text('default', wpcli_output, 'left'),
#                 W.get_blank_flow()
#             ]), ('weight', 1)))

#     def after_response(self):
#         """After response is displayed, redirect to theme list"""
#         self.app.views.actions.themes.get_theme_list()


# class InstallThemes(Default):
#     """Creates the specific body widget for the view of the same name"""

#     def __init__(self, app, initial_text, user_args=None,
#                  calling_view=None, progress_bar=False):
#         super(InstallThemes, self).__init__(
#             app, initial_text, progress_bar=progress_bar)
#         self.log.debug("user_args: %s, calling_view: %s", user_args, calling_view)

#     def define_widget(self):
#         """shows initial widget"""

#         self.log.debug(' initial_text : %s', self.metadata['initial_text'])
#         theme_install_edit = widgets.DbSearchEditMap(
#             self.app,
#             self,
#             'body',
#             caption='Enter Theme Name to Install: ',
#             on_enter=self.app.views.actions.themes.install,
#             align='center')

#         return U.Filler(theme_install_edit, 'middle')


# class Plugins(Default):
#     """Creates the specific body widget for the view of the same name"""

#     def __init__(self, app, initial_text, user_args=None,
#                  calling_view=None, progress_bar=False):
#         super(Plugins, self).__init__(
#             app, initial_text, progress_bar=progress_bar)
#         self.log.debug("user_args: %s, calling_view: %s", user_args, calling_view)
#         self.parser = HTMLParser()
#         self.deactivated_plugins = ''
#         self.response_pile = None

#     def update_progress_bar(self, progress):
#         """Updates the display of Progress Bar"""

#         self.progress = 0
#         while self.progress < 100:
#             self.log.debug('Progress: %s', int(self.progress))
#             self.progress = self.progress + 10
#             self.progress_bar.set_completion(int(self.progress))
#             self.app.loop.draw_screen()
#             time.sleep(.250)
#         self.progress_bar.set_completion(100)
#         self.app.loop.remove_watch_pipe(self.app.action_pipe)
#         self.app.loop.draw_screen()

#     def after_action(self, plugin_list):
#         """Displays after_action contents"""
#         plugin_rows = [
#             U.AttrMap(W.get_col_row([
#                 W.get_blank_flow(),
#                 ('weight', 2, W.get_text(
#                     'header', 'Plugin Name', 'center')),
#                 W.get_text(
#                     'header', 'Status', 'center'),
#                 W.get_text(
#                     'header', 'Version', 'center'),
#                 W.get_text(
#                     'header', 'Update Status', 'center'),
#                 W.get_text(
#                     'header', 'Update Version', 'center'),
#                 ('weight', 4, W.get_text(
#                     'header', 'Options', 'center')),
#                 W.get_blank_flow()
#             ]), 'header')
#         ]
#         for plugin in plugin_list:
#             plugin_row = [
#                 W.get_blank_flow(),
#                 ('weight', 2, W.get_text(
#                     'default', '\n' + plugin['name'] + '\n', 'center')),
#                 W.get_text(
#                     'default', '\n' + plugin['status'] + '\n', 'center'),
#                 W.get_text(
#                     'default', '\n' + plugin['version'] + '\n', 'center'),
#                 W.get_text(
#                     'default', '\n' + plugin['update'] + '\n', 'center'),
#             ]
#             if plugin['update'] == 'available':
#                 plugin_row.append(
#                     W.get_text(
#                         'default', '\n' + plugin['update_version'] + '\n',
#                         'center'),
#                 )
#             else:
#                 plugin_row.append(
#                     W.get_blank_flow()
#                 )
#             plugin_row.extend([
#                 widgets.BoxButton(
#                     'Details',
#                     on_press=self.app.views.actions.plugins.details,
#                     user_data=[plugin]),
#                 widgets.BoxButton(
#                     'Uninstall',
#                     on_press=self.app.views.actions.plugins.uninstall,
#                     user_data=[plugin])
#             ])
#             if plugin['update'] == 'available':
#                 plugin_row.append(widgets.BoxButton(
#                     'Update',
#                     on_press=self.app.views.actions.plugins.update,
#                     user_data=[plugin]))
#             else:
#                 plugin_row.append(
#                     W.get_blank_flow()
#                 )

#             if plugin['status'] == 'inactive':
#                 plugin_row.append(widgets.BoxButton(
#                     'Activate',
#                     on_press=self.app.views.actions.plugins.activate,
#                     user_data=[plugin]))
#             else:
#                 plugin_row.append(widgets.BoxButton(
#                     'Deactivate',
#                     on_press=self.app.views.actions.plugins.deactivate,
#                     user_data=[plugin]))

#             plugin_row.append(
#                 W.get_blank_flow()
#             )
#             plugin_rows.append(
#                 W.get_col_row(plugin_row)
#             )
#         plugin_rows.append(
#             W.get_div()
#         )
#         if self.deactivated_plugins:
#             act_deact_all_plugins = widgets.BoxButton(
#                 'Re-Activate All',
#                 on_press=self.app.views.actions.plugins.reactivate,
#                 user_data=self.deactivated_plugins)
#         else:
#             act_deact_all_plugins = widgets.BoxButton(
#                 'Deactivate All',
#                 on_press=self.app.views.actions.plugins.deactivate_all,
#                 user_data='--all')
#         plugin_rows.append(
#             W.get_col_row([
#                 W.get_blank_flow(),
#                 act_deact_all_plugins,
#                 widgets.BoxButton(
#                     'Update All',
#                     on_press=self.app.views.actions.plugins.update_all,
#                     user_data='--all'),
#                 W.get_blank_flow()
#             ])
#         )
#         plugin_rows.append(
#             W.get_col_row([
#                 W.get_blank_flow(),
#                 W.get_text(
#                     'body', 'Install Plugin:', 'right'
#                 ),
#                 widgets.DbSearchEditMap(
#                     self.app,
#                     self,
#                     'underline',
#                     on_enter=self.app.views.actions.plugins.install,
#                     align='left'),
#                 W.get_blank_flow()
#             ]))
#         self.pile = U.Pile(plugin_rows)
#         filler = U.Filler(self.pile)
#         self.app.frame.contents.__setitem__('body', [filler, None])
#         time.sleep(1)
#         self.app.loop.draw_screen()

#     def show_plugin_details(self, plugin_details):
#         """Show Plugin Details"""
#         self.log.debug('Plugin Details: %s', plugin_details)
#         plugin_name = ''
#         plugin_title = ''
#         plugin_version = ''
#         if 'name' in plugin_details.keys():
#             plugin_name = plugin_details['name']
#             del plugin_details['name']
#         if 'title' in plugin_details.keys():
#             plugin_title = plugin_details['title']
#             del plugin_details['title']
#         if 'version' in plugin_details.keys():
#             plugin_version = plugin_details['version']
#             del plugin_details['version']
#         plugin_details_rows = [
#             W.get_col_row([
#                 W.get_blank_flow(),
#                 U.AttrMap(
#                     W.get_text('header', plugin_name, 'center'), 'header'),
#                 U.AttrMap(
#                     W.get_text('header', plugin_title, 'center'), 'header'),
#                 U.AttrMap(
#                     W.get_text(
#                         'header', plugin_version, 'center'), 'header'),
#                 W.get_blank_flow()
#             ])
#         ]
#         plugin_details_rows.append(W.get_div())
#         for key, value in plugin_details.items():
#             if isinstance(value, list):
#                 value = " | ".join(value)
#             if value:
#                 plugin_details_rows.append(
#                     W.get_col_row([
#                         W.get_blank_flow(),
#                         (15, W.get_text(
#                             'default', str(key).capitalize(), 'left')),
#                         (3, W.get_text('default', ' : ', 'center')),
#                         W.get_text(
#                             'default', self.parser.unescape(value), 'left'),
#                         W.get_blank_flow()
#                     ])
#                 )
#         theme_details_pile = U.Pile(plugin_details_rows)
#         filler = U.Filler(theme_details_pile)
#         self.app.frame.contents.__setitem__('body', [filler, None])
#         time.sleep(1)
#         self.app.loop.draw_screen()

#     def show_plugin_action_response(self, response_text=None):
#         """Displays response from plugin-actions"""
#         response_text = [
#             W.get_col_row([
#                 W.get_blank_flow(),
#                 U.AttrMap(W.get_text('header', 'Result', 'center'), 'header'),
#                 W.get_blank_flow()
#             ]),
#             W.get_div()
#         ]
#         if response_text:
#             result = response_text
#             response_text.append(
#                 W.get_col_row([
#                     W.get_blank_flow(),
#                     W.get_text('default', result, 'left'),
#                     W.get_blank_flow()
#                 ]))
#         self.response_pile = U.Pile(response_text)
#         filler = U.Filler(self.response_pile)
#         self.app.frame.contents.__setitem__('body', [filler, None])
#         time.sleep(1)
#         self.app.loop.draw_screen()

#     def update_view(self, wpcli_output):
#         """Update's view from pipe"""
#         self.log.debug("Update: %s", wpcli_output)
#         if not wpcli_output:
#             self.app.loop.remove_watch_pipe(self.app.wpcli_pipe)
#         self.response_pile.contents.append((
#             W.get_col_row([
#                 W.get_blank_flow(),
#                 W.get_text('default', wpcli_output, 'left'),
#                 W.get_blank_flow()
#             ]), ('weight', 1)))

#     def after_response(self):
#         """Redirects to plugin_list after response"""
#         time.sleep(2)
#         self.app.views.actions.plugins.get_plugin_list()


# class RevertChanges(Default):
#     """Creates the specific body widget for the view of the same name"""

#     def __init__(self, app, initial_text, user_args=None,
#                  calling_view=None, progress_bar=False):
#         super(RevertChanges, self).__init__(
#             app, initial_text, progress_bar=progress_bar)
#         self.log.debug("user_args: %s, calling_view: %s", user_args, calling_view)

#     def after_action(self, revisions):
#         """Displays after_action contents"""
#         self.log.debug('list_of_revisions: %s', revisions)
#         revisions_rows = [
#             W.get_col_row([
#                 W.get_blank_flow(),
#                 U.AttrMap(W.get_text(
#                     'header', 'Revision Time', 'center'), 'header'),
#                 U.AttrMap(W.get_text(
#                     'header', 'Theme(s)', 'center'), 'header'),
#                 U.AttrMap(W.get_text(
#                     'header', 'Plugin(s)', 'center'), 'header'),
#                 U.AttrMap(W.get_text(
#                     'header', 'Database', 'center'), 'header'),
#                 U.AttrMap(W.get_blank_flow(), 'header'),
#                 W.get_blank_flow()
#             ])
#         ]

#         revisions_sorted = OrderedDict(sorted(revisions.items()))
#         for revision_time, revision_data in revisions_sorted.items():
#             revision_datetime = datetime.datetime.strptime(
#                 revision_time,
#                 self.app.settings.datetime['date_string'])
#             revision_time_str = revision_datetime.strftime(
#                 self.app.settings.datetime['string_date'])
#             if 'themes' in revision_data.keys():
#                 themes = W.get_text(
#                     'default',
#                     '\n' + revision_data['themes'] + '\n', 'center')
#             else:
#                 themes = W.get_blank_flow()
#             if 'plugins' in revision_data.keys():
#                 plugins = W.get_text(
#                     'default',
#                     '\n' + revision_data['plugins'] + '\n', 'center')
#             else:
#                 plugins = W.get_blank_flow()
#             if 'databases' in revision_data.keys():
#                 databases = W.get_text(
#                     'default',
#                     '\n' + revision_data['databases'] + '\n', 'center')
#             else:
#                 databases = W.get_blank_flow()

#             restore_button = widgets.BoxButton(
#                 'Restore',
#                 on_press=self.app.views.actions.revisions.restore_revision,
#                 user_data=[revisions_sorted, revision_time]
#             )
#             revisions_rows.append(
#                 W.get_col_row([
#                     W.get_blank_flow(),
#                     W.get_text(
#                         'default', '\n' + revision_time_str + '\n', 'center'),
#                     themes, plugins, databases,
#                     restore_button, W.get_blank_flow()
#                 ])
#             )
#         if not revisions:
#             revisions_rows.append(
#                 W.get_col_row([
#                     W.get_blank_flow(),
#                     W.get_text(
#                         'default',
#                         'No Revisions available for restoration',
#                         'center'),
#                     W.get_blank_flow()
#                 ])
#             )
#         revisions_pile = U.Pile(revisions_rows)
#         filler = U.Filler(revisions_pile)
#         self.app.frame.contents.__setitem__('body', [filler, None])
#         time.sleep(1)
#         self.app.loop.draw_screen()

#     def after_revert(self, result):
#         """Displays results after reverting changes"""
#         revision_time = datetime.datetime.strptime(
#             result['revision'],
#             self.app.settings.datetime['date_string']
#         )
#         revision_time_str = revision_time.strftime(
#             self.app.settings.datetime['string_date']
#         )
#         result_rows = []
#         result_rows.append(W.get_col_row([
#             W.get_blank_flow(),
#             U.AttrMap(
#                 W.get_text(
#                     'header',
#                     'Revision ' + revision_time_str + ' Results', 'center'),
#                 'header'),
#             W.get_blank_flow()
#         ]))
#         for reversion_type, result in result.items():
#             if 'revision' not in reversion_type:
#                 result_rows.append(
#                     W.get_col_row([
#                         W.get_blank_flow(),
#                         W.get_text('default', reversion_type, 'center'),
#                         W.get_text('default', result, 'center'),
#                         W.get_blank_flow()
#                     ])
#                 )
#         self.pile = U.Pile(result_rows)
#         filler = U.Filler(self.pile)
#         self.app.frame.contents.__setitem__('body', [filler, None])
#         time.sleep(1)
#         self.app.loop.draw_screen()
#         self.after_response()

#     def after_response(self):
#         """After response is displayed, redirect to theme list"""
#         active_view = self.app.state.get_state("active_view")
#         if not active_view.return_view == active_view:
#             active_view.return_view.start({"view": active_view.return_view})
#         else:
#             self.app.views.activate(self, {"view": "Home"})


# class Users(Default):
#     """Creates the specific body widget for the view of the same name"""

#     def __init__(self, app, initial_text, user_args=None,
#                  calling_view=None, progress_bar=False):
#         super(Users, self).__init__(
#             app, initial_text, progress_bar=progress_bar)
#         self.log.debug("user_args: %s, calling_view: %s", user_args, calling_view)


# class Core(Default):
#     """Creates the specific body widget for the view of the same name"""

#     def __init__(self, app, initial_text, user_args=None,
#                  calling_view=None, progress_bar=False):
#         super(Core, self).__init__(
#             app, initial_text, progress_bar=progress_bar)
#         self.log.debug("user_args: %s, calling_view: %s", user_args, calling_view)


# class Quit(Default):
#     """Creates the specific body widget for the view of the same name"""

#     def __init__(self, app, initial_text, user_args=None,
#                  calling_view=None, progress_bar=False):
#         super(Quit, self).__init__(
#             app, initial_text, progress_bar=progress_bar)
#         self.log.debug("user_args: %s, calling_view: %s", user_args, calling_view)

#     def define_widget(self):
#         self.log.debug(' Body Widget View Name: %s', self.app.state.active_view.name)
#         self.log.debug(' Previous View Name: %s', self.app.state.previous_view.name)
#         self.app.settings.display['menu_enabled'] = True
#         quit_list = [
#             W.get_div(),
#             W.get_col_row([
#                 widgets.BoxButton('Yes', on_press=self.app.exit),
#                 widgets.BoxButton('No', on_press=self.app.state.go_back)
#             ]),
#             W.get_div()]
#         quit_box = W.get_list_box(quit_list)[0]
#         return W.centered_list_box(
#             quit_box,
#             'Are You Sure You Want to Quit?',
#             len(quit_list) + 4)
