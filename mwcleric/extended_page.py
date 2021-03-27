from mwclient.page import Page


class ExtendedPage(Page):
    def __init__(self, page):
        super().__init__(page.site, page.name, info=page._info)
        self.base_title = self.page_title.split('/')[0]
        self.base_name = self.name.split('/')[0]
    
    @staticmethod
    def extend_pages(page_gen):
        for page in page_gen:
            yield ExtendedPage(page)
