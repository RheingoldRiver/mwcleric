from .wiki_client import WikiClient


class CargoClient(object):
    """
    Extends mwclient.Site with basic Cargo operations. No Gamepedia-specific functionality here.
    """
    client = None

    def __init__(self, client, **kwargs):
        self.client = client

    def query(self, **kwargs):
        response = self.client.api('cargoquery', **kwargs)
        ret = []
        for item in response['cargoquery']:
            ret.append(item['title'])
        return ret

    def page_list(self, fields=None, limit="max", page_pattern="%s", **kwargs):
        field = fields.split('=')[1] if '=' in fields else fields
        group_by = fields.split('=')[0]
        response = self.client.api('cargoquery',
                                   fields=fields,
                                   group_by=group_by,
                                   limit=limit,
                                   **kwargs
                                   )
        pages = []
        for item in response['cargoquery']:
            page = page_pattern % item['title'][field]
            if page in pages:
                continue
            pages.append(page)
            yield (self.client.pages[page])
