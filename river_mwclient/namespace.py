class Namespace(object):
    def __init__(self, id_number: int = None, name: str = None, canonical_name: str = None, aliases: list = None):
        self.id = id_number
        self.name = name
        self.canonical_name = canonical_name
        self.aliases = aliases or []
