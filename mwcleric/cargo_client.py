from mwclient import InvalidResponse

from mwcleric.site import Site


class CargoClient(object):
    """
    Extends mwclient.Site with basic Cargo operations. No Gamepedia-specific functionality here.
    """
    client = None
    
    def __init__(self, client: Site, **kwargs):
        self.client = client

    def query(self, **kwargs):
        response = self.client.api('cargoquery', **kwargs)
        ret = []
        for item in response['cargoquery']:
            ret.append(item['title'])
        return ret
        
    def query_one_result(self, fields, **kwargs):
        rows = self.query(fields=fields, **kwargs)
        field = fields.split('=')[1] if '=' in fields else fields
        if len(rows) == 0:
            return None
        row = rows[0]
        if field not in row:
            return None
        return row[field]
    
    def page_list(self, fields=None, limit="max", page_pattern="%s", **kwargs):
        if isinstance(fields, list):
            fields = ', '.join(fields)
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
            yield self.client.pages[page]
    
    def create(self, templates):
        self.recreate(templates, replacement=False)
    
    def recreate(self, templates, replacement=True):
        if isinstance(templates, str):
            templates = [templates]
        token = self.client.get_token('csrf')
        for template in templates:
            if not replacement:
                self.client.api('cargorecreatetables', template=template, token=token)
                continue
            self.client.api('cargorecreatetables', template=template, createReplacement=1, token=token)
