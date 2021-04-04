from mwclient import InvalidResponse

from .auth_credentials import AuthCredentials
from .cargo_client import CargoClient
from .site import Site
from .wiki_client import WikiClient


class FandomClient(WikiClient):
    """
    Functions for connecting to and editing specifically Fandom wikis.
    """
    cargo_client: CargoClient = None
    client: Site = None
    wiki: str = None

    def __init__(self, wiki: str, client: Site = None,
                 credentials: AuthCredentials = None, lang: str = None,
                 **kwargs):
        """
        Create a site object.
        :param wiki: Name of a wiki
        :param client: WikiClient object. If this is provided, SessionManager will not be used.
        :param credentials: Optional. Provide if you want a logged-in session.
        :param stg: if it's a staging wiki or not
        """

        url = '{}.fandom.com'.format(wiki)
        self.lang = '/' + ('' if lang is None else lang + '/')
        super().__init__(url=url, path=self.lang, credentials=credentials, client=client, **kwargs)

        self.cargo_client = CargoClient(self.client)

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
