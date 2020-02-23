import mwclient, datetime


class ExtendedSite(mwclient.Site):
    """
    Various utilities that extend mwclient and could be useful on any wiki/wiki farm
    Utilities here should not depend on any extensions
    There's no intention to develop anything that's not useful on Gamepedia/Gamepedia esports wikis
    but anything that's platform or extension-specific will go in GamepediaSite instead
    """
    def recentchanges_by_interval(self, minutes, offset=0,
                                  prop='title|ids|tags|user|patrolled'
                                  , **kwargs):
        now = datetime.datetime.utcnow() - datetime.timedelta(minutes=offset)
        then = now - datetime.timedelta(minutes=minutes)
        result = self.recentchanges(
            start=now.isoformat(),
            end=then.isoformat(),
            limit='max',
            prop=prop,
            **kwargs
        )
        return result

    def recent_titles_by_interval(self, *args, **kwargs):
        revisions = self.recentchanges_by_interval(*args, **kwargs, toponly=0)
        titles = [_['title'] for _ in revisions]
        return titles

    def recent_pages_by_interval(self, *args, **kwargs):
        revisions = self.recent_titles_by_interval(*args, **kwargs)
        titles = [_['title'] for _ in revisions]
        for title in titles:
            yield self.pages[title]

    def logs_by_interval(self, minutes, offset=0,
                         lelimit="max",
                         leprop='details|type|title|tags', **kwargs):
        now = datetime.datetime.utcnow() - datetime.timedelta(minutes=offset)
        then = now - datetime.timedelta(minutes=minutes)
        logs = self.api('query', format='json',
                        list='logevents',
                        # lestart=now.isoformat(),
                        leend=then.isoformat(),
                        leprop=leprop,
                        lelimit=lelimit,
                        ledir='older',
                        **kwargs
                        )
        return logs['query']['logevents']
