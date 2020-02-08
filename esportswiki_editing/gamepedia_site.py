from .extended_site import ExtendedSite
from .cargo_site import CargoSite
from .wiki_script_error import WikiScriptError
from .wiki_content_error import WikiContentError


class GamepediaSite(ExtendedSite, CargoSite):
    def __init__(self, user, wiki, stg=False, username=None, pwd=None):
        suffix = 'io' if stg else 'com'
        super().__init__('%s.gamepedia.' % wiki + suffix, path='/')
        if username is None or pwd is None:
            pwd_file = 'password2.txt' if user == 'bot' else 'password.txt'
            user_file = 'username2.txt' if user == 'bot' else 'username.txt'
            pwd = open(pwd_file).read().strip()
            username = open(user_file).read().strip()
        self.login(username, pwd)

        self.errors = []

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
