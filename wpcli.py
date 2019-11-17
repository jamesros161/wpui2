import os
import shlex
import subprocess
import time
import json

class Installations():
    def __init__(self):
        self.app = None
        self.log = None
        self.meta = None

    def get_installation_details(self, app, meta, installations):
        """Getter for installation details"""
        self.app = app
        self.log = app.log
        self.meta = meta
        self.log.debug('Start get_installation_details')

        progress = 0
        if installations:
            progress_sections = 100 / len(installations)
        else:
            progress_sections = 100
        progress_increments = progress_sections

        while 'action_pipe' not in self.meta.user_data.keys():
            time.sleep(1)

        for installation in installations:
            self.log.debug('installation: %s', installation)

            db_check_data, db_check_error = call(
                self.app,
                'db check',
                install_path=installation['directory'])

            if db_check_data:
                self.app.log.debug('db_check_data: %s', db_check_data)
                data = db_check_data.splitlines()
                for line in data:
                    if '_options' in line and 'OK' in line:
                        # L.debug('Line: %s', line)
                        installation['valid_wp_options'] = True
                        homedata, _ = call(
                            self.app,
                            'option get home',
                            install_path=installation['directory'])
                        self.app.log.debug('homedata: %s', homedata)
                        if homedata:
                            installation['home_url'] = homedata.rstrip()
                    if 'Success: Database checked' in line:
                        installation['wp_db_check_success'] = True
            if db_check_error:
                installation['wp_db_error'] = db_check_error
            progress = progress + progress_increments
            os.write(
                self.meta.user_data['action_pipe'],
                str.encode(str(progress)))

class Themes():
    def __init__(self):
        self.app = None
        self.log = None
        self.meta = None

    def get_themes(self, app, meta):
        self.app = app
        self.log = app.log
        self.meta = meta

        while 'action_pipe' not in self.meta.user_data.keys():
            time.sleep(1)

        install_path = self.app.state.active_installation['directory']
        themes, error = call(
            app, 'theme list --format=json', install_path=install_path)
        self.log.debug(themes)

        themes = json.loads(themes)
        self.app.actions.apis.api_vars['wpcli']['themes'] = themes

        progress = 100
        os.write(
            self.meta.user_data['action_pipe'],
            str.encode(str(progress)))

    def activate(self, app, meta):
        self.app = app
        self.log = app.log

        if isinstance(meta, dict):
            user_data = meta
        else:
            user_data = meta.user_data

        install_path = self.app.state.active_installation['directory']

        theme_name = user_data['user_data']['name']

        result, error = call(
            app, 'theme activate ' + theme_name, install_path=install_path)

        self.log.debug('Result: %s\nError:%s', result, error)

        return {'result': result, 'error': error}


def call(app, command, skip_themes=True, skip_plugins=True,
         install_path='', php_version='7.0'):
    """runs_wp-cli command"""
    api_vars = app.actions.apis.api_vars['wpcli']
    wpcli_path = app.settings.apis['wpcli']['binary']
    php_path = app.settings.apis['php']['versions'][php_version]

    path = ''
    if install_path:
        path = install_path
    else:
        if 'dir' in api_vars['active_install'].keys():
            if api_vars['active_install']['dir']:
                path = api_vars['active_install']['dir']

    popen_args = [php_path, wpcli_path]
    arguments = shlex.split(command)
    for argument in arguments:
        popen_args.append(argument)
    if path:
        popen_args.append('--path='+path)

    if skip_themes:
        popen_args.append('--skip-themes')
    if skip_plugins:
        popen_args.append('--skip-plugins')
    data, error = subprocess.Popen(
        popen_args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    ).communicate()

    app.log.debug("data: %s\nerror: %s\n", data, error)

    return data.decode('UTF-8'), error.decode('UTF-8')

def register_api(api_vars):
    if 'wpcli' not in api_vars.keys():
        api_vars['wpcli'] = {
            'active_install': {},
            'installation_details': [],
            'themes': []
        }
