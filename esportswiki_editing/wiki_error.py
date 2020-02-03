from mwclient.page import Page


class WikiError(object):
    def __init__(self, page: Page, e: Exception):
        self.title = page.name
        self.error = e

    def format_for_print(self):
        self.error:Exception
        return '{}: {} - {}'.format(type(self.error), self.title, self.error)
