from .wiki_error import WikiError
from mwclient.page import Page


class WikiContentError(WikiError):
    """Exceptions that we note based on the content of the wiki
    """
    def __init__(self, page: Page, e: str):
        super().__init__()
        self.title = page.name
        self.error = e
        self.error_type = 'Wiki Content Error'
