from mwclient import Site
from .cargo_client import CargoClient
from .wiki_client import WikiClient
from .auth_credentials import AuthCredentials


class GamepediaClient(WikiClient):
    """
    Functions for connecting to and editing specifically Gamepedia wikis.
    """
    cargo_client: CargoClient = None
    client: Site = None
    wiki: str = None

    def __init__(self, wiki: str, client: Site = None,
                 credentials: AuthCredentials = None, stg: bool = False,
                 **kwargs):
        """
        Create a site object.
        :param wiki: Name of a wiki
        :param client: WikiClient object. If this is provided, SessionManager will not be used.
        :param credentials: Optional. Provide if you want a logged-in session.
        :param stg: if it's a staging wiki or not
        """

        suffix = 'io' if stg else 'com'
        url = '{}.gamepedia.{}'.format(wiki, suffix)

        super().__init__(url=url, path='/', credentials=credentials, client=client, **kwargs)
        self.cargo_client = CargoClient(self.client)
