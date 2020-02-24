from .gamepedia_site import GamepediaSite
from .cargo_site import CargoSite

ALL_ESPORTS_WIKIS = ['lol', 'halo', 'smite', 'vg', 'rl', 'pubg', 'fortnite',
                     'apexlegends', 'fifa', 'gears', 'nba2k', 'paladins', 'siege',
                     'default-loadout', 'commons', 'teamfighttactics']


class EsportsSite(object):
    """
    Functions for connecting to and editing specifically to Gamepedia esports wikis.

    No functions in this class should be useful to non-esports wikis; if they are, they should
    go in GamepediaSite instead.

    Reasons for inclusion here include enumerating sites using ALL_ESPORTS_WIKIS, or
    specifically querying esports Cargo tables that won't exist elsewhere
    """
    ALL_ESPORTS_WIKIS = ALL_ESPORTS_WIKIS
    cargo_client = None
    client = None
    gp_client = None

    def __init__(self, wiki: str=None, gp_client: GamepediaSite = None, **kwargs):
        """
        Create a site object. Username is optional
        :param wiki: Name of a wiki
        """
        if gp_client:
            self.gp_client = gp_client
        else:
            self.gp_client = GamepediaSite(self.get_wiki(wiki), **kwargs)

        self.cargo_client = self.gp_client.cargo_client
        self.client = self.gp_client.client

    @staticmethod
    def get_wiki(wiki):
        if wiki in ['lol', 'teamfighttactics'] or wiki not in ALL_ESPORTS_WIKIS:
            return wiki
        return wiki + '-esports'

    def standard_name_redirects(self):
        """
        TODO: move this to a separate library, this is too specific for inclusion here
        :return:
        """
        for item in self.cargo_client.query(
                tables="Tournaments,_pageData",
                join_on="Tournaments.StandardName_Redirect=_pageData._pageName",
                where="_pageData._pageName IS NULL AND Tournaments.StandardName_Redirect IS NOT NULL",
                fields="Tournaments.StandardName_Redirect=Name,Tournaments._pageName=Target",
                limit="max"
        ):
            page = self.pages[item['Name']]
            target = item['Target']
            page.save('#redirect[[%s]]' % target, summary="creating needed CM_StandardName redirects")

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
            yield EsportsSite(wiki)

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
            yield EsportsSite(wiki)

    def all_sites_logged_in(self):
        for wiki in ALL_ESPORTS_WIKIS:
            yield EsportsSite(wiki, username=self.username, password=self.password)
