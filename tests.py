from river_mwclient.esports_client import EsportsClient
from river_mwclient.auth_credentials import AuthCredentials
from river_mwclient.gamepedia_client import GamepediaClient

credentials = AuthCredentials(user_file='me')

site = GamepediaClient('lol', credentials=credentials)

site.client.pages['User:RheingoldRiver/login test'].save('ki3ttens 3')
