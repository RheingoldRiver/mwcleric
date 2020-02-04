from .extended_site import ExtendedSite
from .cargo_site import CargoSite
from .wiki_script_error import WikiScriptError
from .wiki_content_error import WikiContentError


class GamepediaSite(ExtendedSite, CargoSite):
    def __init__(self, user, wiki, stg=False):
        suffix = 'io' if stg else 'com'
        super().__init__('%s.gamepedia.' % wiki + suffix, path='/')
        pwd_file = 'password2.txt' if user == 'bot' else 'password.txt'
        user_file = 'username2.txt' if user == 'bot' else 'username.txt'
        pwd = open(pwd_file).read().strip()
        username = open(user_file).read().strip()
        self.login(username, pwd)

        self.errors = []

    def script_error(self, title: str, e: Exception):
        self.errors.append(WikiScriptError(title, e))

    def content_error(self, title: str, error: str = None):
        self.errors.append(WikiContentError(title, error=error))

    def report_all_errors(self, error_title):
        error_page = self.pages['Log:' + error_title]
        errors = [_.format_for_print() for _ in self.errors]
        error_text = '<br>\n'.join(errors)
        error_page.append('\n' + error_text)
