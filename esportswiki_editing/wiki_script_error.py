from .wiki_error import WikiError
from mwclient.page import Page


class WikiScriptError(WikiError):
    """Exceptions raised by scripts
    """
    def __init__(self, page: Page, e: Exception):
        super().__init__()
        self.title = page.name
        self.error = e
        self.error_type = type(self.error)
