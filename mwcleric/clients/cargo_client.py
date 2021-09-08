from typing import Union, List, Optional

from mwcleric.clients.site import Site


class CargoClient(object):
    """
    Extends mwclient.Site with basic Cargo operations.
    """
    client = None

    def __init__(self, client: Site, **kwargs):
        self.client = client

    def query(self, *, tables: Union[str, List[str]], fields: Union[str, List[str]],
              where: Optional[str] = None, join_on: Optional[Union[str, List[str]]] = None,
              group_by: Optional[str] = None, having: Optional[Union[str, List[str]]] = None,
              order_by: Optional[str] = None, offset: Optional[int] = None, limit: Optional[int] = None,
              auto_continue: bool = True):
        # auto-continue & set limit to max unless the user specified a lower limit, or set auto-continue to False
        if limit is not None:
            auto_continue = False
        if auto_continue:
            limit = 'max'
        data = {}
        fields_to_concat = {
            'tables': tables,
            'fields': fields,
            'join_on': join_on,
            'having': having,
        }
        for field_name, field in fields_to_concat.items():
            if isinstance(field, list):
                data[field_name] = ', '.join(field)
            elif field is not None:
                data[field_name] = field
        fields_to_add = {
            'where': where,
            'group_by': group_by,
            'order_by': order_by,
            'offset': offset,
            'limit': limit,
        }
        for field_name, field in fields_to_add.items():
            if field is not None:
                data[field_name] = field
        ret = []
        while True:
            response = self.client.api('cargoquery', **data)
            for item in response['cargoquery']:
                ret.append(item['title'])
            if not auto_continue or response['limits']['cargoquery'] > len(response['cargoquery']):
                break
            data['offset'] = len(ret)
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
