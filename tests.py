from river_mwclient.esports_client import EsportsClient
from river_mwclient.auth_credentials import AuthCredentials
from river_mwclient.gamepedia_client import GamepediaClient
from river_mwclient.errors import EsportsCacheKeyError

credentials = AuthCredentials(user_file='me')

site = EsportsClient('lol', credentials=credentials)

print(site.cache.get('Champion', 'lee', 'link'))

try:
    print(site.cache.get('Champion', 'lee', 'long'))
except EsportsCacheKeyError as e:
    print(e)

site.client.pages['User:RheingoldRiver/login test'].save('ki3ttens 3')
