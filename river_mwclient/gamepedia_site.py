from .extended_site import ExtendedSite
from .cargo_site import CargoSite
from .wiki_script_error import WikiScriptError
from .wiki_content_error import WikiContentError


class GamepediaSite(ExtendedSite, CargoSite):
    def __init__(self, wiki, stg=False):
        suffix = 'io' if stg else 'com'
        super().__init__('%s.gamepedia.' % wiki + suffix, path='/')
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
