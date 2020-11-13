import datetime
import time
from mwclient.page import Page
from mwclient.errors import AssertUserFailedError
from mwclient.errors import APIError
from requests.exceptions import ReadTimeout

from .auth_credentials import AuthCredentials
from .session_manager import session_manager
from .site import Site
from .wiki_content_error import WikiContentError
from .wiki_script_error import WikiScriptError
from .namespace import Namespace
from .errors import PatrolRevisionNotSpecified
from .errors import RetriedLoginAndStillFailed


class WikiClient(object):
    """
    Various utilities that extend mwclient and could be useful on any wiki/wiki farm
    Utilities here should not depend on any extensions
    There's no intention to develop anything that's not useful on Gamepedia/Gamepedia esports wikis
    but anything that's platform or extension-specific will go in GamepediaSite instead
    """
    url = None
    client = None
    write_errors = (AssertUserFailedError, ReadTimeout)

    def __init__(self, url: str, path='/', credentials: AuthCredentials = None, client: Site = None,
                 max_retries=3, retry_interval=10, **kwargs):
        self.url = url
        self.errors = []
        self._namespaces = None
        self.credentials = credentials
        self.path = path
        self.kwargs = kwargs
        self.max_retries = max_retries
        self.retry_interval = retry_interval
        if client:
            self.client = client
            return

        self.client = session_manager.get_client(url=url, path=path, credentials=credentials, **kwargs)

    def login(self):
        if self.credentials is None:
            return
        self.client.login(username=self.credentials.username, password=self.credentials.password)

    def relog(self):
        """
        Completely discards pre-existing session and creates a new site object
        :return:
        """
        # The session manager will log in for us too
        self.client = session_manager.get_client(url=self.url, path=self.path,
                                                 credentials=self.credentials, **self.kwargs,
                                                 force_new=True)

    @property
    def namespaces(self):
        if self._namespaces is not None:
            return self._namespaces
        result = self.client.api('query', meta='siteinfo', siprop="namespaces|namespacealiases")
        ns_aliases = {}
        for alias in result['query']['namespacealiases']:
            alias_key = str(alias['id'])
            if alias_key not in ns_aliases:
                ns_aliases[alias_key] = []
            ns_aliases[alias_key].append(alias['*'])
        ret = []
        for ns_str, ns_data in result['query']['namespaces'].items():
            ns = int(ns_str)
            ret.append(Namespace(id_number=ns, name=ns_data['*'],
                                 canonical_name=ns_data.get('canonical'), aliases=ns_aliases.get(ns_str)))
        self._namespaces = ret
        return ret

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

    def target(self, name: str):
        """
        Return the name of a page's redirect target
        :param name: Name of page
        :return: Name of page's redirect target
        """
        return self.client.pages[name].resolve_redirect().name

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

    def log_error_script(self, title: str = None, error: Exception = None):
        self.errors.append(WikiScriptError(title, error))

    def log_error_content(self, title: str = None, text: str = None):
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

    def patrol(self, revid=None, rcid=None, **kwargs):
        if revid is None and rcid is None:
            raise PatrolRevisionNotSpecified
        patrol_token = self.client.get_token('patrol')
        try:
            self.client.api('patrol', revid=revid, rcid=rcid, **kwargs, token=patrol_token)
        except APIError:
            self.relog()
            try:
                self.client.api('patrol', revid=revid, rcid=rcid, **kwargs, token=patrol_token)
            except APIError:
                raise RetriedLoginAndStillFailed('patrol')

    def save(self, page: Page, text, summary=u'', minor=False, bot=True, section=None, **kwargs):
        """
        Performs a page edit, retrying the login once if the edit fails due to the user being logged out
        
        This function hopefully makes it easy to workaround the lag and frequent login timeouts
        experienced on the Fandom UCP platform compared to Gamepedia Hydra.
        
        :param page: mwclient Page object
        :param text: as in mwclient.Page.edit
        :param summary: as in mwclient.Page.edit
        :param minor: as in mwclient.Page.edit
        :param bot: as in mwclient.Page.edit
        :param section: as in mwclient.Page.edit
        :param kwargs: as in mwclient.Page.edit
        :return: nothing
        """
        try:
            page.edit(text, summary=summary, minor=minor, bot=bot, section=section, **kwargs)
        except self.write_errors:
            self._retry_login_action(self._retry_save, 'edit', page=page, text=text, summary=summary, minor=minor,
                                     bot=bot, section=section, **kwargs)

    def _retry_save(self, **kwargs):
        old_page: Page = kwargs.pop('page')
        # recreate the page object so that we're using the new site object, post-relog
        page = self.client.pages[old_page.name]
        text = kwargs.pop('text')
        page.edit(text, **kwargs)

    def _retry_login_action(self, f, failure_type, **kwargs):
        was_successful = False
        for retry in range(self.max_retries):
            self.relog()
            # don't sleep at all the first retry, and then increment in retry_interval intervals
            # default interval is 10, default retries is 3
            time.sleep((2 ** retry - 1) * self.retry_interval)
            try:
                f(**kwargs)
                was_successful = True
                break
            except self.write_errors:
                continue
        if not was_successful:
            raise RetriedLoginAndStillFailed(failure_type)

    def save_tile(self, title: str, text, summary=None, minor=False, bot=True, section=None, **kwargs):
        self.save(self.client.pages[title], text,
                  summary=summary, minor=minor, bot=bot, section=section, **kwargs)
