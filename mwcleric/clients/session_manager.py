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
                   user_agent: Optional[str] = None,
                   **kwargs):
        if http_user is not None and http_pw is not None:
            url = f"{http_user}:{http_pw}@{url}"
        if url in self.existing_wikis and not force_new:
            return self.existing_wikis[url]['client']
        if credentials and not user_agent:
            user_agent = credentials.user_agent
        client_kwargs = dict(
            path=path,
            max_retries=max_retries,
            clients_useragent=user_agent,
            **kwargs
        )
        if scheme is not None:
            client = Site(url, scheme=scheme, **client_kwargs)
        else:
            client = Site(url, **client_kwargs)
        if credentials:
            client.login(username=credentials.username, password=credentials.password)
        self.existing_wikis[url] = {'client': client}
        return client


session_manager = SessionManager()
