River's tools for writing Python scripts for Leaguepedia / other Gamepedia esports wikis.

This library is basically an `mwclient` (https://github.com/mwclient/mwclient) wrapper, it has some built-in error handling for you, some Cargo support, and most importantly decreases the number of lines of code needed to create and log into a site object from like 3 to 1. It's intended for my wikis primarily but feel free to clone/use.

# Install/upgrade:
```
pip install -U git+git://github.com/RheingoldRiver/river_mwclient
```

You probably also want development version of `mwclient`:
```
pip install -U git+git://github.com/mwclient/mwclient.git
```
This adds a patch I made to add methods `page.touch`, `page.append`, and `page.prepend`. If those are already in the most recent published version, tell me and I'll delete this instruction.

If you're using PyCharm, press alt+F12 to open the console and you can install directly to your venv or whatever it's using that way.

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

# Contributing
If you want to contribute feel free to open a pull request, as long as whatever you add works, the only way I wouldn't accept is if it actively interferes with my existing code (but that does include being poorly organized etc so pls actually make it a nice change).
