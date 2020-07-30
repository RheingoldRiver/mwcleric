from river_mwclient.esports_client import EsportsClient
from river_mwclient.auth_credentials import AuthCredentials
from river_mwclient.gamepedia_client import GamepediaClient
from river_mwclient.errors import EsportsCacheKeyError
from river_mwclient.wiki_time_parser import time_from_str

credentials = AuthCredentials(user_file='me')

site = EsportsClient('lol', credentials=credentials)

# check fallback to Teams.Short
assert site.cache.get_team_from_event_tricode('GUL 2020 Closing Playoffs', 'MK') == 'Mad Kings'

assert site.cache.get_team_from_event_tricode('Worlds 2019 Main Event', 'SKT') == 'SK Telecom T1'

assert site.cache.get_disambiguated_player_from_event(
    'Worlds 2019 Main Event', 'Splyce', 'Duke') == 'Duke (Hadrien Forestier)'

assert time_from_str("2020-03-27T16:49:18+00:00").dst == 'spring'

# check special character
assert site.cache.get_disambiguated_player_from_event(
    'Belgian League 2020 Summer', 'Aethra Esports', 'Tuomarí') == 'Tuomarí'

assert sum(1 for _ in site.data_pages('LDL 2020 Summer')) == 11
