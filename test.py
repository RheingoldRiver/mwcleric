from mwcleric.auth_credentials import AuthCredentials
from mwcleric.fandom_client import FandomClient
from mwcleric.wiki_client import WikiClient
from mwcleric.wikigg_client import WikiGGClient

credentials = AuthCredentials(user_file='me')
f_credentials = AuthCredentials(user_file='fme')

# check schemes
site1 = WikiClient('https://terraria.wiki.gg', credentials=credentials)
page1 = site1.client.pages['User:RheingoldRiver/mwcleric test']
site2 = WikiClient('http://terraria.wiki.gg', scheme='https', credentials=credentials)
page2 = site2.client.pages['User:RheingoldRiver/mwcleric test']
site3 = WikiClient('https://terraria.wiki.gg', credentials=credentials)
page3 = site3.client.pages['User:RheingoldRiver/mwcleric test']
site4 = FandomClient('leagueoflegends', lang='de', credentials=f_credentials)
page4 = site4.client.pages['User:RheingoldRiver/mwcleric test']
site5 = WikiGGClient('terraria', credentials=credentials)
page5 = site5.client.pages['User:RheingoldRiver/mwcleric test']
page5.save(int(page5.text() or 0) + 1)
site6 = WikiGGClient('terraria', lang='pl', credentials=credentials)
page6 = site6.client.pages['User:RheingoldRiver/mwcleric test']
page6.save(int(page6.text() or 0) + 1)


site = FandomClient('lol', credentials=f_credentials)
cargo_site = FandomClient('help-esports')

assert 'Template:PBH' in site.pages_using('PBH', namespace='Template', generator=False)

assert 'Template:PBH' in site.pages_using('PBH', namespace=10, generator=False)
assert 'Portal:Champions/List' in site.pages_using('PortalChampionList/Start', namespace='Portal', generator=False)
assert 'Leaguepedia:Blocking Policy' in site.pages_using('CommunityNavbox', namespace='Project', generator=False)
assert 'Leaguepedia:Blocking Policy' in site.pages_using('CommunityNavbox', namespace='Leaguepedia', generator=False)

assert site.target('Main Page') == 'League of Legends Esports Wiki'

titles = ['Faker', 'Bengi', 'Module:CargoUtil',
          'Main Page', 'Template:Infobox Player', 'Amazing',
          'lowercasepagethatdoesntexist', 'Module:lowercasepagethatdoesntexist',
          'Notanamespace:lowercasepagethatdoesntexist',
          'Notanamespace:asd', 'Notanamespace:Asd']
pages = site.get_simple_pages(titles, 3)
assert len(pages) == len(titles)
assert pages[0].name == 'Faker'
assert pages[0].exists is True
assert pages[2].name == 'Module:CargoUtil'
assert pages[6].text == ''
assert pages[6].exists is False
assert pages[6].name == 'Lowercasepagethatdoesntexist'
assert pages[9].name == 'Notanamespace:asd'
assert pages[10].name == 'Notanamespace:Asd'

assert len(cargo_site.cargo_client.query(tables='MwclericTest', fields='Counter')) == 550

assert len(cargo_site.cargo_client.query(tables='MwclericTest', fields='Counter', limit=50)) == 50

assert len(cargo_site.cargo_client.query(tables='MwclericTest', fields='Counter', where='Counter > 500')) == 50

assert len(cargo_site.cargo_client.query(tables='MwclericTest', fields='Counter', group_by='_pageName')) == 1
