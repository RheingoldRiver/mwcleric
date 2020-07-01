from river_mwclient.esports_client import EsportsClient
from river_mwclient.auth_credentials import AuthCredentials
from river_mwclient.gamepedia_client import GamepediaClient
from river_mwclient.errors import EsportsCacheKeyError

credentials = AuthCredentials(user_file='me')

site = EsportsClient('lol', credentials=credentials)

print(site.cache.get_team_from_event_tricode('Worlds 2019 Main Event', 'SKT'))

print(site.cache.get_disambiguated_player_from_event('Worlds 2019 Main Event', 'Splyce', 'Duke'))

try:
    print(site.cache.get('Team', 't1', 'not_a_real_length'))
except EsportsCacheKeyError as e:
    print(e)

site.client.pages['User:RheingoldRiver/login test'].save('ki3ttens 3')
