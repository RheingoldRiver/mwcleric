from mwcleric.auth_credentials import AuthCredentials
from mwcleric.clients.site import Site


class SessionManager(object):
    """Manages instances of WikiClient
    """
    existing_wikis = {}

    def get_client(self, url: str = None, path: str = None, scheme=None,
                   credentials: AuthCredentials = None, force_new=False,
                   **kwargs):
        if url in self.existing_wikis and not force_new:
            return self.existing_wikis[url]['client']
        if scheme is not None:
            client = Site(url, path=path, scheme=scheme, **kwargs)
        else:
            client = Site(url, path=path, **kwargs)
        if credentials:
            client.login(username=credentials.username, password=credentials.password)
        self.existing_wikis[url] = {'client': client}
        return client


session_manager = SessionManager()
