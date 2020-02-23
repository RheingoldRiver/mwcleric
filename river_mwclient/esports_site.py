from .gamepedia_site import GamepediaSite

ALL_ESPORTS_WIKIS = ['lol', 'halo', 'smite', 'vg', 'rl', 'pubg', 'fortnite',
                     'apexlegends', 'fifa', 'gears', 'nba2k', 'paladins', 'siege',
                     'default-loadout', 'commons', 'teamfighttactics']


class EsportsSite(GamepediaSite):

    def __init__(self, wiki: str, username: str = None, password: str = None):
        """
        Create a site object. Username is optional
        :param wiki: Name of a wiki
        """
        super().__init__(self.get_wiki(wiki))
        self.wiki = wiki
        self.username = username  # set this in login if not provided here
        self.password = password  # set this in login if not provided here

    def login(self, username=None, password=None, **kwargs):
        self.username = username
        self.password = password
        super().login(username=username, password=password, **kwargs)

    def login_from_file(self, user, **kwargs):
        """
        Log in using the configuration expected by the original log_into_wiki that I wrote
        :param user: Either "me" (reads from username.txt & password.txt) or "bot" (username2/password2)
        :param kwargs: Sent directly to super().login
        :return: none
        """
        pwd_file = 'password2.txt' if user == 'bot' else 'password.txt'
        user_file = 'username2.txt' if user == 'bot' else 'username.txt'
        password = open(pwd_file).read().strip()
        username = open(user_file).read().strip()
        self.login(username=username, password=password, **kwargs)

    @staticmethod
    def get_wiki(wiki):
        if wiki in ['lol', 'teamfighttactics'] or wiki not in ALL_ESPORTS_WIKIS:
            return wiki
        return wiki + '-esports'

    def standard_name_redirects(self):
        for item in self.cargoquery(
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
