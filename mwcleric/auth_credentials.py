import json
import os

from .errors import InvalidUserFile


class AuthCredentials(object):
    file_pattern = 'wiki_account_{}.json'
    username = None
    password = None
    site_user = None
    site_pw = None
    config_path = os.path.join(os.path.expanduser('~'), '.config', 'mwcleric')

    def __init__(self, username=None, password=None, user_file=None, start_over=False):
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

        if start_over:
            if user_file is None:
                raise ValueError('No user_file is defined.')
            start_over_confirm = input('Are you sure you want to overwrite your previous credentials? [Y]es or [N]o ')
            if start_over_confirm.lower()[0] == 'y':
                account_data = self.prompt_user_info()
                self.save_account_data(account_data, user_file)
            else:
                # Proceeding with existing login credentials.
                pass

        if username and password:
            self.username = username
            self.password = password
        elif user_file:
            # Environment Variables Method
            pw = os.getenv('WIKI_PASSWORD_{}'.format(user_file.upper()), None)
            usr = os.getenv('WIKI_USERNAME_{}'.format(user_file.upper()), None)
            site_pw = os.getenv('WIKI_SITE_PASSWORD_{}'.format(user_file.upper()), None)
            site_usr = os.getenv('WIKI_SITE_USERNAME_{}'.format(user_file.upper()), None)
            if pw and usr:
                self.password = pw
                self.username = usr
                self.site_pw = site_pw
                self.site_user = site_usr
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
            self.site_pw = user_info.get('site_pw', '')
            self.site_user = user_info.get('site_user', '')

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
        extra_info_text = (
            f"\n\n We will also ask for the credentials required to view the wiki (separate from your personal account info). "
            f"If such credentials don't exist or you need to start over at any time, press Ctrl+C.")
        print(
            f'For your user account, we will prompt for 3 separate things: '
            f'Username, bot pw name, bot token name. '
            f'Whitespace will be stripped.')
        username = input('What is your USERNAME (not bot password yet)?')
        pw_name = input('What is your bot pw NAME (not token yet)?')
        pw_token = input('What is your bot pw token/secret?')
        should_prompt_next = input('Is this wiki locked behind a password? [Y]es or [N]o')
        site_user = ''
        site_pw = ''
        if should_prompt_next[0].lower() == 'y':
            site_user = input('What is the HTTP authentication USERNAME (credentials required to view the wiki)?')
            site_pw = input('WWhat is the HTTP authentication PASSWORD (credentials required to view the wiki)?')
        password = '{}@{}'.format(pw_name.strip(), pw_token.strip())
        account_data = {
            'username': username.strip(),
            'password': password.strip(),
            'site_user': site_user.strip(),
            'site_pw': site_pw.strip(),
        }
        return account_data

    @property
    def site_password_prefix(self):
        if self.site_pw == '':
            return ''
        return f'{self.site_user}:{self.site_pw}@'
