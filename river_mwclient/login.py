from .esports_site import EsportsSite


def login(user, wiki, **kwargs):
    """
    :param user: Either "me" or "bot"
    :param wiki: Domain of a Gamepedia wiki
    :param kwargs: Sent directly to site.login
    :return: EsportsSite
    """
    site = EsportsSite(wiki)
    site.login_from_file(user, **kwargs)
    return site
