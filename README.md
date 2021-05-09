# MediaWiki Client Library for Editing and Revision In Code (MW CLERIC)

River's tools for writing Python scripts for MediaWiki wikis, including the Fandom wiki farm.

This library was originally known as `river_mwclient`, however I renamed it because it has grown beyond the scope of just being tools for myself into a full-fledged library with a lot of utilities that's useful for many people. Thanks to pcj for coming up with the excellent name.

## Install/upgrade:
This library can be installed from PyPI:
```
pip install mwcleric
```

However, for the most up-to-date version including minor changes you may want to pull directly from the repo if I haven't updated PyPI:
```
pip install -U git+git://github.com/RheingoldRiver/mwcleric
```

If you're using PyCharm, press Alt+F12 to open the console and you can install directly to your venv or whatever it's using that way.

## Logging in

Currently, bot passwords are supported; legacy login without bot passwords should also work. If you want to add support for another type of login, I'm happy to merge a PR for it.

If you don't want to log in, you can just create a `WikiClient` / `FandomClient` object and never log in; this is fine if you just want to make Cargo queries etc. However, if you want to edit your wiki, you probably will want to log in.

You can specify a username & password directly in the `AuthCredentials` constructor, or you can set the name of a `user_file`. This user_file will be used as a key to look up either environment variables or a file. If the file doesn't exist, you will be prompted to enter your information.

**TL;DR: you can do nothing and just be prompted to enter your information.**

### Environment variables method

If you're editing via crontab or setting up a Discord bot etc, dealing with files can suck, so you can set up environment variables. These are expected to be:

* `WIKI_USERNAME_%s`
* `WIKI_PASSWORD_%s`

If you use bot passwords, the password should be formatted like `RheingoldRiver@Python`; your username then `@` then the name of your bot password. The password is just your bot password secret.

### Files / interactive method
The interactive method prompts you to enter your username in two parts, first the wiki username, then the bot password name; as well as the bot password secret, and then creates the user file json.

The location of this file is:

```python
os.path.join(os.path.expanduser('~'), '.config', 'mwcleric')
```

If you want, you can also create a json manually in the same directory as your code, which will overwrite your `.config` location json. The format of any json is:

```json
{
    "username": "@",
    "password": "",
}
```
Fill in the blanks with your info.

### Bot password information & best practices
River wrote an entire blog post about this! See https://river.me/blog/bot-passwords/ for more information.

## Editing
For people wanting to edit wikis, `PageModifier` and `TemplateModifier` are the two things most likely to make your life easier. To use them, you subclass and then overwrite methods to modify the page or template as needed, then instantiate the subclass and run. 

For `PageModifier`, you probably want *either* `update_plaintext` *or* `update_wikitext`, not both.
### Copyable code 
```python
from mwcleric.wiki_client import WikiClient
from mwcleric.auth_credentials import AuthCredentials
from mwcleric.template_modifier import TemplateModifierBase
from mwparserfromhell.nodes import Template

credentials = AuthCredentials(user_file="me")
site = WikiClient(site='lol.fandom.com', credentials=credentials)
summary = 'Bot edit'


class TemplateModifier(TemplateModifierBase):
	def update_template(self, template: Template):
		return


TemplateModifier(site, 'TEMPLATEYOUCAREABOUT',
                 summary=summary).run()

```

```python
from mwcleric.wiki_client import WikiClient
from mwcleric.auth_credentials import AuthCredentials
from mwcleric.page_modifier import PageModifierBase

credentials = AuthCredentials(user_file="me")
site = WikiClient(site='lol.fandom.com', credentials=credentials)
summary = 'Bot edit'


class PageModifier(PageModifierBase):
    def update_plaintext(self, text):
        return text

    def update_wikitext(self, wikitext):
        return


PageModifier(site,
             summary=summary).run()
```

## Contributing
PRs are welcome! So far this repo is mostly Fandom-wiki-centric but it definitely doesn't have to stay that way; though contributions to `FandomClient` are also appreciated. Help with documentation & tests is also welcome!
