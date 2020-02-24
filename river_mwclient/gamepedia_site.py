from .extended_site import ExtendedSite
from .cargo_site import CargoSite


class GamepediaSite(ExtendedSite):
    """
    Functions for connecting to and editing Gamepedia wikis. As with ExtendedSite, the focus of support
    is Gamepedia esports wikis specifically, but no functions here require using an esports wiki to work.

    Cargo-specific functions should be in CargoSite
    """
    cargo_client = None

    def __init__(self, wiki: str, stg=False, username: str = None, password: str = None):
        suffix = 'io' if stg else 'com'
        wiki = '%s.gamepedia.' % wiki + suffix
        super().__init__(wiki, path='/', username=username, password=password)

        self.cargo_client = CargoSite(client=self)
