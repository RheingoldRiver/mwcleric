from requests import HTTPError

from mwcleric.clients.cargo_client import CargoClient
from mwcleric.clients.site import Site
from .auth_credentials import AuthCredentials
from .wiki_client import WikiClient


class WikiggClient(WikiClient):
    """
    Functions for connecting to and editing specifically wiki.gg wikis.
    """
    cargo_client: CargoClient = None
    client: Site = None
    wiki: str = None
    credentials: AuthCredentials

    def __init__(self, wiki: str, client: Site = None,
                 credentials: AuthCredentials = None, lang: str = None,
                 use_site_pw: bool = False,
                 **kwargs):
        """
        Create a site object.

        :param wiki: Name of a wiki
        :param lang: Optional. If the wiki has a language path in the URL, provide it here.
        :param client: Otpional. If this is provided, SessionManager will not be used.
        :param credentials: Optional. Provide if you want a logged-in session.
        """

        path = '/'

        self.is_public = True
        # en-language wikis have no special path on wiki.gg
        if lang == 'en':
            lang = None
        try:
            # first assume the wiki is public
            url = '{}.wiki.gg{}'.format(
                wiki, f"/{lang}" if lang is not None else '')
            super().__init__(url=url, path=path, credentials=credentials, client=client, **kwargs)
        except HTTPError:
            # else try to log into an onboarding wiki if possible
            # on wiki.gg onboarding wikis are locked behind HTTP auth
            if credentials is None:
                raise HTTPError
            if credentials.site_password_prefix == '':
                raise HTTPError
            url = '{}{}.wiki.gg{}'.format(
                credentials.site_password_prefix,
                wiki, f"/{lang}" if lang is not None else '')
            super().__init__(url=url, path=path, credentials=credentials, client=client, **kwargs)
            self.is_public = False

        self.cargo_client = CargoClient(self.client)
        self.credentials = credentials

    def relog(self):
        super().relog()
        self.cargo_client = CargoClient(self.client)
