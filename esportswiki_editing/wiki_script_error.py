from .wiki_error import WikiError


class WikiScriptError(WikiError):
    """Exceptions raised by scripts
    """
    def __init__(self, title: str, e: Exception):
        super().__init__()
        self.title = title
        self.error = e
        self.error_type = type(self.error)
