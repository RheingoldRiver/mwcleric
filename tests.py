from river_mwclient.esports_client import EsportsClient
from river_mwclient.auth_credentials import AuthCredentials

credentials = AuthCredentials(user_file='me')

site = EsportsClient('lol', credentials=credentials)

site.client.pages['User:RheingoldRiver/login test'].save('kittens')
