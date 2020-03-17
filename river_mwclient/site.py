from mwclient import Site as MwclientSite


class Site(MwclientSite):
    """Wrap mwclient since we might include a site object in constructors"""
    pass
