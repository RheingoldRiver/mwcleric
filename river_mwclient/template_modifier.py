from mwparserfromhell import parse
from .wiki_client import WikiClient
from .page_modifier import PageModifierBase
from .errors import TemplateModifierNotImplemented


class TemplateModifierBase(PageModifierBase):
    def __init__(self, site: WikiClient, template, page_list=None, limit=-1, summary=None, startat_page=None):
        self.template_name = template
        self.current_template = None
        page_list = page_list if page_list else site.pages_using(template)
        super().__init__(site, page_list=page_list, limit=limit, summary=summary, startat_page=startat_page)

    def update_page(self):
        for template in self.current_wikitext.filter_templates():
            if template.name.matches(self.template_name):
                self.current_template = template
                self.update_template()

    def update_template(self):
        raise TemplateModifierNotImplemented()
