class AuthCredentials(object):
    username = None
    password = None

    def __init__(self, username=None, password=None, user_file=None):
        if username and password:
            self.username = username
            self.password = password
        elif user_file:
            pwd_file = 'password2.txt' if user_file == 'bot' else 'password.txt'
            user_file = 'username2.txt' if user_file == 'bot' else 'username.txt'
            self.password = open(pwd_file).read().strip()
            self.username = open(user_file).read().strip()
