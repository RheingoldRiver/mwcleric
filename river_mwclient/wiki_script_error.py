from .wiki_error import WikiError


class WikiScriptError(WikiError):
    """Exceptions raised by scripts
    """
    
    def __init__(self, title: str = None, error: Exception = None):
        super().__init__()
        self.title = title
        self.error = error
        self.error_type = type(self.error)
