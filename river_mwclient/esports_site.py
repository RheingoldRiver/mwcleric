from .gamepedia_site import GamepediaSite


class EsportsSite(GamepediaSite):

    ALL_ESPORTS_WIKIS = ['lol', 'halo', 'smite', 'vg', 'rl', 'pubg', 'fortnite',
                         'apexlegends', 'fifa', 'gears', 'nba2k', 'paladins', 'siege',
                         'default-loadout', 'commons', 'teamfighttactics']

    def __init__(self, user, wiki, **kwargs):
        super().__init__(user, self.get_wiki(wiki), **kwargs)
        self.user = user
        self.wiki = wiki

    def get_wiki(self, wiki):
        if wiki in ['lol', 'teamfighttactics'] or wiki not in self.ALL_ESPORTS_WIKIS:
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
        for wiki in self.ALL_ESPORTS_WIKIS:
            if wiki == self.wiki:
                continue
            yield wiki

    def other_sites(self):
        for wiki in self.other_wikis():
            yield EsportsSite('me', wiki)

    def all_wikis(self):
        for wiki in self.ALL_ESPORTS_WIKIS:
            yield wiki

    def all_sites(self, user):
        for wiki in self.ALL_ESPORTS_WIKIS:
            yield EsportsSite(user, wiki)
