River's tools for writing Python scripts for Leaguepedia / other Gamepedia esports wikis.

# Install/upgrade:
```
pip install -U git+git://github.com/RheingoldRiver/esportswiki_editing
```

# Logging in

The function `login` should be your single point of entry to create an `EsportsSite` object. This function expects the following files in **the same directory as your code**:
* `username.txt` - your user name (for the login `me`)
* `password.txt` - your bot password (for the login `me`)
* `username2.txt` - your bot's user name (for the login `bot`)
* `password2.txt` - your bot's bot password (for the login `bot`)

Logging in is necessary even if you are only making queries, if this is a problem open an issue and maybe I'll fix it so that's not required anymore.

## Bot password best practices
* Use a unique password just for your Python code that isn't also used for any other service
* In fact you should do this for every separate application that you use a bot password in