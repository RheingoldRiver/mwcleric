from mwclient import InvalidResponse
from requests import HTTPError

from .auth_credentials import AuthCredentials
from .cargo_client import CargoClient
from .session_manager import session_manager
from .site import Site
from .wiki_client import WikiClient


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
        try:
            super().__init__(url=url, path='/', credentials=credentials, client=client, **kwargs)
        except InvalidResponse:
            url = url.replace('gamepedia', 'fandom')
            super().__init__(url=url, path='/', credentials=credentials, client=client, **kwargs)

        # this backup_client would only be used for people who did not get their client fixed
        # by the login above, so we do not need to supply credentials at this point in time
        try:
            backup_client = session_manager.get_client(url=self.url.replace('gamepedia', 'fandom'), path='/',
                                                       **kwargs)
        except HTTPError:
            backup_client = self.client
        self.cargo_client = CargoClient(self.client, backup_client=backup_client)

    def relog(self):
        super().relog()
        self.cargo_client = CargoClient(self.client)

    def login(self):
        if self.credentials is None:
            return
        try:
            self.client.login(username=self.credentials.username, password=self.credentials.password)
        except InvalidResponse:
            self.url = self.url.replace('gamepedia', 'fandom')
            self.relog()
