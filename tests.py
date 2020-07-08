from river_mwclient.esports_client import EsportsClient
from river_mwclient.auth_credentials import AuthCredentials
from river_mwclient.gamepedia_client import GamepediaClient
from river_mwclient.errors import EsportsCacheKeyError
from river_mwclient.wiki_time_parser import time_from_str

credentials = AuthCredentials(user_file='me')

site = EsportsClient('lol', credentials=credentials)

print(site.cache.get_team_from_event_tricode('Worlds 2019 Main Event', 'SKT'))
print(site.cache.get_team_from_event_tricode('LCK 2020 Summer', 'Test'))
print(site.cache.get_team_from_event_tricode('LCK 2020 Summer', 'kt rolster'))

print(site.cache.get_disambiguated_player_from_event('Worlds 2019 Main Event', 'Splyce', 'Duke'))

print(time_from_str("2020-03-27T16:49:18+00:00").dst)

try:
    print(site.cache.get('Team', 't1', 'not_a_real_length'))
except EsportsCacheKeyError as e:
    print(e)

site.client.pages['User:RheingoldRiver/login test'].save('ki3ttens 3')

print(site.cargo_client.query_one_result(
    tables="Players",
    fields="Name",
    where="ID=\"Faker\"")
)


print(site.cargo_client.query_one_result(
    tables='Tournaments',
    where='OverviewPage="Intel Arabian Cup 2020/Egypt/Split 1"',
    fields='ScrapeLink'
))