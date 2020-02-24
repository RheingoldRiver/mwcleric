from .esports_site import EsportsSite


def login(user, wiki, **kwargs):
    """
    This function exists for backwards compatibility, but it also creates a stable wrapper for initializing
    and logging into site objects. Eventually this message will be used, but until then I'd recommend to
    use this wrapper any time you need to instantiate an esports site.
    :param user: Either "me" or "bot"
    :param wiki: Domain of a Gamepedia wiki
    :param kwargs: Sent directly to site.login
    :return: EsportsSite
    """
    site = EsportsSite(wiki)
    site.login_from_file(user, **kwargs)
    return site
