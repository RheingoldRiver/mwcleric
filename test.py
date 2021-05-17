from mwcleric.auth_credentials import AuthCredentials
from mwcleric.fandom_client import FandomClient
from mwcleric.wiki_client import WikiClient

credentials = AuthCredentials(user_file='me')

# check schemes
site1 = WikiClient('https://wikisandbox-ucp.fandom.com', credentials=credentials)
site2 = WikiClient('http://wikisandbox-ucp.fandom.com', scheme='https', credentials=credentials)
site3 = FandomClient('leagueoflegends', lang='de', credentials=credentials)

site = FandomClient('lol', credentials=credentials)

assert 'Template:PBH' in site.pages_using('PBH', namespace='Template', generator=False)

assert 'Template:PBH' in site.pages_using('PBH', namespace=10, generator=False)

assert site.target('Main Page') == 'League of Legends Esports Wiki'

titles = ['Faker', 'Bengi', 'Module:CargoUtil',
          'Main Page', 'Template:Infobox Player', 'Amazing',
          'lowercasepagethatdoesntexist', 'Module:lowercasepagethatdoesntexist', 'Notanamespace:lowercasepagethatdoesntexist',
          'Notanamespace:asd', 'Notanamespace:Asd']
pages = site.get_simple_pages(titles, 3)
assert len(pages) == len(titles)
assert pages[0].name == 'Faker'
assert pages[2].name == 'Module:CargoUtil'
assert pages[6].text == ''
assert pages[6].name == 'Lowercasepagethatdoesntexist'
assert pages[9].name == 'Notanamespace:asd'
assert pages[10].name == 'Notanamespace:Asd'
