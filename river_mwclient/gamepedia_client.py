from .cargo_client import CargoClient
from .wiki_client import WikiClient
from .gamepedia_session_manager import session_manager
from .auth_credentials import AuthCredentials


class EsportsClient(object):
    """
    Functions for connecting to and editing specifically Gamepedia wikis.
    """
    cargo_client: CargoClient = None
    client: WikiClient = None
    wiki: str = None

    def __init__(self, wiki: str, client: WikiClient = None,
                 credentials: AuthCredentials = None, stg: bool = False,
                 **kwargs):
        """
        Create a site object. Credentials are optional.
        :param wiki: Name of a wiki
        :param client: WikiClient object. If this is provided, SessionManager will not be used.
        :param credentials: Optional. Provide if you want a logged-in session.
        :param stg: if it's a staging wiki or not
        """
        self.wiki = wiki
        if client:
            # completely skip the session manager
            self.cargo_client = CargoClient(client)
            self.client = client
            return

        suffix = 'io' if stg else 'com'
        url = '{}.gamepedia.{}'.format(wiki, suffix)

        self.client, self.cargo_client = session_manager.get_client(url=url,
                                                                    credentials=credentials,
                                                                    **kwargs
                                                                    )
