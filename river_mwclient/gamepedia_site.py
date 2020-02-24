from .extended_site import ExtendedSite
from .cargo_site import CargoSite
from .wiki_script_error import WikiScriptError
from .wiki_content_error import WikiContentError


class GamepediaSite(ExtendedSite, CargoSite):
    """
    Functions for connecting to and editing Gamepedia wikis. As with ExtendedSite, the focus of support
    is Gamepedia esports wikis specifically, but no functions here require using an esports wiki to work.

    Cargo-specific functions should be in CargoSite
    """
    def __init__(self, wiki: str, stg=False, username: str = None, password: str = None):
        suffix = 'io' if stg else 'com'
        super().__init__('%s.gamepedia.' % wiki + suffix, path='/')
        self.errors = []

        self.wiki = wiki
        self.username = username  # set this in login if not provided here
        self.password = password  # set this in login if not provided here

    def login(self, username=None, password=None, **kwargs):
        self.username = username
        self.password = password
        super().login(username=username, password=password, **kwargs)

    def login_from_file(self, user, **kwargs):
        """
        Log in using the configuration expected by the original log_into_wiki that I wrote
        :param user: Either "me" (reads from username.txt & password.txt) or "bot" (username2/password2)
        :param kwargs: Sent directly to super().login
        :return: none
        """
        pwd_file = 'password2.txt' if user == 'bot' else 'password.txt'
        user_file = 'username2.txt' if user == 'bot' else 'username.txt'
        password = open(pwd_file).read().strip()
        username = open(user_file).read().strip()
        self.login(username=username, password=password, **kwargs)

    def error_script(self, title: str = None, error: Exception = None):
        self.errors.append(WikiScriptError(title, error))

    def error_content(self, title: str = None, text: str = None):
        self.errors.append(WikiContentError(title, error=text))

    def report_all_errors(self, error_title):
        if not self.errors:
            return
        error_page = self.pages['Log:' + error_title]
        errors = [_.format_for_print() for _ in self.errors]
        error_text = '<br>\n'.join(errors)
        error_page.append('\n' + error_text)

        # reset the list so we can reuse later if needed
        self.errors = []
