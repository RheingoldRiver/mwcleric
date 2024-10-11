from datetime import datetime, timedelta
import time
import calendar
from typing import Optional, Union, List, Dict, Generator

from mwcleric.clients.cargo_client import CargoClient
from mwclient.errors import APIError, MaximumRetriesExceeded
from mwclient.errors import AssertUserFailedError
from mwclient.page import Page
from requests.exceptions import ReadTimeout

from mwcleric.clients.session_manager import session_manager
from mwcleric.clients.site import Site
from mwcleric.models.namespace import Namespace
from mwcleric.models.simple_page import SimplePage
from .auth_credentials import AuthCredentials
from .errors import PatrolRevisionInvalid, InvalidNamespaceName
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
    write_errors = (AssertUserFailedError, ReadTimeout, APIError, MaximumRetriesExceeded)

    def __init__(self, url: str, path='/', credentials: AuthCredentials = None, client: Site = None,
                 max_retries=3, retry_interval=10, max_retries_mwc: int = 0, cargo: bool=False, **kwargs):
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
        self.credentials = credentials
        self.path = path
        self.kwargs = kwargs
        self.max_retries = max_retries
        self.max_retries_mwc = max_retries_mwc
        self.retry_interval = retry_interval

        self._namespaces = None
        self._ns_name_to_ns = None

        self._extensions = None

        if client:
            self.client = client
            return
        self.client = session_manager.get_client(url=url, path=path, scheme=self.scheme,
                                                 max_retries=max_retries_mwc,
                                                 credentials=credentials, **kwargs)

        if cargo is True:
            self.cargo_client = CargoClient(self.client)
        self._localization_cache = {}

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
        self.client = session_manager.get_client(url=self.url, path=self.path, scheme=self.scheme,
                                                 credentials=self.credentials, max_retries=self.max_retries_mwc,
                                                 **self.kwargs, force_new=True)

    @property
    def namespaces(self):
        if self._namespaces is not None:
            return self._namespaces
        self._populate_namespaces()
        return self._namespaces

    @property
    def ns_name_to_namespace(self) -> Dict[str, Namespace]:
        if self._ns_name_to_ns is not None:
            return self._ns_name_to_ns
        self._populate_namespaces()
        self._ns_name_to_ns: Dict[str, Namespace]
        return self._ns_name_to_ns

    def _populate_namespaces(self):
        result = self.client.api('query', meta='siteinfo', siprop="namespaces|namespacealiases")
        ns_aliases = {}
        for alias in result['query']['namespacealiases']:
            alias_key = str(alias['id'])
            if alias_key not in ns_aliases:
                ns_aliases[alias_key] = []
            ns_aliases[alias_key].append(alias['*'])
        ns_list = []
        ns_map = {}
        for ns_str, ns_data in result['query']['namespaces'].items():
            ns = int(ns_str)
            canonical = ns_data.get('canonical')
            aliases = ns_aliases.get(ns_str)
            ns_obj = Namespace(id_number=ns, name=ns_data['*'],
                               canonical_name=canonical, aliases=aliases)
            ns_list.append(ns_obj)
            ns_map[ns_data['*']] = ns_obj
            if canonical is not None:
                ns_map[canonical] = ns_obj
            if aliases is not None:
                for alias in aliases:
                    ns_map[alias] = ns_obj
        self._namespaces = ns_list
        self._ns_name_to_ns = ns_map

    def get_ns_number(self, ns: str):
        ns_obj = self.ns_name_to_namespace.get(ns)
        if ns_obj is None:
            raise InvalidNamespaceName
        return ns_obj.id

    def pages_using(self, template: Union[str, List[str]], namespace: Optional[Union[int, str]] = None,
                    filterredir='all', limit=None, generator=True,
                    unique=True) -> Union[List[Page], Generator[Page, None, None]]:
        """
        Returns the list of pages using the provided template or templates

        :param template: A template or list of templates to operate on
        :param namespace: Optional - the namespace to restrict the result set to
        :param filterredir: Passed directly to the MediaWiki api - filter redirects in the result?
        :param limit: Passed directly to the MediaWiki api - limit the number of results?
        :param generator: Default True - return result as a generator? If False, result will be a list
        :param unique: Default True, but only has an effect if `generator` is False. Remove duplicates from the list output?
        :return: A list or generator of Page objects containing all the results of what transcludes the input(s)
        """
        if isinstance(namespace, str):
            namespace = self.get_ns_number(namespace)
        if isinstance(template, str):
            return self._pages_using_single(template=template, namespace=namespace, filterredir=filterredir,
                                            limit=limit, generator=generator)

        if generator is False:
            ret = []
            for tl in template:
                new_ret = self._pages_using_single(template=tl, namespace=namespace, filterredir=filterredir,
                                                   limit=limit, generator=generator)
                ret += new_ret
            if unique:
                return list(set(ret))
            return ret

        return self._pages_using_gen(template=template, namespace=namespace, filterredir=filterredir,
                                     limit=limit)

    def _pages_using_single(self, template: str, namespace: Optional[int], filterredir, limit, generator):
        if ':' not in template:
            title = 'Template:' + template
        elif template.startswith(':'):
            title = template[1:]
        else:
            title = template
        return self.client.pages[title].embeddedin(namespace=namespace, filterredir=filterredir,
                                                   limit=limit, generator=generator)

    def _pages_using_gen(self, template: List[str], namespace: Optional[int], filterredir,
                         limit) -> Generator[Page, None, None]:
        for tl in template:
            next_ret = self._pages_using_single(template=tl, namespace=namespace, filterredir=filterredir,
                                                limit=limit, generator=True)
            for p in next_ret:
                yield p

    def recentchanges_by_interval(self, minutes, offset=0,
                                  prop='title|ids|tags|user|patrolled', **kwargs):
        now = datetime.utcnow() - timedelta(minutes=offset)
        then = now - timedelta(minutes=minutes)
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
            result = self.client.api('query', prop='revisions', titles='|'.join(query), rvprop='content',
                                     rvslots='main')
            unsorted_pages = []
            for pageid in result['query']['pages']:
                row = result['query']['pages'][pageid]
                name = row['title']
                text = row['revisions'][0]['slots']['main']['*'] if row.get('revisions') else ''
                exists = True if row.get('revisions') else False
                unsorted_pages.append(SimplePage(name=name, text=text, exists=exists))

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
                    ns_ucfirst_title = title[0].upper() + title[1:p + 1] + title[p + 1].upper() + title[p + 2:]
                    if not any([ns_ucfirst_title in q for q in titles_paginated]):
                        capitalization_corrected_query.append(ns_ucfirst_title)
            unsorted_pages.sort(key=lambda x: capitalization_corrected_query.index(x.name))
            ret += unsorted_pages
        return ret

    def logs_by_interval(self, minutes, offset=0,
                         lelimit="max",
                         leprop='details|type|title|tags', **kwargs):
        now = datetime.utcnow() - timedelta(minutes=offset)
        then = now - timedelta(minutes=minutes)
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
        data = {
            'from': page.name,
            'to': new_title,
            'reason': reason,
            'movetalk': 1 if move_talk else None,
            'movesubpages': 1 if move_subpages else None,
            'noredirect': 1 if no_redirect else None,
            'ignorewarnings': 1 if ignore_warnings else None,
        }
        move_token = self.client.get_token('move')
        try:
            self.client.api('move', **data, token=move_token)
        except APIError as e:
            if e.code == 'badtoken':
                self._retry_login_action(self._retry_move, 'move', **data, token=move_token)
            else:
                raise e

    def _retry_move(self, **kwargs):
        # token is mandatory
        token = kwargs.pop('token')
        self.client.api('move', token=token, **kwargs)

    def protect(self, page: Page, protections="edit=sysop|move=sysop", expiry="infinite", reason=None, **data):
        data.update({
            'title': page.name,
            'protections': protections,
            'expiry': expiry,
            'reason': reason,
        })
        protect_token = self.client.get_token('csrf')
        try:
            self.client.api('protect', **data, token=protect_token)
        except APIError as e:
            if e.code == 'badtoken':
                self._retry_login_action(self._retry_protect, 'move', **data, token=protect_token)
            else:
                raise e

    def _retry_protect(self, **kwargs):
        token = kwargs.pop('token')
        self.client.api('protect', token=token, **kwargs)

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

    def append(self, page: Page, append_text, summary=u'', minor=False, bot=True, section=None,
               **kwargs):
        try:
            page.site = self.client
            page.append(append_text, summary=summary, minor=minor, bot=bot, section=section, **kwargs)
        except self.write_errors:
            self._retry_login_action(self._retry_append, 'append', page=page, text=append_text, summary=summary,
                                     minor=minor, bot=bot, section=section, **kwargs)

    def _retry_append(self, **kwargs):
        old_page: Page = kwargs.pop('page')
        # recreate the page object so that we're using the new site object, post-relog
        page = self.client.pages[old_page.name]
        text = kwargs.pop('text')
        page.append(text, **kwargs)

    def prepend(self, page: Page, prepend_text, summary=u'', minor=False, bot=True, section=None,
                **kwargs):
        try:
            page.site = self.client
            page.prepend(prepend_text, summary=summary, minor=minor, bot=bot, section=section, **kwargs)
        except self.write_errors:
            self._retry_login_action(self._retry_prepend, 'prepend', page=page, text=prepend_text, summary=summary,
                                     minor=minor, bot=bot, section=section, **kwargs)

    def _retry_prepend(self, **kwargs):
        old_page: Page = kwargs.pop('page')
        # recreate the page object so that we're using the new site object, post-relog
        page = self.client.pages[old_page.name]
        text = kwargs.pop('text')
        page.prepend(text, **kwargs)

    def append_title(self, title: str, append_text, summary=u'', minor=False, bot=True, section=None,
                     **kwargs):
        self.append(self.client.pages[title], append_text,
                    summary=summary, minor=minor, bot=bot, section=section, **kwargs)

    def prepend_title(self, title: str, prepend_text, summary=u'', minor=False, bot=True, section=None,
                      **kwargs):
        self.prepend(self.client.pages[title], prepend_text,
                     summary=summary, minor=minor, bot=bot, section=section, **kwargs)

    def upload(self, file: str = None, filename: str = None, description: str = None, ignore_warnings: bool = False,
               url: str = None, filekey: str = None, comment: str = None, **kwargs):
        """
        Uploads a file from a local directory or a URL. Only one of file, filekey or url must be specified.
        Retries in case the upload fails.

        :param file: File object to upload
        :param filename: Destination filename without including a prefix like File:
        :param description: Wikitext description for the file
        :param ignore_warnings: Whether to ignore warnings raised by the API
        :param url: URL to fetch the file from, disabled in some wikis
        :param filekey: Key that identifies a previous upload that was stashed temporarily
        :param comment: Comment for the upload, will be used as the initial page text for new files if description is not provided.
        :param kwargs: Extra arguments to be passed to mwclient
        """
        request_errors = ("mustbeloggedin", "permissiondenied", "fileexists-shared-forbidden", "chunk-too-small",
                          "stashfailed", "verification-error", "windows-nonascii-filename", "copyuploaddisabled",
                          "fileexists-no-change")
        try:
            self.client.upload(file=file, filename=filename, description=description, ignore=ignore_warnings,
                               url=url, filekey=filekey, comment=comment, **kwargs)
        except self.write_errors as e:
            # If the returned error code is our fault then don't retry
            if type(e) == APIError and e.code in request_errors:
                raise e
            self._retry_login_action(self.client.upload, 'upload', file=file, filename=filename,
                                     description=description, ignore=ignore_warnings, url=url,
                                     filekey=filekey, comment=comment, **kwargs)

    def last_edited_interval(self, page: Union[Page, str]) -> timedelta:
        if type(page) == str:
            page = self.client.pages[page]
        if page.last_rev_time is None:
            # force last_rev_time to populate
            _text = page.text()
        return datetime.now() - datetime.fromtimestamp(calendar.timegm(page.last_rev_time))

    @property
    def extensions(self):
        if self._extensions is not None:
            return self._extensions
        result = self.client.get('query', meta='siteinfo', formatversion=2, siprop='extensions')
        self._extensions = [_['name'] for _ in result['query']['extensions']]
        return self._extensions

    def localize(self, s: str, uselang: Optional[str] = None) -> Optional[str]:
        if s in self._localization_cache:
            return self._localization_cache[s]
        if uselang is None:
            uselang = self.client.site['lang']
        res = self.client.get('query', meta='allmessages', ammessages=s, uselang=uselang)
        if 'missing' in res['query']['allmessages'][0]:
            return None
        return res['query']['allmessages'][0]['*']
