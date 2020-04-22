from .auth_credentials import AuthCredentials
from .cargo_client import CargoClient
from .esports_lookup_cache import EsportsLookupCache
from .site import Site
from .wiki_client import WikiClient

ALL_ESPORTS_WIKIS = ['lol', 'halo', 'smite', 'vg', 'rl', 'pubg', 'fortnite',
                     'apexlegends', 'fifa', 'gears', 'nba2k', 'paladins', 'siege',
                     'splatoon2', 'legendsofruneterra',
                     'default-loadout', 'commons', 'teamfighttactics', 'valorant']


class EsportsClient(WikiClient):
    """
    Functions for connecting to and editing specifically to Gamepedia esports wikis.

    If not using an esports wiki, please use GamepediaSite instead.
    """
    ALL_ESPORTS_WIKIS = ALL_ESPORTS_WIKIS
    cargo_client: CargoClient = None
    client: Site = None
    wiki: str = None
    
    def __init__(self, wiki: str, client: Site = None,
                 credentials: AuthCredentials = None, stg: bool = False,
                 cache: EsportsLookupCache = None,
                 **kwargs):
        """
        Create a site object.
        :param wiki: Name of a wiki
        :param client: WikiClient object. If this is provided, SessionManager will not be used.
        :param credentials: Optional. Provide if you want a logged-in session.
        :param stg: if it's a staging wiki or not
        """
        self.wiki = self.get_wiki(wiki)
        
        suffix = 'io' if stg else 'com'
        url = '{}.gamepedia.{}'.format(self.wiki, suffix)
        
        super().__init__(url=url, path='/', credentials=credentials, client=client, **kwargs)
        if cache:
            self.cache = cache
        else:
            self.cache = EsportsLookupCache(self.client)
        self.cargo_client = CargoClient(self.client)
    
    @staticmethod
    def get_wiki(wiki):
        if wiki in ['lol', 'teamfighttactics'] or wiki not in ALL_ESPORTS_WIKIS:
            return wiki
        return wiki + '-esports'
    
    def create_tables(self, tables):
        self.recreate_tables(tables, replacement=False)
    
    def recreate_tables(self, tables, replacement=True):
        if isinstance(tables, str):
            tables = [tables]
        templates = ['{}/CargoDec'.format(_) for _ in tables]
        self.cargo_client.recreate(templates, replacement=replacement)
    
    def other_wikis(self):
        """
        :return: Generator of wiki names as strings, not site objects
        """
        for wiki in ALL_ESPORTS_WIKIS:
            if wiki == self.wiki:
                continue
            yield wiki
    
    def other_sites(self):
        for wiki in self.other_wikis():
            yield EsportsClient(wiki)
    
    @staticmethod
    def all_wikis():
        for wiki in ALL_ESPORTS_WIKIS:
            yield wiki
    
    @staticmethod
    def all_sites():
        """
        Use self.all_sites_logged_in() if you want to log in; this is deliberately static
        :return: Generator of all esports wikis as site objects
        """
        for wiki in ALL_ESPORTS_WIKIS:
            yield EsportsClient(wiki)
    
    def all_sites_logged_in(self):
        for wiki in ALL_ESPORTS_WIKIS:
            yield EsportsClient(wiki, username=self.client.username, password=self.client.password)
