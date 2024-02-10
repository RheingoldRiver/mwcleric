from mwcleric.clients.cargo_client import CargoClient
from mwcleric.clients.site import Site
from .auth_credentials import AuthCredentials
from .wiki_client import WikiClient


class WikiGGClient(WikiClient):
    """
    Functions for connecting to and editing specifically wiki.gg wikis.
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
        :param lang: Optional. If the wiki has a language path in the URL, provide it here.
        :param client: Otpional. If this is provided, SessionManager will not be used.
        :param credentials: Optional. Provide if you want a logged-in session.
        """

        url = '{}.wiki.gg{}'.format(wiki, f"/{lang}" if lang is not None else '')
        path = '/'
        super().__init__(url=url, path=path, credentials=credentials, client=client, **kwargs)

        self.cargo_client = CargoClient(self.client)

    def relog(self):
        super().relog()
        self.cargo_client = CargoClient(self.client)
