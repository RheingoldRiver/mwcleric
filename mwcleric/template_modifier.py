import re
from copy import deepcopy
from typing import Optional, Union

from mwparserfromhell.nodes import Template

from .errors import TemplateModifierNotImplemented
from .page_modifier import PageModifierBase
from .wiki_client import WikiClient


class TemplateModifierBase(PageModifierBase):
    def __init__(self, site: WikiClient, template, page_list=None, title_list=None, limit=-1, summary=None,
                 quiet=False, lag=0, tags=None, skip_pages=None,
                 recursive=True,
                 startat_page=None,
                 namespace: Optional[Union[int, str]] = None,
                 **data):
        """

        :param site: WikiClient site
        :param template: The template to modify
        :param page_list: A default page_list parameter. Otherwise the template's used_in list will be used
        :param title_list: See page_list.
        :param limit: See PageModifier class.
        :param summary: See PageModifier class.
        :param quiet: See PageModifier class.
        :param lag: See PageModifier class.
        :param tags: See PageModifier class.
        :param skip_pages: See PageModifier class.
        :param recursive: See mwparserfromhell.wikitext.filter_templates method
        :param startat_page: See PageModifier class
        :param namespace: Do we filter the template's used_in list?
        :param data: Extra keywords to save to the class for use in the update_template method
        """
        self.template_name = template
        self.current_template = None
        self.recursive = recursive
        self.check_deletion_marks = False
        self.invoke_namespace = None
        if title_list is None:
            page_list = page_list if page_list else site.pages_using(template, namespace=namespace)
        super().__init__(site, page_list=page_list, title_list=title_list, limit=limit, summary=summary,
                         quiet=quiet, lag=lag, tags=tags, skip_pages=skip_pages,
                         startat_page=startat_page, **data)

    def update_wikitext(self, wikitext):
        for template in wikitext.filter_templates(recursive=self.recursive):
            name = template.name
            # handle Scribunto modules
            # see https://github.com/earwig/mwparserfromhell/issues/287
            if name.startswith('#invoke:'):
                if self.invoke_namespace is None:
                    self.invoke_namespace = self.site.ns_name_to_namespace.get('Module', False)
                if self.invoke_namespace:
                    name = deepcopy(name)
                    # replace with localized namespace
                    name.replace('#invoke:', self.invoke_namespace.name + ':')
            if name.matches(self.template_name):
                self.current_template = template
                self.update_template(template)

    def update_template(self, template):
        raise TemplateModifierNotImplemented()

    def remove_from_page(self):
        """
        Marks the template to remove it completely from the page in a later layer of processing
        """
        # we are not using wikitext.remove(node) because we want to clean up newlines later
        self.current_template: Template
        params = []
        for param in self.current_template.params:
            params.append(param.name.strip())
        for param in params:
            self.current_template.remove(param)

        self.current_template.name = '@@@DELETE@@@'
        self.check_deletion_marks = True

    def postprocess_plaintext(self, text):
        if not self.check_deletion_marks:
            return text

        # case: middle of article, with extra whitespace on each side
        text = text.replace('\n\n{{@@@DELETE@@@}}\n\n', '\n\n')
        # case: middle of article
        text = text.replace('\n{{@@@DELETE@@@}}\n', '\n')
        # case: beginning of article
        text = re.sub('^' + re.escape('{{@@@DELETE@@@}}\n'), '', text)
        # case: middle of a line or whatever
        text = text.replace('{{@@@DELETE@@@}}', '')
        return text
