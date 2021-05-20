from mwcleric.models.logs.log_entry import LogEntry
from mwcleric.wiki_client import WikiClient


class MoveLogEntry(LogEntry):
    def __init__(self, log, site: WikiClient):
        super().__init__(log, site)
        self.title = log['params']['target_title']
        self.page = site.client.pages[self.title]
