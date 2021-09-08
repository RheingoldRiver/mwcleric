class SimplePage:
    """A data container holding the name of a page and its text. Not capable of any operations."""

    def __init__(self, name: str, text: str, exists: bool):
        self.name = name
        self.text = text
        self.exists = exists
