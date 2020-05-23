from .errors import TemplateModifierNotImplemented
from .page_modifier import PageModifierBase
from .wiki_client import WikiClient


class TemplateModifierBase(PageModifierBase):
    def __init__(self, site: WikiClient, template, page_list=None, title_list=None, limit=-1, summary=None,
                 quiet=False,
                 startat_page=None):
        self.template_name = template
        self.current_template = None
        if not title_list:
            page_list = page_list if page_list else site.pages_using(template)
        super().__init__(site, page_list=page_list, title_list=title_list, limit=limit, summary=summary,
                         quiet=quiet,
                         startat_page=startat_page)
    
    def update_wikitext(self):
        for template in self.current_wikitext.filter_templates():
            if template.name.matches(self.template_name):
                self.current_template = template
                self.update_template()
    
    def update_template(self):
        raise TemplateModifierNotImplemented()
