from mwparserfromhell import parse
from .wiki_client import WikiClient
from .errors import PageModifierNotImplemented


class PageModifierBase(object):
    current_page = None
    current_text = None
    current_wikitext = None
    prioritize_plaintext = False
    prioritize_wikitext = False

    def __init__(self, site: WikiClient, page_list=None, title_list=None, limit=-1, summary=None, startat_page=None):
        if title_list is not None:
            page_list = [site.client.pages[p] for p in title_list]
        self.summary = summary if summary else 'Bot Edit'
        self.site = site
        self.page_list = page_list
        self.limit = limit
        self.passed_startat = False if startat_page else True
        self.startat_page = startat_page

    def update_wikitext(self):
        self.prioritize_plaintext = True

    def update_plaintext(self):
        self.prioritize_wikitext = True

    def run(self):
        lmt = 0
        for page in self.page_list:
            if lmt == self.limit:
                break
            if self.startat_page and page.name == self.startat_page:
                self.passed_startat = True
            if not self.passed_startat:
                print("Skipping page %s, before startat" % page.name)
                continue
            lmt += 1
            self.current_text = page.text()
            self.current_page = page
            self.current_wikitext = parse(self.current_text)
            self.update_plaintext()
            self.update_wikitext()
            newtext = str(self.current_wikitext)
            if newtext != self.current_page.text() and not self.prioritize_plaintext:
                print('Saving page %s...' % page.name)
                page.save(newtext, summary=self.summary)
            elif self.current_text != self.current_page.text():
                print('Saving page %s...' % page.name)
                page.save(self.current_text, summary=self.summary)
            else:
                print('Skipping page %s...' % page.name)
