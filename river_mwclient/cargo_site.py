import mwclient
from .extended_site import ExtendedSite


class CargoSite(ExtendedSite):
    """
    Extends mwclient.Site with basic Cargo operations. No Gamepedia-specific functionality here.
    """
    def cargoquery(self, **kwargs):
        response = self.api('cargoquery', **kwargs)
        ret = []
        for item in response['cargoquery']:
            ret.append(item['title'])
        return ret

    def cargo_pagelist(self, fields=None, limit="max", page_pattern="%s", **kwargs):
        field = fields.split('=')[1] if '=' in fields else fields
        group_by = fields.split('=')[0]
        response = self.api('cargoquery',
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
            yield (self.pages[page])
