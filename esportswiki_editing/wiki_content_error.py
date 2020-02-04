from .wiki_error import WikiError


class WikiContentError(WikiError):
    """Exceptions that we note based on the content of the wiki
    """
    def __init__(self, title: str, e: str):
        super().__init__()
        self.title = title
        self.error = e
        self.error_type = 'Wiki Content Error'
