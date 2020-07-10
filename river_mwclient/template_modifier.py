from .errors import TemplateModifierNotImplemented
from .page_modifier import PageModifierBase
from .wiki_client import WikiClient


class TemplateModifierBase(PageModifierBase):
    def __init__(self, site: WikiClient, template, page_list=None, title_list=None, limit=-1, summary=None,
                 quiet=False, lag=0, tags=None, skip_pages=None,
                 recursive=False,
                 startat_page=None):
        self.template_name = template
        self.current_template = None
        self.recursive=recursive
        if not title_list:
            page_list = page_list if page_list else site.pages_using(template)
        super().__init__(site, page_list=page_list, title_list=title_list, limit=limit, summary=summary,
                         quiet=quiet, lag=lag, tags=tags, skip_pages=skip_pages,
                         startat_page=startat_page)
    
    def update_wikitext(self, wikitext):
        for template in wikitext.filter_templates(recursive=self.recursive):
            if template.name.matches(self.template_name):
                self.current_template = template
                self.update_template(template)
    
    def update_template(self, template):
        raise TemplateModifierNotImplemented()
