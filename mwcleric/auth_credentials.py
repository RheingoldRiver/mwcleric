import json
import os

from .errors import InvalidUserFile


class AuthCredentials(object):
    file_pattern = 'wiki_account_{}.json'
    username = None
    password = None
    config_path = os.path.join(os.path.expanduser('~'), '.config', 'mwcleric')

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
            # Environment Variables Method
            pw = os.getenv('WIKI_PASSWORD_{}'.format(user_file.upper()), None)
            usr = os.getenv('WIKI_USERNAME_{}'.format(user_file.upper()), None)
            lmt = os.getenv('WIKI_APILIMIT_{}'.format(user_file.upper()), None)
            if pw and usr:
                self.password = pw
                self.username = usr
                self.api_high_limits = lmt
                return

            # Files / User Input Method
            user_info = self.get_user_data_from_file(user_file, '')
            if not user_info:
                user_info = self.get_user_data_from_file(user_file, self.config_path)
            if not user_info:
                account_data = self.prompt_user_info()
                self.save_account_data(account_data, user_file)
                user_info = self.get_user_data_from_file(user_file, self.config_path)
            if not user_info:
                raise InvalidUserFile
            self.password = user_info['password']
            self.username = user_info['username']
            if user_info.get('api_high_limits'):
                if user_info['api_high_limits'].lower()[0] == 'y':
                    self.api_high_limits = True
                else:
                    self.api_high_limits = False
            else:
                self.api_high_limits = None

    def get_user_data_from_file(self, user_file, base_path):
        account_file = os.path.join(base_path, self.file_pattern.format(user_file.lower()))
        legacy_user_file = os.path.join(base_path, 'username_{}.txt'.format(user_file.lower()))
        legacy_pw_file = os.path.join(base_path, 'password_{}.txt'.format(user_file.lower()))
        if os.path.exists(account_file):
            return self.read_user_info(account_file)
        elif os.path.exists(legacy_user_file) and os.path.exists(legacy_pw_file):
            self.update_legacy_user_info(legacy_user_file, legacy_pw_file, account_file)
            return self.read_user_info(account_file)
        else:
            return None

    @staticmethod
    def read_user_info(file):
        with open(file) as f:
            json_data = json.load(f)
        return json_data

    @staticmethod
    def update_legacy_user_info(legacy_user_file, legacy_pw_file, account_file):
        with open(legacy_user_file, 'r') as f:
            username = f.read().strip()
        with open(legacy_pw_file, 'r') as f:
            password = f.read().strip()
        account_data = {
            'username': username,
            'password': password
        }
        with open(account_file, 'w') as f:
            f.write(json.dumps(account_data, indent=4))

    def save_account_data(self, account_data, user_file):
        os.makedirs(self.config_path, exist_ok=True)
        with open(os.path.join(self.config_path,
                               self.file_pattern.format(user_file.lower())), 'w') as f:
            f.write(json.dumps(account_data, indent=4))

    @staticmethod
    def prompt_user_info():
        print(
            'We will prompt for 3 separate things: Username, bot pw name, bot token name. Whitespace will be stripped.')
        username = input('What is your USERNAME (not bot password yet)?')
        pw_name = input('What is your bot pw NAME (not token yet)?')
        pw_token = input('What is your bot pw token/secret?')
        api_high_limits = input(
            'Does this bot pw have api high limits? [Y/N] Press Enter if unsure or to make the software auto detect.').strip()
        username = username.strip()
        password = '{}@{}'.format(pw_name.strip(), pw_token.strip())
        api_high_limits = api_high_limits.lower().strip()
        account_data = {
            'username': username,
            'password': password,
            'api_high_limits': api_high_limits
        }
        return account_data
