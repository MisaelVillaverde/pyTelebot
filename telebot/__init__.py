import re
import requests
import time
import mimetypes

class TeleBot(object):

    def __init__(self, import_name):
        self.import_name = import_name
        self.update_rules = []
        self.config = {
            api_key=None,
            requests_kwargs={
                timeout=60,
            },
        }
        self.offset = 0
        self.whoami = None

    def add_update_rule(self, rule, endpoint=None, view_func=None, **options):
        self.update_rules.append({
            rule=re.compile(rule),
            endpoint=endpoint,
            view_func=view_func,
            options=dict(**options),
        })

    def route(self, rule, **options):
        """A decorator that is used to register a view function for a
        given URL rule.  This does the same thing as :meth:`add_url_rule`
        but is intended for decorator usage::
            @app.route('/')
            def index():
                return 'Hello World'
        For more information refer to :ref:`url-route-registrations`.
        :param rule: the URL rule as string
        :param endpoint: the endpoint for the registered URL rule.  Flask
                         itself assumes the name of the view function as
                         endpoint
        :param options: the options to be forwarded to the underlying
                        :class:`~werkzeug.routing.Rule` object.  A change
                        to Werkzeug is handling of method options.  methods
                        is a list of methods this rule should be limited
                        to (``GET``, ``POST`` etc.).  By default a rule
                        just listens for ``GET`` (and implicitly ``HEAD``).
                        Starting with Flask 0.6, ``OPTIONS`` is implicitly
                        added and handled by the standard request handling.
        """
        def decorator(f):
            endpoint = options.pop('endpoint', None)
            self.add_update_rule(rule, endpoint, f, **options)
            return f
        return decorator

    def _start(self):
        '''Requests bot information based on current api_key, and sets
        self.whoami to dictionary with username, first_name, and id of the
        configured bot.

        '''
        if self.whoami is None:
            me = self.get_me()
            if me.get('ok', False):
                self.whoami = me['result']
            else:
                raise ValueError("Bot Cannot request information, check "
                                 "api_key")

    def _bot_cmd(self, method, endpoint, *args, **kwargs):
        api = f"https://api.telegram.org/bot{self.config['api_key']}/{endpoint}"

        try:
            response = method(api,
                              data=kwargs.get('data', None),
                              files=kwargs.get('files', None),
                              params=kwargs.get('params', {}),
                              **self.config['requests_kwargs'])

            if response.status_code != 200:
                raise ValueError(f"Got unexpected response. ({response.status_code}) - {response.text}")

            return response.json()
        except Exception as e:
            return {
                'ok': False,
                'error': str(e),
            }

    def get_me(self):
        '''A simple method for testing your bot's auth token. Requires no
        parameters. Returns basic information about the bot in form of a `User
        object.

        '''
        return self._bot_cmd(requests.get, 'getMe')

    def send_message(self, chat_id, text):
        data = {
            "chat_id": chat_id,
            "text": text,
        }

        return self._bot_cmd(requests.post, 'sendMessage', data=data)

    def forward_message(self):
        raise NotImplemented("forward_message needs work")

    def send_photo(self):
        raise NotImplemented("send_photo needs work")

    def send_audio(self):
        raise NotImplemented("send_audio needs work")

    def send_document(self, chat_id, caption, filename, fileurl):
        filetype = mimetypes.guess_type(fileurl)

        if (filetype is None):
            raise ValueError("The file you want to sent is not valid")
        data = {
            chat_id: chat_id,
            caption: caption
        }
        files = [('document', (filename, open(fileurl, 'rb'), filetype)]

        return self._bot_cmd(requests.post, 'sendDocument', data=data, files=files)

    def send_sticker(self):
        raise NotImplemented("send_sticker needs work")

    def send_video(self):
        raise NotImplemented("send_video needs work")

    def send_location(self):
        raise NotImplemented("send_location needs work")

    def send_chat_action(self):
        raise NotImplemented("send_chat_action needs work")

    def get_user_profile_photos(self):
        raise NotImplemented("get_user_profile_photos needs work")

    def get_updates(self, offset=None):
        data = {
            "offset": offset or self.offset,
        }
        updates = self._bot_cmd(requests.get, 'getUpdates', data=data)

        if updates['ok']:
            for update in updates['result']:
                self.offset = max(self.offset, update['update_id'])
        return updates

    def set_webhook(self):
        raise NotImplemented("set_webhook needs work")
