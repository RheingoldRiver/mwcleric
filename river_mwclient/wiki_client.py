from .site import Site
import datetime
from .wiki_script_error import WikiScriptError
from .wiki_content_error import WikiContentError
from .auth_credentials import AuthCredentials
from .session_manager import session_manager


class WikiClient(object):
    """
    Various utilities that extend mwclient and could be useful on any wiki/wiki farm
    Utilities here should not depend on any extensions
    There's no intention to develop anything that's not useful on Gamepedia/Gamepedia esports wikis
    but anything that's platform or extension-specific will go in GamepediaSite instead
    """
    errors = []
    url = None
    client = None

    def __init__(self, url: str, path='/', credentials: AuthCredentials = None, client: Site = None,  **kwargs):
        self.url = url
        if client:
            self.client = client
            return

        self.client = session_manager.get_client(url=url, path=path, credentials=credentials, **kwargs)

    def pages_using(self, template, **kwargs):
        if ':' not in template:
            title = 'Template:' + template
        elif template.startswith(':'):
            title = template[1:]
        else:
            title = template
        return self.client.pages[title].embeddedin(**kwargs)

    def recentchanges_by_interval(self, minutes, offset=0,
                                  prop='title|ids|tags|user|patrolled', **kwargs):
        now = datetime.datetime.utcnow() - datetime.timedelta(minutes=offset)
        then = now - datetime.timedelta(minutes=minutes)
        result = self.client.recentchanges(
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
            yield self.client.pages[title]

    def logs_by_interval(self, minutes, offset=0,
                         lelimit="max",
                         leprop='details|type|title|tags', **kwargs):
        now = datetime.datetime.utcnow() - datetime.timedelta(minutes=offset)
        then = now - datetime.timedelta(minutes=minutes)
        logs = self.client.api('query', format='json',
                               list='logevents',
                               #  lestart=now.isoformat(),
                               leend=then.isoformat(),
                               leprop=leprop,
                               lelimit=lelimit,
                               ledir='older',
                               **kwargs
                               )
        return logs['query']['logevents']

    def error_script(self, title: str = None, error: Exception = None):
        self.errors.append(WikiScriptError(title, error))

    def error_content(self, title: str = None, text: str = None):
        self.errors.append(WikiContentError(title, error=text))

    def report_all_errors(self, error_title):
        if not self.errors:
            return
        error_page = self.client.pages['Log:' + error_title]
        errors = [_.format_for_print() for _ in self.errors]
        error_text = '<br>\n'.join(errors)
        error_page.append('\n' + error_text)

        # reset the list so we can reuse later if needed
        self.errors = []
