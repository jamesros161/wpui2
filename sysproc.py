import os

class Installations():

    def get_installations(self, app, meta):
        app.log.debug(dir(meta))

        app.log.debug('get_installations started')

        installations = []
        app.log.debug("Homedir: %s", app.home_dir)
        for root, _, files in os.walk(app.home_dir, topdown=True):
            if 'wp-config.php' in files:
                if '/.' not in root:
                    _x = {
                        'directory': root,
                        'home_url': '',
                        'valid_wp_options': False,
                        'wp_db_check_success': False,
                        'wp_db_error': ''
                    }
                    installations.append(_x)

        app.actions.apis.api_vars['sysproc']['installations'] = installations
        app.log.debug("Installations: %s", installations)
        app.actions.apis.wpcli.Installations.get_installation_details(
            Installations, app, meta, installations)

def register_api(api_vars):
    if 'sysproc' not in api_vars.keys():
        api_vars['sysproc'] = {
            'installations': {}
        }
