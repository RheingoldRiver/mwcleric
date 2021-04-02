from mwcleric.auth_credentials import AuthCredentials
from mwcleric.fandom_client import FandomClient
from mwcleric.wiki_client import WikiClient

credentials = AuthCredentials(user_file='me')

# check schemes
site1 = WikiClient('https://wikisandbox-ucp.fandom.com', credentials=credentials)
site2 = WikiClient('http://wikisandbox-ucp.fandom.com', scheme='https', credentials=credentials)
site3 = FandomClient('leagueoflegends', lang='de', credentials=credentials)

site = FandomClient('lol', credentials=credentials)

backlinks = []
for page in site.pages_using('PBH'):
    backlinks.append(page.name)
assert 'Template:PBH' in backlinks

assert site.target('Main Page') == 'League of Legends Esports Wiki'
