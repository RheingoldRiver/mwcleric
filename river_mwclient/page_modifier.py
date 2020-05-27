from mwparserfromhell import parse
from time import sleep

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
    current_page = None
    current_text = None
    current_wikitext = None
    prioritize_plaintext = False
    prioritize_wikitext = False
    
    def __init__(self, site: WikiClient, page_list=None, title_list=None, limit=-1, summary=None, startat_page=None,
                 quiet=False, lag=0):
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
        """
        if title_list is not None:
            page_list = [site.client.pages[p] for p in title_list]
        self.summary = summary if summary else 'Bot Edit'
        self.site = site
        self.page_list = page_list
        self.limit = limit
        self.passed_startat = False if startat_page else True
        self.startat_page = startat_page
        self.lag = lag
        self.quiet = quiet
    
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
    
    def run(self):
        lmt = 0
        for page in self.page_list:
            if lmt == self.limit:
                break
            if self.startat_page and page.name == self.startat_page:
                self.passed_startat = True
            if not self.passed_startat:
                self._print("Skipping page %s, before startat" % page.name)
                continue
            lmt += 1
            self.current_text = page.text()
            self.current_page = page
            self.current_wikitext = parse(self.current_text)
            self.current_text = self.update_plaintext(self.current_text)
            self.update_wikitext(self.current_wikitext)
            newtext = str(self.current_wikitext)
            if newtext != self.current_page.text() and not self.prioritize_plaintext:
                self._print('Saving page %s...' % page.name)
                sleep(self.lag)
                page.save(newtext, summary=self.summary)
            elif self.current_text != self.current_page.text():
                self._print('Saving page %s...' % page.name)
                sleep(self.lag)
                page.save(self.current_text, summary=self.summary)
            else:
                self._print('Skipping page %s...' % page.name)
