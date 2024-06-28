from mwclient.page import Page
from mwparserfromhell import parse
from time import sleep

from mwparserfromhell.wikicode import Wikicode

from .wiki_client import WikiClient


class PageModifierBase(object):
    """
    Update pages on a wiki by using update_wikitext or update_plaintext.

    Available attributes you can change:

    * self.current_text (do this in self.update_plaintext()
    * self.current_wikitext (do this in self.update_wikitext()

    Available attributes you can use but not modify:

    * self.current_page, which is an mwclient Page, so you can access page.name, etc
    * self.site, a WikiClient object

    Specify a summary on initialization along with either a page_list or a title_list.

    * page_list is a list of Page objects (for example maybe site.client.categories)
    * title_list is a list of strings which will be turned into Page objects
    """
    current_page: Page = None
    current_text: str = None
    current_wikitext: Wikicode = None
    prioritize_plaintext: bool = False
    prioritize_wikitext: bool = False

    def __init__(self, site: WikiClient, page_list=None, title_list=None, limit=-1, summary=None, startat_page=None,
                 tags=None, skip_pages=None,
                 quiet=False, lag=0, **data):
        """Create a PageModifier object, which can perform operations to edit the plaintext
        or wikitext of a page.

        :param site: a WikiClient to perform the edits on
        :param page_list: a list of Page objects to operate on, do not use with title_list
        :param title_list: a list of title strings to operate on, do not use with page_list
        :param limit: stop after scanning this many pages
        :param summary: edit summary
        :param startat_page: skip to this page
        :param quiet: don't print any console output (set to True for cron processes)
        :param lag: sleep this many seconds before saving
        :param data: Extra keywords to save to the class for use in the update_wikitext/update_plaintext methods
        """
        self.title_list = title_list
        self.summary = summary if summary else 'Bot Edit'
        self.site = site
        self.page_list = page_list
        self.limit = limit
        self.passed_startat = False if startat_page else True
        self.startat_page = startat_page
        self.skip_pages = skip_pages if skip_pages is not None else []
        self.lag = lag
        self.quiet = quiet
        self.tags = tags
        self.data = data
        self.lmt = 0

    def _print(self, s):
        """Print iff the quiet flag is not set to True"""
        if self.quiet:
            return
        print(s)

    def update_wikitext(self, wikitext):
        """This will be run iff update_wikitext isn't overridden in a subclass.
        
        Modify wikitext in place.
        """
        self.prioritize_plaintext = True

    def update_plaintext(self, text):
        """This will be run iff update_plaintext isn't overridden in a subclass.
        
        Modify text and return it.
        """
        self.prioritize_wikitext = True
        return text

    def postprocess_plaintext(self, text):
        """This method may not be supported forever, do not use it!!!

        It's only here because TemplateModifier requires it due to mwparserfromhell's node removal
        not completely removing newlines when removing nodes.
        """
        return text

    def run(self):
        if self.page_list is not None:
            for page in self.page_list:
                if not self.process_page(page):
                    break
        elif self.title_list is not None:
            for title in self.title_list:
                page = self.site.client.pages[title]
                if not self.process_page(page):
                    break

    def process_page(self, page):
        if self.lmt == self.limit:
            return False
        if self.startat_page and page.name == self.startat_page:
            self.passed_startat = True
        if not self.passed_startat:
            self._print("Skipping page %s, before startat" % page.name)
            return True
        if page.name in self.skip_pages:
            self._print("Skipping page %s as requested" % page.name)
            return True
        self.lmt += 1
        self.current_text = page.text()
        self.current_page = page
        self.current_wikitext = parse(self.current_text)
        self.current_text = self.update_plaintext(self.current_text)
        self.update_wikitext(self.current_wikitext)
        newtext = str(self.current_wikitext)

        # TODO: If mwparserfromhell has better support for removing nodes from wikitext,
        # delete postprocess_plaintext method
        newtext = self.postprocess_plaintext(newtext)
        if newtext != self.current_page.text() and not self.prioritize_plaintext:
            self._print('Saving page %s...' % page.name)
            sleep(self.lag)
            self.site.save(page, newtext, summary=self.summary, tags=self.tags)
        elif self.current_text != self.current_page.text():
            self._print('Saving page %s...' % page.name)
            sleep(self.lag)
            self.site.save(page, self.current_text, summary=self.summary, tags=self.tags)
        else:
            self._print('Skipping page %s...' % page.name)
        return True
