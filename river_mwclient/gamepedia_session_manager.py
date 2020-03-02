from .wiki_client import WikiClient
from .cargo_client import CargoClient
from .auth_credentials import AuthCredentials


class GamepediaSessionManager(object):
    """Manages instances of Gamepedia client
    We assume all Gamepedia wikis have Cargo (if one doesn't, this code won't break)
    """
    existing_wikis = {}

    def get_client(self, url: str = None, credentials: AuthCredentials = None, **kwargs):
        if url in self.existing_wikis:
            return self.existing_wikis[url]['client'], self.existing_wikis[url]['cargo_client']
        client = WikiClient(url, path='/', credentials=credentials, **kwargs)
        cargo_client = CargoClient(client)
        self.existing_wikis[url] = {'client': client, 'cargo_client': cargo_client}
        return client, cargo_client


session_manager = GamepediaSessionManager()
