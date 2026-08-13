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
        if credentials and not user_agent:
            user_agent = credentials.user_agent
        process_cache_key = (
            url,
            credentials and credentials.username,
            user_agent
        )
        if process_cache_key in self.existing_wikis and not force_new:
            return self.existing_wikis[process_cache_key]['client']
        client_kwargs = dict(
            path=path,
            max_retries=max_retries,
            clients_useragent=user_agent,
            custom_headers=dict(),
            **kwargs
        )

        # Bind the Cloudflare token if provided in the credentials
        if credentials and credentials.cloudflare_token_id and credentials.cloudflare_token_secret:
            client_kwargs['custom_headers']['CF-Access-Client-Id'] = credentials.cloudflare_token_id
            client_kwargs['custom_headers']['CF-Access-Client-Secret'] = credentials.cloudflare_token_secret

        if scheme is not None:
            client = Site(url, scheme=scheme, **client_kwargs)
        else:
            client = Site(url, **client_kwargs)
        if credentials:
            client.login(username=credentials.username, password=credentials.password)
        self.existing_wikis[process_cache_key] = {'client': client}
        return client


session_manager = SessionManager()
