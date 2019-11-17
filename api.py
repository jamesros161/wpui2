import wpcli as WpCli
import sysproc as SysProc

class Apis():
    def __init__(self, app):
        self.app = app
        self.log = app.log
        self.wpcli = WpCli
        self.sysproc = SysProc
        self.api_vars = {}

        self.register_apis(
            self.api_vars, [
            self.wpcli,
            self.sysproc])

    def register_apis(self, api_vars, apis):
        for api in apis:
            if hasattr(api, 'register_api'):
                reg = getattr(api, 'register_api')
                reg(api_vars)
            else:
                self.log.warning(
                    'Failed to Register %s API: Missing register_api method')

    def run_api(self, meta):
        if isinstance(meta, dict):
            user_data = meta
        else:
            user_data = meta.user_data
        api_type = None
        api_class = None
        api_method = None
        self.log.debug('user_data: %s', user_data)
        if hasattr(self, user_data['api']):
            api_type = getattr(self, user_data['api'])
        if hasattr(api_type, user_data['class']):
            api_class = getattr(api_type, user_data['class'])
        if hasattr(api_class, user_data['method']):
            api_method = getattr(api_class, user_data['method'])
        self.log.debug(
            "api: %s\nclass: %s\n fun: %s",
            api_type, api_class, api_method
            )
        api_response = api_method(self, self.app, meta)

        if "after_action_view" in user_data.keys():
            if "skip_results_popup" in user_data.keys():
                self.app.views.activate(
                    self, {'view': user_data['after_action_view']})
            else:
                self.app.views.activate(
                    self, {
                        'view': 'api_response_view',
                        'api_response': api_response,
                        'return_view': user_data['after_action_view']
                        })

