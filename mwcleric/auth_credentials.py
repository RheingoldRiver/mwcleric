import json
from os import path, getenv

from .errors import InvalidUserFile


class AuthCredentials(object):
    username = None
    password = None
    
    def __init__(self, username=None, password=None, user_file=None):
        """
        Stores username and password for future use with a WikiClient.
        Specify either user_file or both username and password.
        
        If using a file, files can be either located in the same directory as the code,
        or in the config directory of the user. If files in both locations exist,
        files in the former location will trump those in the latter.

        :param username: Username, this must include an @ if using a bot password
        :param password: Password, this is the actual value of the password, not the "name" of a "bot password"
        :param user_file: Either a file or a system variable as a nicknamed account to look for
        """
        if username and password:
            self.username = username
            self.password = password
        elif user_file:
            account_file = 'wiki_account_{}.json'.format(user_file.lower())
            if path.exists(account_file):
                user_info = self.read_user_info(account_file)
                self.password = user_info['password']
                self.username = user_info['username']
                if user_info.get('api_high_limits'):

                return
            pwd_path = path.join(path.expanduser('~'), '.config', 'mwcleric', pwd_file)
            usr_path = path.join(path.expanduser('~'), '.config', 'mwcleric', usr_file)
            if path.exists(pwd_path) and path.exists(usr_path):
                self.password = open(pwd_path).read().strip()
                self.username = open(usr_path).read().strip()
                return
            pwd_key = 'WIKI_PASSWORD_{}'.format(user_file.upper())
            usr_key = 'WIKI_USERNAME_{}'.format(user_file.upper())
            pwd = getenv(pwd_key, None)
            usr = getenv(usr_key, None)
            if not pwd or not usr:
                raise InvalidUserFile
            self.password = pwd
            self.username = usr

    @staticmethod
    def read_user_info(file):
        with open(file) as f:
            json_data = json.load(f)
            return json_data

    @staticmethod
    def prompt_user_info():
        print('We will prompt for 3 things: Username, bot pw name, bot token name. Whitespace will be stripped.')
        username = input('What is your username?')
        pw_name = input('What is your bot pw name?')
        pw_token = input('What is your bot pw token?')
        api_high_limits = input('Does this bot pw have api high limits? [Y/N] Press Enter if unsure or to make the software auto detect.')
        username = username.strip()
        password = '{}@{}'.format(pw_name.strip(), pw_token.strip())
        api_high_limits = api_high_limits.lower().strip()
        return username, password, api_high_limits
