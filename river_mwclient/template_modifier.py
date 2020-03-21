from mwparserfromhell import parse
from .wiki_client import WikiClient
from .errors import TemplateModifierNotImplemented


class TemplateModifierBase(object):
    def __init__(self, site: WikiClient, template, page_list=None, limit=-1, summary=None, startat_page=None):
        self.summary = summary if summary else 'Bot Edit'
        self.site = site
        self.template_name = template
        self.page_list = page_list if page_list else site.pages_using(template)
        self.limit = limit
        self.passed_startat = False if startat_page else True
        self.startat_page = startat_page

    def update(self, template):
        raise TemplateModifierNotImplemented()

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
            text = page.text()
            wikitext = parse(text)
            for template in wikitext.filter_templates():
                if template.name.matches(self.template_name):
                    self.update(template)

            newtext = str(wikitext)
            if text != newtext:
                print('Saving page %s...' % page.name)
                page.save(newtext, summary=self.summary)
            else:
                print('Skipping page %s...' % page.name)
