from esports_site import EsportsSite


def login(user, wiki, **kwargs):
    return EsportsSite(user, wiki, **kwargs)
