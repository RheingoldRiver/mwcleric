from river_mwclient.wiki_client import WikiClient


class LogEntry(object):
    def __init__(self, log, site: WikiClient):
        self.site = site
        self.log_type = log['type']
        self.title = log['title']
        self.page = site.client.pages[self.title]
        self.logid = log['logid']
        self.comment = log['comment']
        self.user = log['user']
