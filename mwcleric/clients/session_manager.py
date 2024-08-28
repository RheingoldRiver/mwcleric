from typing import Optional

from mwcleric.auth_credentials import AuthCredentials
from mwcleric.clients.site import Site


class SessionManager(object):
    """Manages instances of WikiClient
    """
    existing_wikis = {}

    def get_client(self, url: str = None, path: str = None, scheme=None,
                   credentials: AuthCredentials = None, force_new=False,
                   max_retries: int = 10,
                   http_user: Optional[str] = None,
                   http_pw: Optional[str] = None,
                   **kwargs):
        if http_user is not None and http_pw is not None:
            url = f"{http_user}:{http_pw}@{url}"
        if url in self.existing_wikis and not force_new:
            return self.existing_wikis[url]['client']
        if scheme is not None:
            client = Site(url, path=path, scheme=scheme, max_retries=max_retries, **kwargs)
        else:
            client = Site(url, path=path, max_retries=max_retries, **kwargs)
        if credentials:
            client.login(username=credentials.username, password=credentials.password)
        self.existing_wikis[url] = {'client': client}
        return client


session_manager = SessionManager()
