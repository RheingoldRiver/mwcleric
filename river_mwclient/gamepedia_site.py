from .extended_site import ExtendedSite
from .cargo_site import CargoSite


class GamepediaSite(ExtendedSite):
    """
    Functions for connecting to and editing Gamepedia wikis. As with ExtendedSite, the focus of support
    is Gamepedia esports wikis specifically, but no functions here require using an esports wiki to work.

    Cargo-specific functions should be in CargoSite
    """
    cargo_client = None

    def __init__(self, wiki: str, stg=False, cargo_site=None, username=None, password=None):
        suffix = 'io' if stg else 'com'
        wiki = '%s.gamepedia.' % wiki + suffix
        super().__init__(wiki, path='/')
        if not cargo_site:
            # this is where I'm making a clone of the site?
            # also what if I do site = GamepediaSite and then site.login_from_file()
            # how am i logging into the cargo client too
            self.cargo_client = CargoSite(wiki, username=username, password=password)
