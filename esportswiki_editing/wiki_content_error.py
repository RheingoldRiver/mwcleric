from .wiki_error import WikiError


class WikiContentError(WikiError):
    """Exceptions that we note based on the content of the wiki
    """
    def __init__(self, title: str = None, error: str = None):
        super().__init__()
        self.title = title
        self.error = error if error else 'No details provided'
        self.error_type = 'Wiki Content Error'
