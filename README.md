## MediaWiki Client Library for Editing and Revision In Code (MW CLERIC)

River's tools for writing Python scripts for Leaguepedia / other Gamepedia esports wikis.

This library was originally known as `river_mwclient`, however I renamed it because it has grown beyond the scope of just being tools for myself into a full-fledged library with a lot of utilities that's useful for many people. Thanks to pcj for coming up with the exellent name.

# Install/upgrade:
This library can be installed from PyPI:
```
pip install mwcleric
```

However, for the most up-to-date version including minor changes for Leaguepedia-specific needs you may want to pull directly from the repo if I haven't updated on PyPI:
```
pip install -U git+git://github.com/RheingoldRiver/mwcleric
```

If you're using PyCharm, press alt+F12 to open the console and you can install directly to your venv or whatever it's using that way.

# Logging in

The function `login` should be your single point of entry to create an `EsportsSite` object. This function expects the following files in **the same directory as your code**:
* `username_me.txt` - your user name (for the login `me`) for example, `RheingoldRiver@Python`
* `password_me.txt` - your bot password (for the login `me`) this will be a long string of characters from Special:BotPasswords
* `username_bot.txt` - your bot's user name (for the login `bot`) for example, `RiverIsABot@Python`
* `password_bot.txt` - your bot's bot password (for the login `bot`)

> Note - you may not have two accounts! That's okay; in this case, just make `username_me` and `password_me`, and don't create the `bot` credential set.

These files would allow you to log in as `me` or as `bot`. Remember the username includes both your account name **and also the name of your bot password**, separated by an `@`.

If you prefer, you can set environment variables called `WIKI_USERNAME_ME`, `WIKI_PASSWORD_ME`, etc. 

If you don't want to log in, you can just create an EsportsSite/GamepediaSite object and never log in.

## Bot password best practices
* Use a unique password just for your Python code that isn't also used for any other service
* In fact you should do this for every separate application that you use a bot password in

# Editing
For people wanting to edit wikis, `PageModifier` and `TemplateModifier` are the two things most likely to make your life easier. To use them you subclass and then overwrite methods to modify the page or template as needed, then instantiate the subclass and run. 

For `PageModifier`, you probably want *either* `updage_plaintext` *or* `update_wikitext`, not both.
## Copyable code 
```python
from mwcleric.esports_client import EsportsClient
from mwcleric.auth_credentials import AuthCredentials
from mwcleric.template_modifier import TemplateModifierBase

credentials = AuthCredentials(user_file="me")
site = EsportsClient('lol', credentials=credentials)
summary = 'Bot edit'


class TemplateModifier(TemplateModifierBase):
	def update_template(self, template):
		return


TemplateModifier(site, 'TEMPLATEYOUCAREABOUT',
				 summary=summary).run()
```

```python
from mwcleric.esports_client import EsportsClient
from mwcleric.auth_credentials import AuthCredentials
from mwcleric.page_modifier import PageModifierBase

credentials = AuthCredentials(user_file="me")
site = EsportsClient('lol', credentials=credentials)
summary = 'Bot edit'


class PageModifier(PageModifierBase):
	def update_plaintext(self, text):
		return text
	
	def update_wikitext(self, wikitext):
		return


PageModifier(site,
				 summary=summary).run()
```

# Contributing
If you want to contribute feel free to open a pull request, as long as whatever you add works, the only way I wouldn't accept is if it actively interferes with my existing code (but that does include being poorly organized etc so pls actually make it a nice change).
