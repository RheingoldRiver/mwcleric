import datetime
import time
from typing import Optional, Union, List

from mwclient.page import Page
from mwclient.errors import AssertUserFailedError
from mwclient.errors import APIError
from requests.exceptions import ReadTimeout

from .auth_credentials import AuthCredentials
from .session_manager import session_manager
from .simple_page import SimplePage
from .site import Site
from .wiki_content_error import WikiContentError
from .wiki_script_error import WikiScriptError
from .namespace import Namespace
from .errors import PatrolRevisionNotSpecified
from .errors import RetriedLoginAndStillFailed
from .errors import PatrolRevisionInvalid


class WikiClient(object):
    """
    Various utilities that extend mwclient and could be useful on any wiki/wiki farm
    Utilities here should not depend on any extensions
    There's no intention to develop anything that's not useful on Gamepedia/Gamepedia esports wikis
    but anything that's platform or extension-specific will go in GamepediaSite instead
    """
    url = None
    client = None
    write_errors = (AssertUserFailedError, ReadTimeout, APIError)

    def __init__(self, url: str, path='/', credentials: AuthCredentials = None, client: Site = None,
                 max_retries=3, retry_interval=10, **kwargs):
        self.scheme = None
        if 'http://' in url:
            self.scheme = 'http'
            url = url.replace('http://', '')
        elif 'https://' in url:
            self.scheme = 'https'
            url = url.replace('https://', '')
        # If user specifies scheme, we'll assume they want that with precedence
        # even over specifying something in the url. Scheme is unlikely enough to be specified
        # that it's not worth making an explicit parameter, especially since we support specifying
        # it via the url.
        if 'scheme' in kwargs:
            self.scheme = kwargs.pop('scheme')

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

        self.client = session_manager.get_client(url=url, path=path, scheme=self.scheme,
                                                 credentials=credentials, **kwargs)

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

    def pages_using(self, template, namespace: Optional[Union[int, str]] = None, filterredir='all', limit=None, generator=True):
        if ':' not in template:
            title = 'Template:' + template
        elif template.startswith(':'):
            title = template[1:]
        else:
            title = template
        return self.client.pages[title].embeddedin(namespace=namespace, filterredir=filterredir,
                                                   limit=limit, generator=generator)

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

    def target(self, name: str) -> Optional[str]:
        """
        Return the name of a page's redirect target
        :param name: Name of page
        :return: Name of page's redirect target
        """
        if name is None or name == '':
            return None
        return self.client.pages[name].resolve_redirect().name

    def get_simple_pages(self, title_list: List[str], limit: int) -> List[SimplePage]:
        titles_paginated = []
        i = 0
        paginated_element = []
        for title in title_list:
            if i == limit:
                titles_paginated.append(paginated_element)
                paginated_element = []
                i = 0
            paginated_element.append(title)
            i += 1
        ret = []
        titles_paginated.append(paginated_element)
        for query in titles_paginated:
            result = self.client.api('query', prop='revisions', titles='|'.join(query), rvprop='content', rvslots='main')
            unsorted_pages = []
            for pageid in result['query']['pages']:
                row = result['query']['pages'][pageid]
                name = row['title']
                # Put empty string for the text if the page doesn't exist - it's not the job of this function to check existence
                text = row['revisions'][0]['slots']['main']['*'] if row.get('revisions') else ''
                unsorted_pages.append(SimplePage(name, text))

            # de-alphabetize & sort according to our initial order
            capitalization_corrected_query = []
            for title in query:
                capitalization_corrected_query.append(title[0].upper() + title[1:])
                # We don't know if the : is actually separating a namespace or not. So we'll put both in our lookup for
                # the purpose of re-ordering the response that the api gave us. This is a safe thing to do AS LONG AS
                # both capitalizations didn't previously exist in the original query given to us by the user
                # So along the way just double check that wasn't the case.

                # This might be a bit of a hack but it works out pretty nicely; there's only two possible ways the title
                # could be capitalized, and they end up consecutive in our list (again unless the user specifically
                # specified both separately), so when we reorder later we're guaranteed to look up and find the entry,
                # and have it be in the right order.
                if ':' in title:
                    p = title.index(':')
                    ns_ucfirst_title = title[0].upper() + title[1:p+1] + title[p+1].upper() + title[p+2:]
                    if not any([ns_ucfirst_title in q for q in titles_paginated]):
                        capitalization_corrected_query.append(ns_ucfirst_title)
            unsorted_pages.sort(key=lambda x: capitalization_corrected_query.index(x.name))
            ret += unsorted_pages
        return ret

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
        except APIError as e:
            if e.code == 'nosuchrevid' or e.code == 'nosuchrcid':
                raise PatrolRevisionInvalid
            self._retry_login_action(self._retry_patrol, 'patrol',
                                     revid=revid, rcid=rcid, token=patrol_token, **kwargs)

    def _retry_patrol(self, **kwargs):
        # one of these two must be provided but not both
        revid = kwargs.pop('revid') if 'revid' in kwargs else None
        rcid = kwargs.pop('rcid') if 'rcid' in kwargs else None

        # token is mandatory
        token = kwargs.pop('token')
        self.client.api('patrol', revid=revid, rcid=rcid, token=token, **kwargs)

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
            page.site = self.client
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

    def touch_title(self, title: str):
        self.touch(self.client.pages[title])

    def touch(self, page: Page):
        try:
            page.site = self.client
            page.touch()
        except self.write_errors:
            self._retry_login_action(self._retry_touch, 'touch', page=page)

    def _retry_touch(self, **kwargs):
        old_page = kwargs['page']
        page = self.client.pages[old_page.name]
        page.touch()

    def purge_title(self, title: str):
        self.purge(self.client.pages[title])

    def purge(self, page: Page):
        try:
            page.site = self.client
            page.purge()
        except self.write_errors:
            self._retry_login_action(self._retry_purge, 'purge', page=page)

    def _retry_purge(self, **kwargs):
        old_page = kwargs['page']
        page = self.client.pages[old_page.name]
        page.purge()

    def move(self, page: Page, new_title, reason='', move_talk=True, no_redirect=False,
             move_subpages=False, ignore_warnings=False):
        try:
            page.site = self.client
            page.move(new_title, reason=reason, move_talk=move_talk, no_redirect=no_redirect,
                      move_subpages=move_subpages, ignore_warnings=ignore_warnings)
        except APIError as e:
            if e.code == 'badtoken':
                self._retry_login_action(self._retry_move, 'move', page=page, new_title=new_title,
                                         reason=reason, move_talk=move_talk, no_redirect=no_redirect,
                                         move_subpages=move_subpages, ignore_warnings=ignore_warnings)
            else:
                raise e

    def _retry_move(self, **kwargs):
        old_page: Page = kwargs.pop('page')
        page = self.client.pages[old_page.name]
        new_title = kwargs.pop('new_title')
        page.move(new_title, **kwargs)

    def delete(self, page: Page, reason='', watch=False, unwatch=False, oldimage=False):
        try:
            page.site = self.client
            page.delete(reason=reason, watch=watch, unwatch=unwatch, oldimage=oldimage)
        except APIError as e:
            if e.code == 'badtoken':
                self._retry_login_action(self._retry_delete, 'delete', page=page, reason=reason,
                                         watch=watch, unwatch=unwatch, oldimage=oldimage)
            else:
                raise e

    def _retry_delete(self, **kwargs):
        old_page: Page = kwargs.pop('page')
        page = self.client.pages[old_page.name]
        page.delete(**kwargs)

    def _retry_login_action(self, f, failure_type, **kwargs):
        was_successful = False
        codes = []
        for retry in range(self.max_retries):
            self.relog()
            # don't sleep at all the first retry, and then increment in retry_interval intervals
            # default interval is 10, default retries is 3
            time.sleep((2 ** retry - 1) * self.retry_interval)
            try:
                f(**kwargs)
                was_successful = True
                break
            except self.write_errors as e:
                if isinstance(e, APIError):
                    codes.append(e.code)
                continue
        if not was_successful:
            raise RetriedLoginAndStillFailed(failure_type, codes)

    def save_tile(self, title: str, text, summary=None, minor=False, bot=True, section=None, **kwargs):
        self.save(self.client.pages[title], text,
                  summary=summary, minor=minor, bot=bot, section=section, **kwargs)

    def save_title(self, title: str, text, summary=None, minor=False, bot=True, section=None, **kwargs):
        self.save(self.client.pages[title], text,
                  summary=summary, minor=minor, bot=bot, section=section, **kwargs)
